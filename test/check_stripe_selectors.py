import asyncio
import os
import sys
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    # Nhận checkout URL từ đối số dòng lệnh hoặc dùng một URL mẫu
    url = sys.argv[1] if len(sys.argv) > 1 else None
    if not url:
        print("Vui lòng truyền checkout URL vào dòng lệnh!")
        sys.exit(1)

    print(f"Đang phân tích trang Checkout: {url}")
    
    async with async_playwright() as p:
        # Launch browser headed để có thể quan sát
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            locale="en-IN",
            timezone_id="Asia/Kolkata"
        )
        page = await context.new_page()
        
        try:
            await page.goto(url)
            print("Đang đợi trang load...")
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(5000)
            
            # Chụp ảnh màn hình trước khi điền
            artifacts_dir = Path("C:/Users/Ryuga/.gemini/antigravity/artifacts")
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = artifacts_dir / "stripe_initial.png"
            await page.screenshot(path=screenshot_path)
            print(f"Đã chụp ảnh màn hình ban đầu tại: {screenshot_path}")
            
            # Liệt kê tất cả các frames
            print("Danh sách tất cả các frames trên trang:")
            for idx, frame in enumerate(page.frames):
                print(f"[{idx}] Name: {frame.name!r}, URL: {frame.url[:80]}...")
                
            # Click tab UPI
            upi_selectors = [
                "button:has-text('UPI')",
                "text=UPI",
                "label:has-text('UPI')",
                "#upi-tab",
                'button[aria-controls$="upi"]',
                'button[id$="upi"]'
            ]
            upi_clicked = False
            for sel in upi_selectors:
                try:
                    loc = page.locator(sel).first
                    if await loc.is_visible(timeout=2000):
                        await loc.click(timeout=2000)
                        upi_clicked = True
                        print(f"Đã click tab UPI bằng selector: {sel}")
                        break
                except Exception:
                    continue
                    
            await page.wait_for_timeout(3000)
            
            # Tìm tất cả các inputs trong main page và các frames
            print("\nTìm các ô Input trong Main Page:")
            inputs = await page.locator("input").all()
            for idx, inp in enumerate(inputs):
                name = await inp.get_attribute("name")
                id_val = await inp.get_attribute("id")
                placeholder = await inp.get_attribute("placeholder")
                visible = await inp.is_visible()
                print(f"  [{idx}] name={name!r}, id={id_val!r}, placeholder={placeholder!r}, visible={visible}")
                
            # Duyệt các frames để tìm input
            for idx, frame in enumerate(page.frames):
                if frame == page.main_frame:
                    continue
                try:
                    frame_inputs = await frame.locator("input").all()
                    if frame_inputs:
                        print(f"\nTìm thấy {len(frame_inputs)} inputs trong Frame [{idx}] ({frame.name!r}):")
                        for f_idx, inp in enumerate(frame_inputs):
                            name = await inp.get_attribute("name")
                            id_val = await inp.get_attribute("id")
                            placeholder = await inp.get_attribute("placeholder")
                            visible = await inp.is_visible()
                            print(f"    [{f_idx}] name={name!r}, id={id_val!r}, placeholder={placeholder!r}, visible={visible}")
                except Exception as exc:
                    print(f"  Frame [{idx}] error: {exc}")
                    
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
