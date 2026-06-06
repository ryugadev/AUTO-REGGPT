"""Guard regression cho Auto CDK: phân loại lỗi terminal vs retriable + dịch msg.

Chạy: .venv\\Scripts\\python.exe test\\check_autocdk_error_kind.py
Không cần network. Import trực tiếp các helper từ web/manager.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

# package root (chứa app/, web/, models.py...)
PKG_ROOT = Path(__file__).resolve().parent.parent
ROOT = PKG_ROOT.parent
for p in (str(ROOT), str(PKG_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)


def main() -> int:
    # import qua package để 'app' resolve đúng
    from gpt_signup_hybrid.web.manager import (
        _autocdk_is_terminal,
        _autocdk_translate_msg,
        _AutoCdkError,
    )

    ok = True

    # 1. Terminal markers
    terminal_cases = ["卡密不存在", "请输入卡密", "卡密已用完", "卡密已过期",
                      "account not eligible", "no free trial"]
    for msg in terminal_cases:
        if not _autocdk_is_terminal(msg):
            print(f"✗ phải terminal: {msg!r}")
            ok = False
    if ok:
        print("✓ terminal markers nhận diện đúng")

    # 2. Retriable (network/timeout) KHÔNG phải terminal
    retriable_cases = ["All connection attempts failed", "timeout", "查询失败", "出码失败"]
    ok2 = True
    for msg in retriable_cases:
        if _autocdk_is_terminal(msg):
            print(f"✗ phải retriable: {msg!r}")
            ok2 = False
    print("✓ retriable không bị đánh terminal" if ok2 else "✗ retriable sai")
    ok = ok and ok2

    # 3. Dịch msg
    tr = _autocdk_translate_msg("卡密不存在")
    ok3 = tr == "CDK không tồn tại"
    print(f"{'✓' if ok3 else '✗'} dịch msg: 卡密不存在 → {tr!r}")
    ok = ok and ok3

    # 4. _AutoCdkError mang kind
    e = _AutoCdkError("x", kind="terminal")
    ok4 = e.kind == "terminal"
    print(f"{'✓' if ok4 else '✗'} _AutoCdkError.kind")
    ok = ok and ok4

    print("\n" + ("ALL PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
