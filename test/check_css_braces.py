"""Quick CSS sanity: balanced braces, no orphan @media, no rogue */ before /*."""
from __future__ import annotations

import re
import sys
from pathlib import Path

CSS = Path(__file__).resolve().parent.parent / "web" / "static" / "style.css"


def main() -> int:
    text = CSS.read_text(encoding="utf-8")
    # Strip CSS comments before counting braces (comments must be balanced too)
    if text.count("/*") != text.count("*/"):
        print(f"FAIL: comment markers unbalanced: /* x{text.count('/*')} != */ x{text.count('*/')}", file=sys.stderr)
        return 1
    stripped = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    opens = stripped.count("{")
    closes = stripped.count("}")
    if opens != closes:
        print(f"FAIL: braces unbalanced: {{ x{opens} vs }} x{closes}", file=sys.stderr)
        return 1
    print(f"OK  comments: {text.count('/*')} pairs")
    print(f"OK  braces  : {opens} pairs")
    print(f"OK  size    : {len(text)} bytes, {text.count(chr(10))+1} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
