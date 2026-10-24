#!/usr/bin/env python3
"""Run the Jev screen from a script instead of per-unit agent tool calls.

One process, concurrency four by default, retries on transport errors, null on
persistent failure, and resumable output. The agent reads the aggregate result
instead of carrying every raw response through its context.

Usage:
    # 1. split the draft
    python3 prepare_units.py draft.tex --candidates > units.jsonl

    # 2. control gate (blocks the document run when it fails)
    python3 run_screen.py gate --out gate.jsonl

    # 3. document triage
    python3 run_screen.py triage --units units.jsonl --out screen.jsonl

    # 4. focused deletion check for selected spans
    python3 run_screen.py focused --spans spans.jsonl --out focused.jsonl

Environment:
    PI_JEV_BASE_URL   base URL of the System One endpoint (default http://localhost:8090)
    JEV_MODEL         optional model field sent with each request
    JEV_CONCURRENCY   optional worker count (default 4)

Input shapes:
    units.jsonl   {"id","start","end","text"} from prepare_units.py
    spans.jsonl   {"id","text","span","evidence"}

Output: one JSON object per line with the unit id, the four probabilities, the
triage maximum, the resolved model reported by the service, and raw nulls for
failed calls. Nothing is imputed.

Exit codes: 0 ok, 2 gate failed, 1 malformed input or unreachable service.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTROLS = HERE.parent / "references" / "controls.json"

DEFAULT_BASE = "http://localhost:8090"
GENRE = "academic paper, English"
RULES = ("Preserve facts, metric direction, mathematical conditions, "
         "intervention scope, and necessary uncertainty.")


def load_controls() -> dict:
    return json.loads(CONTROLS.read_text(encoding="utf-8"))


def post(base: str, payload: dict, timeout: float, model: str | None) -> dict:
    body = dict(payload)
    if model:
        body["model"] = model
    request = urllib.request.Request(
        base.rstrip("/") + "/v1/systemone",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def values(answers: dict) -> dict[str, float | None]:
    out: dict[str, float | None] = {}
    for name, answer in answers.items():
        if isinstance(answer, dict):
            out[name] = answer.get("noul", answer.get("value"))
        else:
            out[name] = None
    return out


def call(base, payload, timeout, model, retries=1):
    """Return (values, resolved_model, attempts, error). Retries transport errors only."""
    last = ""
    for attempt in range(retries + 1):
        try:
            response = post(base, payload, timeout, model)
            answers = response.get("answers") or response
            return values(answers), response.get("model"), attempt + 1, None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            last = f"{type(exc).__name__}: {exc}"
    return None, None, retries + 1, last


def state_for(text: str, location: str = "", context: str = "") -> dict:
    state = {"paragraph": {"text": text, "location": location or "draft"},
             "genre": GENRE,
             "rules": RULES}
    state["context"] = context or "Only facts stated in this paragraph are supplied."
    return state


def run(items, base, questions, timeout, model, workers, label):
    results = []

    def one(item):
        unit_id = item.get("id") or item.get("request_id")
        payload = {"state": item["state"], "questions": questions}
        probs, resolved, attempts, error = call(base, payload, timeout, model)
        row = {"id": unit_id, "kind": label, "ok": probs is not None,
               "attempts": attempts, "resolved_model": resolved, "error": error}
        if probs is None:
            row.update({name: None for name in questions})
            row["triage"] = None
            row["triage_dim"] = None
        else:
            row.update(probs)
            active = [(name, probs.get(name)) for name in questions if probs.get(name) is not None]
            if active:
                dim, score = max(active, key=lambda pair: pair[1])
                row["triage_dim"], row["triage"] = dim, score
            else:
                row["triage_dim"] = row["triage"] = None
        return row

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for row in pool.map(one, items):
            results.append(row)
            print(json.dumps(row, ensure_ascii=False), flush=True)
    return results


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{number}: {exc}") from exc
    return rows


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=("gate", "triage", "focused"))
    parser.add_argument("--units", type=Path)
    parser.add_argument("--spans", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--base", default=os.environ.get("PI_JEV_BASE_URL", DEFAULT_BASE))
    parser.add_argument("--model", default=os.environ.get("JEV_MODEL") or None)
    parser.add_argument("--workers", type=int, default=int(os.environ.get("JEV_CONCURRENCY", "4")))
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--context", default="", help="shared context for triage units")
    parser.add_argument("--resume", action="store_true",
                        help="keep succeeded rows from --out and retry only missing or failed ids")
    args = parser.parse_args(argv)

    controls = load_controls()
    questions = controls["questions"]

    if args.mode == "gate":
        items = [{"id": row["id"], "state": state_for(row["text"], "control battery")}
                 for row in controls["controls"]]
        results = run(items, args.base, questions, args.timeout, args.model, args.workers, "gate")
        thresholds = controls["thresholds"]
        failures = []
        for row, spec in zip(results, controls["controls"]):
            if not row["ok"]:
                failures.append(f"{row['id']}: call failed ({row['error']})")
                continue
            if spec["designated_dimension"] == "all":
                scores = [row[name] for name in questions if row.get(name) is not None]
                if any(score > thresholds["negative_max"] for score in scores):
                    failures.append(f"{row['id']}: neutral control above {thresholds['negative_max']}")
            elif (row.get(spec["designated_dimension"]) or 0) < thresholds["positive_min"]:
                failures.append(f"{row['id']}: {spec['designated_dimension']} below {thresholds['positive_min']}")
        args.out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in results) + "\n",
                            encoding="utf-8")
        resolved = next((r["resolved_model"] for r in results if r["resolved_model"]), None)
        print(f"gate: {len(results) - len(failures)}/{len(results)} passed; resolved model: {resolved}",
              file=sys.stderr)
        for failure in failures:
            print(f"  FAIL {failure}", file=sys.stderr)
        return 0 if not failures else 2

    kept: list[dict] = []
    if args.resume and args.out.is_file():
        for row in read_jsonl(args.out):
            if row.get("ok"):
                kept.append(row)
    keep_ids = {row["id"] for row in kept}

    if args.mode == "triage":
        if not args.units:
            raise SystemExit("triage needs --units")
        items = []
        for unit in read_jsonl(args.units):
            if unit["id"] in keep_ids:
                continue
            items.append({"id": unit["id"],
                          "state": state_for(unit["text"],
                                             f"lines {unit.get('start')}-{unit.get('end')}",
                                             args.context)})
        results = kept + run(items, args.base, questions, args.timeout, args.model, args.workers, "triage")
    else:
        if not args.spans:
            raise SystemExit("focused needs --spans")
        payload_questions = {
            "removal_preserves": {
                "type": "noul",
                "instructions": "If `span` is removed from `text`, does the remaining text still accurately convey all facts and necessary restrictions in `evidence`?",
                "criteria": {"true": "Removal preserves every known fact, scope condition, and methodological limit in evidence",
                             "false": "Removal loses a fact, scope condition, methodological limit, safety rule, or operational requirement"},
            }
        }
        items = [{"id": span["id"],
                  "state": {"text": span["text"], "span": span["span"],
                            "evidence": span.get("evidence") or "unknown"}}
                 for span in read_jsonl(args.spans) if span["id"] not in keep_ids]
        results = kept + run(items, args.base, payload_questions, args.timeout, args.model, args.workers, "focused")

    args.out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in results) + "\n",
                        encoding="utf-8")
    ok = sum(1 for r in results if r["ok"])
    failed = [r["id"] for r in results if not r["ok"]]
    resolved = next((r["resolved_model"] for r in results if r["resolved_model"]), None)
    print(f"{args.mode}: {ok}/{len(results)} ok; resolved model: {resolved}; failures: {failed or 'none'}",
          file=sys.stderr)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
