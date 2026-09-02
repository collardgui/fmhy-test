#!/usr/bin/env python3
"""Extract FMHY's French, Live TV, and Live Sports sections."""

from __future__ import annotations

import argparse
import re
import urllib.request
from pathlib import Path

SOURCE_URL = "https://raw.githubusercontent.com/wiki/fmhy/FMHY/Non-Eng.md"
STREAMING_SOURCE_URL = "https://raw.githubusercontent.com/wiki/fmhy/FMHY/Streaming.md"
SECTION_START = re.compile(r"^#\s+►\s+(?:French|Français)\s*/\s*(?:Français|French)\s*$", re.IGNORECASE)
SECTION_END = re.compile(r"^#\s+►\s+", re.IGNORECASE)
LIVE_TV_START = re.compile(r"^##\s+▷\s+Live TV\s*$", re.IGNORECASE)
LIVE_SPORTS_START = re.compile(r"^##\s+▷\s+Live Sports\s*$", re.IGNORECASE)
SUBSECTION_END = re.compile(r"^##\s+", re.IGNORECASE)


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


def extract_subsection(markdown: str, start_pattern: re.Pattern[str], label: str) -> str:
    lines = markdown.splitlines()
    start = next((index for index, line in enumerate(lines) if start_pattern.match(line.strip())), None)
    if start is None:
        raise ValueError(f"{label} section not found in the FMHY Streaming wiki")

    end = next(
        (index for index in range(start + 1, len(lines)) if SUBSECTION_END.match(lines[index].strip())),
        len(lines),
    )
    section = "\n".join(lines[start:end]).strip()
    if not section:
        raise ValueError(f"{label} section is empty")
    return section + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("docs/index.md"))
    parser.add_argument("--source", default=SOURCE_URL)
    args = parser.parse_args()

    french_section = extract_french_section(fetch_source(args.source))
    streaming_source = fetch_source(STREAMING_SOURCE_URL)
    live_tv_section = extract_subsection(streaming_source, LIVE_TV_START, "Live TV")
    live_sports_section = extract_subsection(streaming_source, LIVE_SPORTS_START, "Live Sports")
    output = french_section + "\n# ► Live TV / Sports\n\n" + live_tv_section + "\n" + live_sports_section
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "# FMHY - French\n\n"
        "Source: [FMHY Non-Eng wiki](https://github.com/fmhy/FMHY/wiki/Non-Eng)\n\n"
        f"{output}"
        "Source: [FMHY Streaming wiki](https://github.com/fmhy/FMHY/wiki/Streaming)\n\n",
        encoding="utf-8",
    )
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()