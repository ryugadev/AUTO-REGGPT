import asyncio
import os
import sys
from pathlib import Path

# Thêm thư mục gốc vào path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from config import load_settings

async def main():
    print("=== TEST GỬI ẢNH CHỤP MÀN HÌNH TỚI TELEGRAM BOT ===")
    settings = load_settings()
    token = settings.telegram_bot_token
    chat_id = settings.telegram_chat_id
    
    print(f"TELEGRAM_BOT_TOKEN: {token}")
    print(f"TELEGRAM_CHAT_ID: {chat_id}")
    
    if not token or not chat_id:
        print("[-] LỖI: Chưa cấu hình TELEGRAM_BOT_TOKEN hoặc TELEGRAM_CHAT_ID trong .env!")
        return

    # Khởi tạo Playwright chụp ảnh google.com để test
    from playwright.async_api import async_playwright
    import httpx
    
    print("[-] Đang mở trình duyệt ngầm Playwright để chụp ảnh google.com làm mẫu...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto("https://www.google.com", timeout=30000)
            await page.wait_for_load_state("networkidle")
            
            print("[+] Đã mở google.com thành công. Đang tiến hành chụp ảnh màn hình...")
            screenshot_bytes = await page.screenshot(type="png")
            print(f"[+] Đã chụp ảnh màn hình thành công! Kích thước: {len(screenshot_bytes)} bytes.")
            
            print("[-] Đang gửi ảnh chụp màn hình tới Telegram bot...")
            url = f"https://api.telegram.org/bot{token}/sendPhoto"
            caption = "📸 Test chụp màn hình tự động từ hệ thống gpt_signup_hybrid!"
            
            files = {"photo": ("google_test.png", screenshot_bytes, "image/png")}
            data = {"chat_id": chat_id, "caption": caption}
            
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, files=files, data=data, timeout=30.0)
                if resp.status_code == 200:
                    print("[+] THÀNH CÔNG! Bot Telegram đã gửi ảnh chụp màn hình thành công tới bạn.")
                    print("Hãy mở Telegram kiểm tra xem có bức ảnh google.com chưa nhé!")
                else:
                    print(f"[-] THẤT BẠI: Telegram API trả về mã lỗi {resp.status_code}")
                    print(f"Chi tiết: {resp.text}")
        except Exception as exc:
            print(f"[-] LỖI XẢY RA: {exc}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
