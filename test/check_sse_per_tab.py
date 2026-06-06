"""Guard: cơ chế SSE-per-active-tab để tránh đầy quota 6 connection/origin.

Kiểm tra (static, đọc source JS):
  - app.js có registerTabSSE + chỉ giữ 1 _activeSSE.
  - 6 module JS đều dùng registerTabSSE thay vì connectSSE() vô điều kiện.
  - Không còn setTimeout(connectSSE, ...) auto-reconnect (gây tích tụ connection).

Chạy: .venv\\Scripts\\python.exe test\\check_sse_per_tab.py
"""
from __future__ import annotations

import sys
from pathlib import Path

STATIC = Path(__file__).resolve().parent.parent / "web" / "static"

TABS = {
    "app.js": "reg",
    "session.js": "session",
    "link.js": "link",
    "checker.js": "checker",
    "autocdk.js": "autocdk",
    "cdkcheck.js": "cdkcheck",
}


def main() -> int:
    ok = True

    app = (STATIC / "app.js").read_text(encoding="utf-8")
    for token in ("function registerTabSSE", "_activeSSE", "_closeActiveSSE", "_openTabSSE"):
        passed = token in app
        print(f"{'OK' if passed else 'XX'}  app.js chứa {token}")
        ok = ok and passed

    for fname, tabid in TABS.items():
        src = (STATIC / fname).read_text(encoding="utf-8")
        has_register = f"registerTabSSE('{tabid}'" in src
        no_autoreconnect = "setTimeout(connectSSE" not in src
        print(f"{'OK' if has_register else 'XX'}  {fname} registerTabSSE('{tabid}')")
        print(f"{'OK' if no_autoreconnect else 'XX'}  {fname} bỏ setTimeout(connectSSE)")
        ok = ok and has_register and no_autoreconnect

    print("\n" + ("ALL PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
