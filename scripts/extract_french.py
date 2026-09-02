#!/usr/bin/env python3
"""Extract the French section from the FMHY Non-Eng wiki page."""

from __future__ import annotations

import argparse
import re
import urllib.request
from pathlib import Path

SOURCE_URL = "https://raw.githubusercontent.com/wiki/fmhy/FMHY/Non-Eng.md"
SECTION_START = re.compile(r"^#\s+►\s+(?:French|Français)\s*/\s*(?:Français|French)\s*$", re.IGNORECASE)
SECTION_END = re.compile(r"^#\s+►\s+", re.IGNORECASE)


def fetch_source(url: str = SOURCE_URL) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "fmhy-test/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def extract_french_section(markdown: str) -> str:
    lines = markdown.splitlines()
    start = next((index for index, line in enumerate(lines) if SECTION_START.match(line.strip())), None)
    if start is None:
        raise ValueError("French section not found in the FMHY Non-Eng wiki")

    end = next(
        (index for index in range(start + 1, len(lines)) if SECTION_END.match(lines[index].strip())),
        len(lines),
    )
    section = "\n".join(lines[start:end]).strip()
    if not section:
        raise ValueError("French section is empty")
    return section + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("docs/index.md"))
    parser.add_argument("--source", default=SOURCE_URL)
    args = parser.parse_args()

    output = extract_french_section(fetch_source(args.source))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "# FMHY - French\n\n"
        "Source: [FMHY Non-Eng wiki](https://github.com/fmhy/FMHY/wiki/Non-Eng)\n\n"
        f"{output}",
        encoding="utf-8",
    )
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()