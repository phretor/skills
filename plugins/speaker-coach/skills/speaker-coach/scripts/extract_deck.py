#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Extract per-slide text from a slide-deck PDF using pdftotext (poppler).

Usage:
    uv run extract_deck.py <deck.pdf> [--layout]

Prints a numbered slide list to stdout. Exits non-zero if pdftotext is missing
or the input cannot be read.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def require_pdftotext() -> str:
    path = shutil.which("pdftotext")
    if path is None:
        sys.stderr.write(
            "error: pdftotext not found on PATH. Install poppler:\n"
            "  macOS:  brew install poppler\n"
            "  Linux:  apt-get install poppler-utils\n",
        )
        sys.exit(2)
    return path


def extract(pdf_path: Path, layout: bool) -> str:
    pdftotext = require_pdftotext()
    args = [pdftotext]
    if layout:
        args.append("-layout")
    args.extend([str(pdf_path), "-"])
    result = subprocess.run(args, capture_output=True, check=False)
    if result.returncode != 0:
        sys.stderr.write(
            f"error: pdftotext failed (rc={result.returncode}):\n"
            f"{result.stderr.decode('utf-8', errors='replace')}",
        )
        sys.exit(result.returncode)
    return result.stdout.decode("utf-8", errors="replace")


def split_slides(text: str) -> list[str]:
    # pdftotext separates pages with form-feed (\x0c) by default.
    raw = text.split("\x0c")
    return [chunk.strip() for chunk in raw if chunk.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, help="path to the slide-deck PDF")
    parser.add_argument(
        "--layout",
        action="store_true",
        help="preserve original layout (pdftotext -layout)",
    )
    args = parser.parse_args()

    if not args.pdf.is_file():
        sys.stderr.write(f"error: file not found: {args.pdf}\n")
        return 1

    text = extract(args.pdf, args.layout)
    slides = split_slides(text)
    if not slides:
        sys.stderr.write("warning: pdftotext returned no extractable text\n")
        return 0

    for index, slide_text in enumerate(slides, start=1):
        print(f"## Slide {index}")
        print()
        print(slide_text)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
