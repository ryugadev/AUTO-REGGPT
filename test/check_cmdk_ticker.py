"""Verify Command Palette (Ctrl+K) + Number Ticker hoạt động trong browser thật.

Chạy: .venv\\Scripts\\python.exe test\\check_cmdk_ticker.py
"""
from __future__ import annotations

import asyncio
import sys

BASE = "http://127.0.0.1:8090"


async def main() -> int:
    from playwright.async_api import async_playwright

    errs = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        page.on("pageerror", lambda e: errs.append(f"PAGEERROR: {e}"))
        page.on("console", lambda m: errs.append(f"CONSOLE[{m.type}]: {m.text}") if m.type == "error" else None)

        await page.goto(BASE, wait_until="domcontentloaded")
        await asyncio.sleep(2)

        # 1. GptUi exports
        ui_check = await page.evaluate("""() => ({
            openCmdk: typeof window.GptUi.openCmdk,
            bumpTicker: typeof window.GptUi.bumpTicker,
            setTickerValue: typeof window.GptUi.setTickerValue,
            registerTabSSE: typeof window.GptUi.registerTabSSE,
        })""")
        print(f"GptUi exports: {ui_check}")
        ok = all(v == "function" for v in ui_check.values())
        print(f"{'OK' if ok else 'XX'}  exports")

        # 2. Click cmdk trigger → modal show
        await page.click("#cmdk-trigger")
        await asyncio.sleep(0.4)
        modal_visible = await page.evaluate(
            "() => document.getElementById('cmdk-modal').classList.contains('show')"
        )
        print(f"{'OK' if modal_visible else 'XX'}  cmdk modal show after trigger click")

        # 3. Type → filter list
        await page.fill("#cmdk-input", "auto")
        await asyncio.sleep(0.3)
        items = await page.eval_on_selector_all(
            "#cmdk-list .cmdk-item[data-id]", "els => els.map(e => e.dataset.id)"
        )
        has_auto = "tab:autocdk" in items
        print(f"{'OK' if has_auto else 'XX'}  filter 'auto' → {items}")

        # 4. Press Enter → action chạy + close
        await page.press("#cmdk-input", "Enter")
        await asyncio.sleep(0.4)
        active_tab = await page.evaluate(
            "() => document.querySelector('.tab-btn.active').dataset.tab"
        )
        modal_closed = not await page.evaluate(
            "() => document.getElementById('cmdk-modal').classList.contains('show')"
        )
        print(f"{'OK' if active_tab == 'autocdk' and modal_closed else 'XX'}  Enter chạy action (tab={active_tab}, closed={modal_closed})")

        # 5. Esc đóng modal
        await page.click("#cmdk-trigger")
        await asyncio.sleep(0.2)
        await page.keyboard.press("Escape")
        await asyncio.sleep(0.4)
        closed = not await page.evaluate(
            "() => document.getElementById('cmdk-modal').classList.contains('show')"
        )
        print(f"{'OK' if closed else 'XX'}  Esc đóng modal")

        # 6. Ctrl+K toggle
        await page.keyboard.press("Control+KeyK")
        await asyncio.sleep(0.4)
        opened = await page.evaluate(
            "() => document.getElementById('cmdk-modal').classList.contains('show')"
        )
        print(f"{'OK' if opened else 'XX'}  Ctrl+K mở modal")
        await page.keyboard.press("Escape")

        # 7. Number ticker bump
        await page.evaluate("""() => {
            const el = document.createElement('span');
            el.id = '_test_ticker';
            el.className = 'num-ticker';
            el.textContent = '0';
            document.body.appendChild(el);
            window.GptUi.setTickerValue(el, '5');
        }""")
        await asyncio.sleep(0.1)
        bump = await page.evaluate(
            "() => document.getElementById('_test_ticker').classList.contains('bump')"
        )
        val = await page.evaluate("() => document.getElementById('_test_ticker').textContent")
        print(f"{'OK' if bump and val == '5' else 'XX'}  ticker bump (val={val}, bump={bump})")

        # Console errors?
        print()
        if errs:
            print("ERRORS:")
            for e in errs[:10]:
                print(f"  {e}")
        else:
            print("(no console errors)")

        await browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
