#!/usr/bin/env python3
"""Split Markdown, plain text, or conservative LaTeX into screening units.

Emits one JSON object per prose paragraph: stable id, line range, verbatim
text, and optional defensive-phrase candidate spans. No network, no
dependencies, no writes.

Usage:
    python3 prepare_units.py draft.md > units.jsonl
    python3 prepare_units.py draft.md --max-units 40
    python3 prepare_units.py draft.md --candidates
    cat draft.md | python3 prepare_units.py - --candidates

Output fields:
    id          <slug>_p<N>, stable for the same input and options
    start,end   1-based line range
    paragraph   paragraph index within the emitted set
    text        verbatim paragraph text, blank lines collapsed to one space
    candidates  exact substrings that may deserve a focused Jev question

Candidates are retrieval hints only. A paragraph without a candidate span is
still screened; absence of a phrase proves nothing.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Phrases that commonly mark defensive or self-undermining phrasing.
# They are retrieval hints, not verdicts. Extend per language and genre.
PATTERNS_ZH = [
    r"仅仅[^。；，]{0,20}",
    r"只是[^。；，]{0,20}初步[^。；，]{0,20}",
    r"只能提供[^。；，]{0,12}",
    r"尚不能[^。；，]{0,20}",
    r"仍有[^。；，]{0,12}提升空间",
    r"并不声称[^。；，]{0,30}",
    r"无意[^。；，]{0,20}",
    r"不意味着[^。；，]{0,30}",
    r"不应被理解为[^。；，]{0,30}",
    r"值得注意的是[^。；，]{0,20}",
    r"需要澄清的是[^。；，]{0,20}",
    r"并非[^。；，]{0,20}而是[^。；，]{0,20}",
    r"很难[^。；，]{0,20}",
    r"几乎无法[^。；，]{0,20}",
    r"仅[^。；，]{0,12}",
    r"只能[^。；，]{0,16}",
    r"难以[^。；，]{0,16}",
    r"尚未[^。；，]{0,16}",
    r"若仅[^。；，]{0,20}",
    r"仍然?[^。；，]{0,10}(?:差距|不足|落后|有限|需要|尚)",
]
PATTERNS_EN = [
    r"\bnot claim[^.;]{0,40}",
    r"\bdo(?:es)? not attempt to[^.;]{0,40}",
    r"\brather than[^.;]{0,30}",
    r"\bshould not be (?:taken|read|understood)[^.;]{0,30}",
    r"\bgoal is not[^.;]{0,30}",
    r"\bto be clear\b",
    r"\bit (?:is|should be) worth noting\b",
    r"\bof course,[^.;]{0,40}",
    r"\bonly a preliminary[^.;]{0,30}",
    r"\bmay potentially[^.;]{0,40}",
    r"\bcould possibly[^.;]{0,40}",
    r"\b(?:do|does|did) not (?:claim|attempt|provide|include|prove|address|cover)\b[^.;]{0,40}",
    r"\bnot (?:intended|meant|designed) to\b[^.;]{0,40}",
    r"\binstead of\b[^.;]{0,30}",
    r"\bas opposed to\b[^.;]{0,30}",
    r"\bcould hardly\b",
    r"\bto some extent\b",
    r"\bnot necessarily\b",
    r"\bnot by themselves\b",
]

SKIP_PREFIXES = ("```", "~~~", "|", "![", "<img", "<table", "$$", "\\[", "\\begin{", "%")
HEADING = re.compile(r"^#{1,6}\s")
FOOTNOTE_DEF = re.compile(r"^\[\^[^\]]+\]:")


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._")
    return cleaned or "draft"


def normalize(block: str) -> str:
    return re.sub(r"\s*\n\s*", " ", block).strip()


def is_prose(block: str, min_chars: int) -> bool:
    stripped = block.lstrip()
    if HEADING.match(stripped) or FOOTNOTE_DEF.match(stripped):
        return False
    if stripped.startswith(SKIP_PREFIXES):
        return False
    if re.fullmatch(r"[-*_=\s]{3,}", stripped):
        return False
    has_letters = re.search(r"[\w\u4e00-\u9fff]", stripped) is not None
    return has_letters and len(stripped) >= min_chars


def iter_blocks(text: str):
    """Yield (start_line, end_line, block), splitting on blank lines outside fences."""
    in_fence = False
    start = None
    buf: list[str] = []
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            if start is None:
                start = number
            buf.append(line)
            continue
        if in_fence:
            buf.append(line)
            continue
        if not stripped:
            if buf:
                yield start, number - 1, "\n".join(buf)
            start, buf = None, []
            continue
        if start is None:
            start = number
        buf.append(line)
    if buf:
        yield start, number, "\n".join(buf)


def find_candidates(text: str) -> list[str]:
    found: list[str] = []
    for pattern in PATTERNS_ZH + PATTERNS_EN:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            span = match.group(0).strip(" \t，,。；;：:")
            # Trim only a regex match ending inside a source word, not a complete
            # fixed phrase such as "not by themselves".
            if (match.end() < len(text) and text[match.end()].isalnum()
                    and match.group(0)[-1].isalnum() and " " in span):
                span = span.rsplit(" ", 1)[0]
            if len(span) >= 2 and span not in found:
                found.append(span)
    return found


def latex_blocks(text: str):
    """Conservative extraction; preserve line positions, not TeX execution.

    No macro expansion or input-file loading. Mask non-prose while retaining
    newlines. Inline math/citations remain in prose. source_text in the output
    supplies the unchanged source range when wrappers are stripped.
    """
    def blank(match):
        return re.sub(r"[^\n]", " ", match.group(0))

    body = text
    document = re.search(r"\\begin\{document\}", body)
    if document:
        body = re.sub(r"[^\n]", " ", body[:document.end()]) + body[document.end():]
    # A percent escaped by an odd number of backslashes is a literal percent.
    lines = []
    for line in body.splitlines(keepends=True):
        for i, char in enumerate(line):
            if char != "%":
                continue
            backslashes = len(line[:i]) - len(line[:i].rstrip("\\"))
            if backslashes % 2 == 0:
                line = line[:i] + re.sub(r"[^\n]", " ", line[i:])
                break
        lines.append(line)
    body = "".join(lines)
    skipped = r"equation\*?|align\*?|alignat\*?|gather\*?|multline\*?|displaymath|math|tabular\*?|tabularx|longtable|thebibliography|verbatim\*?|lstlisting|tikzpicture"
    body = re.sub(r"\\begin\{(" + skipped + r")\}[\s\S]*?\\end\{\1\}", blank, body)
    body = re.sub(r"\\\[[\s\S]*?\\\]|\$\$[\s\S]*?\$\$", blank, body)

    # Strip complete balanced argument commands. Preserve contents only for
    # authorial titles/captions; nested inline commands survive unchanged.
    command = re.compile(r"\\(caption|title|section\*?|subsection\*?|subsubsection\*?|label|includegraphics|bibliography|bibliographystyle|input|include)(?:\[[^\]]*\])?\s*\{")
    cursor = 0
    parts = []
    while True:
        match = command.search(body, cursor)
        if not match:
            parts.append(body[cursor:])
            break
        depth, end = 1, match.end()
        while end < len(body) and depth:
            char = body[end]
            slashes = len(body[:end]) - len(body[:end].rstrip("\\"))
            if slashes % 2 == 0:
                depth += (char == "{") - (char == "}")
            end += 1
        if depth:
            print("warning: unmatched LaTeX argument; inspect coverage manually", file=sys.stderr)
            parts.append(body[cursor:])
            break
        parts.append(body[cursor:match.start()])
        fragment = body[match.start():end]
        if match.group(1) in {"caption", "title"}:
            prefix = re.sub(r"[^\n]", " ", body[match.start():match.end()])
            parts.append(prefix + body[match.end():end-1] + " ")
        else:
            if match.group(1) in {"input", "include"}:
                print("warning: LaTeX includes are not expanded; inspect referenced prose manually", file=sys.stderr)
            parts.append(re.sub(r"[^\n]", " ", fragment))
        cursor = end
    body = "".join(parts)
    body = re.sub(r"\\(?:begin|end)\{[^}]+\}(?:\[[^\]]*\])?", blank, body)
    body = re.sub(r"\\item(?:\[[^\]]*\])?", "", body)
    body = re.sub(r"\\(?:maketitle|centering|par)\b", "", body)
    body = re.sub(r"\\looseness\s*=\s*-?\d+", "", body)
    cleaned = []
    for line in body.splitlines():
        stripped = line.strip()
        # Standalone layout commands are not prose; citation-led sentences stay.
        if (re.match(r"^\\(?:setlength|renewcommand|newcommand|vspace|hspace|clearpage|newpage|pagebreak|noindent|small|footnotesize)\b", stripped)
                or stripped in {"{", "}"}):
            cleaned.append("")
        else:
            cleaned.append(line)
    yield from iter_blocks("\n".join(cleaned))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Split a draft into screening units.")
    parser.add_argument("source", nargs="?", default="-", help="Markdown/text file, or - for stdin")
    parser.add_argument("--name", help="slug for unit ids; defaults to file stem")
    parser.add_argument("--format", choices=("auto", "text", "latex"), default="auto",
                        help="auto selects latex for .tex files; use latex explicitly for stdin")
    parser.add_argument("--candidates", action="store_true", help="include defensive-phrase candidate spans")
    parser.add_argument("--max-units", type=int, default=0, help="emit at most N units (0 = all)")
    parser.add_argument("--min-chars", type=int, default=12, help="skip blocks shorter than this")
    args = parser.parse_args(argv)

    if args.source == "-":
        text = sys.stdin.read()
        name = args.name or "draft"
    else:
        path = Path(args.source)
        text = path.read_text(encoding="utf-8")
        name = args.name or path.stem

    slug = slugify(name)
    emitted = 0
    use_latex = args.format == "latex" or (args.format == "auto" and args.source.endswith(".tex"))
    blocks = latex_blocks(text) if use_latex else iter_blocks(text)
    source_lines = text.splitlines()
    for start, end, block in blocks:
        paragraph = normalize(block)
        if len(paragraph) < args.min_chars or not is_prose(block, args.min_chars):
            continue
        unit = {
            "id": f"{slug}_p{emitted}",
            "start": start,
            "end": end,
            "paragraph": emitted,
            "text": paragraph,
        }
        if use_latex:
            unit["source_text"] = "\n".join(source_lines[start - 1:end])
            unit["format"] = "latex"
        if args.candidates:
            unit["candidates"] = find_candidates(paragraph)
        print(json.dumps(unit, ensure_ascii=False))
        emitted += 1
        if args.max_units and emitted >= args.max_units:
            break

    if emitted == 0:
        print("no prose units found", file=sys.stderr)
        return 1
    print(f"{emitted} unit(s) emitted", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
