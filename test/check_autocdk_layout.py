"""Verify Auto CDK input layout (2-col textareas) renders correctly via Playwright.

Loads http://127.0.0.1:8090/, switches to Auto CDK tab, screenshots input card
and asserts both textareas are visible side-by-side.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright

OUT = Path(__file__).parent / "autocdk_layout.png"
URL = "http://127.0.0.1:8090/"


async def main() -> int:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await ctx.new_page()
        await page.goto(URL, wait_until="domcontentloaded")
        # switch to Auto CDK tab
        await page.click('[data-tab="autocdk"]')
        await page.wait_for_selector("#tab-autocdk.tab-content.active", timeout=5000)
        # ensure the 2-col container exists
        loc = page.locator("#tab-autocdk .two-col-textareas")
        await loc.wait_for(state="visible", timeout=3000)
        box = await loc.bounding_box()
        combo = page.locator("#autocdk-combo-input")
        keys = page.locator("#autocdk-keys-input")
        cb = await combo.bounding_box()
        kb = await keys.bounding_box()
        # screenshot the input card
        card = page.locator("#tab-autocdk .card-input")
        await card.screenshot(path=str(OUT))
        await browser.close()

        if not (cb and kb and box):
            print("FAIL: bounding box null", file=sys.stderr)
            return 1
        # assert side by side: combo.x < keys.x AND vertical overlap
        side_by_side = cb["x"] < kb["x"] and abs(cb["y"] - kb["y"]) < 20
        same_height = abs(cb["height"] - kb["height"]) < 5
        print(f"combo: x={cb['x']:.0f} y={cb['y']:.0f} w={cb['width']:.0f} h={cb['height']:.0f}")
        print(f"keys : x={kb['x']:.0f} y={kb['y']:.0f} w={kb['width']:.0f} h={kb['height']:.0f}")
        print(f"side_by_side={side_by_side} same_height={same_height}")
        print(f"screenshot saved: {OUT}")
        if not side_by_side:
            print("FAIL: textareas not side-by-side", file=sys.stderr)
            return 1
        if not same_height:
            print("FAIL: textareas have very different heights", file=sys.stderr)
            return 1
        print("PASS")
        return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
