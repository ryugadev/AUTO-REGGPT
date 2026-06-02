"""Verify _fill_about_you đã có: blur sau type age, ép-set hidden birthday,
và nút 'Finish creating account'. Guard regression cho form /about-you mới.

Chạy: .venv\\Scripts\\python.exe test\\check_about_you_fill.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "browser_phase.py"


def main() -> int:
    src = SRC.read_text(encoding="utf-8")
    checks = {
        "blur sau type age": 'log(f"[browser] typed age={age} + blur")' in src,
        "press Tab (blur)": 'await page.keyboard.press("Tab")' in src,
        "ép set hidden birthday": "input[name=\\\"birthday\\\"]" in src or 'name="birthday"' in src,
        "dispatch input/change cho React": "dispatchEvent(new Event('input'" in src,
        "nút Finish creating account": 'button:has-text("Finish creating account")' in src,
        "verify birthday today_iso": "today_iso" in src,
    }
    ok = True
    for name, passed in checks.items():
        print(f"{'✓' if passed else '✗'} {name}")
        ok = ok and passed

    # Đảm bảo Finish button đứng TRƯỚC generic submit trong danh sách click chính
    fill_idx = src.find("Verify hidden `birthday`")
    submit_idx = src.find('button:has-text("Finish creating account")', fill_idx if fill_idx > 0 else 0)
    generic_idx = src.find('button[type="submit"]', submit_idx if submit_idx > 0 else 0)
    order_ok = 0 < submit_idx < generic_idx
    print(f"{'✓' if order_ok else '✗'} Finish button ưu tiên trước generic submit")
    ok = ok and order_ok

    print("\n" + ("ALL PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
