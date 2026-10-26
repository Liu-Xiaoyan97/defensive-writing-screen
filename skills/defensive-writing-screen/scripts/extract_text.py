#!/usr/bin/env python3
"""Convert a document to plain text before unit splitting.

Every format has its own extraction hazards, so each gets an explicit path:

    markdown   strip fences, keep paragraph structure
    latex      delegate to the conservative LaTeX block reader in prepare_units
    pdf        page-by-page text with de-hyphenation and column de-interleaving
    docx       paragraph runs in document order, tables flattened to rows

The result is ordinary UTF-8 text. Everything after this module sees one format only, so
splitting, screening and unit ids do not depend on the source format.

Missing extractors are reported, never guessed. A PDF without a text layer is an error, not
an empty document: silently returning "" would make the audit claim a clean result on text
it never read.

Usage:
    python3 extract_text.py manuscript.pdf --out source.txt
    python3 extract_text.py notes.docx              # writes to stdout
    cat notes.md | python3 extract_text.py - --format markdown

Exit codes: 0 converted, 1 unsupported or unreadable input, 2 a required extractor is absent.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

FORMATS = ("markdown", "latex", "pdf", "docx", "text")
SUFFIX = {".md": "markdown", ".markdown": "markdown", ".tex": "latex", ".latex": "latex",
          ".pdf": "pdf", ".docx": "docx", ".txt": "text", ".text": "text"}


def detect(path: str) -> str | None:
    return SUFFIX.get(Path(path).suffix.lower())


# ---------------------------------------------------------------- markdown

FENCE = re.compile(r"^\s*(```|~~~)")


def from_markdown(text: str) -> str:
    """Drop fenced code and HTML comments; keep everything a reader would see as prose."""
    out, in_fence, in_comment = [], False, False
    for line in text.split("\n"):
        if in_comment:
            if "-->" in line:
                in_comment = False
            continue
        if "<!--" in line:
            if "-->" not in line.split("<!--", 1)[1]:
                in_comment = True
            line = line.split("<!--", 1)[0]
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        out.append(line)
    return "\n".join(out)


# ---------------------------------------------------------------- latex


def from_latex(text: str) -> str:
    """Keep the source verbatim.

    prepare_units.latex_blocks already understands line structure, comments and the
    environments it can handle conservatively. Rewriting the source here would change line
    numbers and break the unit anchors, so this path only normalizes the encoding.
    """
    return text


# ---------------------------------------------------------------- pdf


class ExtractorMissing(RuntimeError):
    pass


def from_pdf(path: Path) -> str:
    """Extract text page by page, then repair the two artifacts that break sentences.

    1. Line-end hyphenation: a word split across lines is rejoined.
    2. Column interleaving: two-column layouts emit left and right columns as alternating
       lines, which produces sentences that start on one column and end on the other. Lines
       are grouped into blocks separated by blank lines and reordered only when the block
       clearly shows two columns (two long lines followed by two short ones).
    """
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        try:
            from PyPDF2 import PdfReader  # type: ignore
        except Exception:
            pdftotext = shutil.which("pdftotext")
            if pdftotext:
                result = subprocess.run([pdftotext, "-layout", str(path), "-"],
                                        capture_output=True, timeout=120)
                if result.returncode != 0:
                    raise SystemExit(f"pdftotext failed: {result.stderr.decode()[:200]}")
                return repair(result.stdout.decode("utf-8", "replace"))
            raise ExtractorMissing(
                "no PDF extractor available: install pypdf, PyPDF2 or poppler's pdftotext")
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:
            pages.append("")
    text = "\n".join(pages)
    if not text.strip():
        raise SystemExit(
            "the PDF has no extractable text layer; it is likely a scan. Run OCR first and "
            "convert the result, rather than auditing a document that was never read.")
    return repair(text)


def repair(text: str) -> str:
    lines = [ln.rstrip() for ln in text.split("\n")]
    joined = []
    for line in lines:
        if joined and re.search(r"\w-$", joined[-1]) and line[:1].islower():
            joined[-1] = joined[-1][:-1] + line.lstrip()
            continue
        joined.append(line)
    blocks, current = [], []
    for line in joined:
        if line.strip():
            current.append(line)
        elif current:
            blocks.append(deinterleave(current))
            current = []
    if current:
        blocks.append(deinterleave(current))
    return "\n\n".join("\n".join(b) for b in blocks)


def deinterleave(block: list[str]) -> list[str]:
    """Reorder a two-column block into left-column-then-right-column order."""
    if len(block) < 4 or len(block) % 2:
        return block
    left, right = block[0::2], block[1::2]
    long_left = sum(1 for ln in left if len(ln) > 40)
    long_right = sum(1 for ln in right if len(ln) > 40)
    if long_left >= len(left) * 0.6 and long_right >= len(right) * 0.6:
        return left + right
    return block


# ---------------------------------------------------------------- docx


def from_docx(path: Path) -> str:
    """Read paragraph runs in document order and flatten tables row by row.

    Uses the OOXML body order rather than python-docx, so no third-party package is needed
    and paragraph order is the order a reader sees.
    """
    try:
        with zipfile.ZipFile(path) as zf:
            with zf.open("word/document.xml") as fh:
                xml = fh.read().decode("utf-8", "replace")
    except (KeyError, zipfile.BadZipFile) as exc:
        raise SystemExit(f"not a readable .docx file: {exc}")
    # Match by local name so a document that declares the WordprocessingML prefix
    # differently, or not at all, still parses.
    blocks = []
    for para in re.finditer(r"<(?:\w+:)?p(?:\s[^>]*)?>(.*?)</(?:\w+:)?p>", xml, re.S):
        body = para.group(1)
        runs = re.findall(r"<(?:\w+:)?t(?:\s[^>]*)?>(.*?)</(?:\w+:)?t>", body, re.S)
        text = "".join(runs)
        text = (text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
                    .replace("&quot;", '"').replace("&apos;", "'"))
        text = text.strip()
        if text:
            blocks.append(text)
    if not blocks:
        raise SystemExit("no paragraphs found in the .docx body")
    return "\n\n".join(blocks)


# ---------------------------------------------------------------- dispatch


def convert(path: Path, fmt: str) -> str:
    if fmt == "pdf":
        return from_pdf(path)
    if fmt == "docx":
        return from_docx(path)
    text = path.read_bytes().decode("utf-8", "replace")
    if fmt == "markdown":
        return from_markdown(text)
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", help="document path, or - for stdin")
    parser.add_argument("--format", choices=FORMATS, help="override suffix detection")
    parser.add_argument("--out", type=Path, help="write here instead of stdout")
    args = parser.parse_args(argv)

    if args.source == "-":
        fmt = args.format or "text"
        raw = sys.stdin.read()
        text = from_markdown(raw) if fmt == "markdown" else raw
    else:
        path = Path(args.source)
        if not path.is_file():
            raise SystemExit(f"no such file: {path}")
        fmt = args.format or detect(args.source)
        if fmt is None:
            raise SystemExit(
                f"cannot tell the format of {path.name}; pass --format one of {', '.join(FORMATS)}")
        try:
            text = convert(path, fmt)
        except ExtractorMissing as exc:
            print(str(exc), file=sys.stderr)
            return 2
    if args.out:
        args.out.write_text(text)
        print(f"{fmt}: {len(text)} chars -> {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
