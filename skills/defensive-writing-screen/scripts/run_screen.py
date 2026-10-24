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
import multiprocessing as mp
import os
import sys
import time
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
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
                json.JSONDecodeError, OSError) as exc:
            last = f"{type(exc).__name__}: {exc}"
            if attempt < retries:
                time.sleep(0.5 * (2 ** attempt))
    return None, None, retries + 1, last


def state_for(text: str, location: str = "", context: str = "") -> dict:
    state = {"paragraph": {"text": text, "location": location or "draft"},
             "genre": GENRE,
             "rules": RULES}
    state["context"] = context or "Only facts stated in this paragraph are supplied."
    return state


def build_row(item, probs, resolved, attempts, error, questions, label):
    unit_id = item.get("id") or item.get("request_id")
    row = {"id": unit_id, "kind": label, "ok": probs is not None,
           "attempts": attempts, "resolved_model": resolved, "error": error}
    if probs is None:
        row.update({name: None for name in questions})
        row["triage"] = None
        row["triage_dim"] = None
        return row
    row.update(probs)
    active = [(name, probs.get(name)) for name in questions if probs.get(name) is not None]
    if active:
        dim, score = max(active, key=lambda pair: pair[1])
        row["triage_dim"], row["triage"] = dim, score
    else:
        row["triage_dim"] = row["triage"] = None
    return row


def worker(job):
    """Runs inside a pool process: one unit, claimed when the process is free."""
    item, base, questions, timeout, model, retries, label = job
    payload = {"state": item["state"], "questions": questions}
    try:
        probs, resolved, attempts, error = call(base, payload, timeout, model, retries)
    except Exception as exc:  # a worker must never take the run down
        probs, resolved, attempts, error = None, None, 0, f"{type(exc).__name__}: {exc}"
    return build_row(item, probs, resolved, attempts, error, questions, label)


def run(items, base, questions, timeout, model, workers, label, executor="process",
        retries=1, out_path=None):
    """Claim units from a shared queue and stream each finished row to disk.

    Process mode isolates a crash to one unit and lets workers claim work as they
    finish instead of receiving a fixed slice. Thread mode stays available for
    platforms where forking is unavailable.
    """
    jobs = [(item, base, questions, timeout, model, retries, label) for item in items]
    results = []
    handle = out_path.open("a", encoding="utf-8") if out_path else None
    try:
        if executor == "thread":
            iterator = _thread_iter(jobs, workers)
        else:
            pool = mp.Pool(processes=workers, maxtasksperchild=25)
            iterator = pool.imap_unordered(worker, jobs, chunksize=1)
        try:
            for row in iterator:
                results.append(row)
                line = json.dumps(row, ensure_ascii=False)
                print(line, flush=True)
                if handle:
                    handle.write(line + "\n")
                    handle.flush()
                    os.fsync(handle.fileno())
        finally:
            if executor != "thread":
                pool.close()
                pool.join()
    finally:
        if handle:
            handle.close()
    return results


def _thread_iter(jobs, workers):
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(worker, job) for job in jobs]
        for future in futures:
            yield future.result()


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
    parser.add_argument("mode", choices=("gate", "triage", "focused", "summarize"))
    parser.add_argument("--units", type=Path)
    parser.add_argument("--spans", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--base", default=os.environ.get("PI_JEV_BASE_URL", DEFAULT_BASE))
    parser.add_argument("--model", default=os.environ.get("JEV_MODEL") or None)
    parser.add_argument("--workers", default=os.environ.get("JEV_CONCURRENCY", "4"),
                        help="pool size, or auto to use the widest safe fan-out (units are independent)")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--retries", type=int, default=1, help="transport retries per unit")
    parser.add_argument("--executor", choices=("process", "thread"), default="process",
                        help="process pool claims units dynamically; thread mode for no-fork platforms")
    parser.add_argument("--context", default="", help="shared context for triage units")
    parser.add_argument("--screen", type=Path, help="summarize: triage output to read")
    parser.add_argument("--threshold", type=float, default=0.65, help="summarize: routing threshold")
    parser.add_argument("--sample", type=int, default=0,
                        help="summarize: also hand over N evenly spaced non-routed units for miss checking")
    parser.add_argument("--chars", type=int, default=1200, help="summarize: per-unit text limit")
    parser.add_argument("--resume", action="store_true",
                        help="keep succeeded rows from --out and retry only missing or failed ids")
    args = parser.parse_args(argv)

    controls = load_controls()
    questions = controls["questions"]

    if args.mode == "summarize":
        if not args.screen:
            raise SystemExit("summarize needs --screen")
        rows = read_jsonl(args.screen)
        texts = {}
        if args.units and args.units.is_file():
            texts = {unit["id"]: unit for unit in read_jsonl(args.units)}
        routed = [r for r in rows if r.get("ok") and (r.get("triage") or 0) >= args.threshold]
        routed.sort(key=lambda r: -(r.get("triage") or 0))
        failed = [r["id"] for r in rows if not r.get("ok")]
        unread = [r["id"] for r in rows if not r.get("ok") or (r.get("triage") or 0) < args.threshold]
        out = [f"# High-risk units at threshold {args.threshold}", "",
               f"- units: {len(rows)}; routed: {len(routed)}; below threshold: {len(rows) - len(routed) - len(failed)}; failed: {len(failed)}",
               f"- resolved model: {next((r['resolved_model'] for r in rows if r.get('resolved_model')), None)}",
               f"- failed ids: {', '.join(failed) if failed else 'none'}", ""]
        if len(out) < 8 and not routed:
            out.append("No unit reached the threshold. That is not a clean bill of health: below-threshold units stay unread.")
        for row in routed:
            unit = texts.get(row["id"], {})
            scores = ", ".join(f"{name}={row.get(name):.3f}" for name in questions
                               if isinstance(row.get(name), (int, float)))
            text = " ".join((unit.get("text") or "").split())
            if args.chars and len(text) > args.chars:
                text = text[: args.chars] + " ..."
            out.append(f"## {row['id']} | lines {unit.get('start', '?')}-{unit.get('end', '?')} | "
                       f"max {row.get('triage_dim')} {row.get('triage'):.3f}")
            out.append(f"{scores}")
            out.append("")
            out.append(text)
            out.append("")
        if args.sample:
            pool = [u for u in texts.values() if u["id"] in set(unread)]
            step = max(1, len(pool) // args.sample) if pool else 1
            picked = pool[::step][: args.sample]
            out.append(f"# Miss-check sample ({len(picked)} of {len(pool)} non-routed units)")
            out.append("")
            for unit in picked:
                text = " ".join((unit.get("text") or "").split())
                if args.chars and len(text) > args.chars:
                    text = text[: args.chars] + " ..."
                out.append(f"## {unit['id']} | lines {unit.get('start')}-{unit.get('end')}")
                out.append("")
                out.append(text)
                out.append("")
        args.out.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
        print(f"summarize: {len(routed)} routed handed over; {len(failed)} failed; {args.sample} sampled",
              file=sys.stderr)
        return 0

    workers = args.workers
    if str(workers).strip().lower() == "auto":
        workers = int(os.environ.get("JEV_AUTO_WORKERS", "8"))
    workers = max(1, min(int(workers), 32))

    if args.mode == "gate":
        items = [{"id": row["id"], "state": state_for(row["text"], "control battery")}
                 for row in controls["controls"]]
        results = run(items, args.base, questions, args.timeout, args.model,
                      min(workers, len(items)), "gate", args.executor, args.retries)
        thresholds = controls["thresholds"]
        failures = []
        # Pool results arrive in completion order: match by id, never by position.
        by_id = {row["id"]: row for row in results}
        missing = [spec["id"] for spec in controls["controls"] if spec["id"] not in by_id]
        if missing:
            failures.append(f"missing control rows: {missing}")
        for spec in controls["controls"]:
            row = by_id.get(spec["id"])
            if row is None:
                continue
            if not row["ok"]:
                failures.append(f"{row['id']}: call failed ({row['error']})")
                continue
            if spec["designated_dimension"] == "all":
                scores = [row[name] for name in questions if row.get(name) is not None]
                if any(score > thresholds["negative_max"] for score in scores):
                    failures.append(f"{row['id']}: neutral control above {thresholds['negative_max']}")
            elif (row.get(spec["designated_dimension"]) or 0) < thresholds["positive_min"]:
                failures.append(f"{row['id']}: {spec['designated_dimension']} below {thresholds['positive_min']}")
        ordered = [by_id[spec["id"]] for spec in controls["controls"] if spec["id"] in by_id]
        args.out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in ordered) + "\n",
                            encoding="utf-8")
        resolved = next((r["resolved_model"] for r in ordered if r["resolved_model"]), None)
        print(f"gate: {len(ordered) - len(failures)}/{len(controls['controls'])} passed; workers {workers}; "
              f"resolved model: {resolved}", file=sys.stderr)
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
        results = kept + run(items, args.base, questions, args.timeout, args.model,
                             min(workers, max(1, len(items))), "triage",
                             args.executor, args.retries, None if kept else args.out)
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
        results = kept + run(items, args.base, payload_questions, args.timeout, args.model,
                             min(workers, max(1, len(items))), "focused", args.executor, args.retries,
                             None if kept else args.out)

    args.out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in results) + "\n",
                        encoding="utf-8")
    ok = sum(1 for r in results if r["ok"])
    failed = [r["id"] for r in results if not r["ok"]]
    resolved = next((r["resolved_model"] for r in results if r["resolved_model"]), None)
    retried = sum(1 for r in results if r.get("attempts", 1) > 1)
    print(f"{args.mode}: {ok}/{len(results)} ok; workers {workers}; retried {retried}; "
          f"resolved model: {resolved}; failures: {failed or 'none'}", file=sys.stderr)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
