import asyncio
import os
import sys
from pathlib import Path

# Thêm thư mục gốc vào path để import được
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from config import load_settings

async def main():
    print("=== KIỂM TRA KẾT NỐI TELEGRAM BOT ===")
    settings = load_settings()
    token = settings.telegram_bot_token
    chat_id = settings.telegram_chat_id
    
    print(f"TELEGRAM_BOT_TOKEN: {token[:10]}...{token[-5:] if len(token) > 10 else ''}")
    print(f"TELEGRAM_CHAT_ID: {chat_id}")
    
    if not token or not chat_id:
        print("[-] LỖI: Chưa cấu hình TELEGRAM_BOT_TOKEN hoặc TELEGRAM_CHAT_ID trong file .env!")
        return

    import httpx
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "🔔 Test kết nối từ hệ thống gpt_signup_hybrid thành công!"
    }
    
    print("[-] Đang gửi tin nhắn test tới Telegram...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=10.0)
            if resp.status_code == 200:
                print("[+] THÀNH CÔNG! Bot Telegram đã gửi tin nhắn thành công tới chat ID của bạn.")
                print("Hãy kiểm tra Telegram của bạn xem đã nhận được tin nhắn chưa nhé!")
            else:
                print(f"[-] THẤT BẠI: Telegram API trả về mã lỗi {resp.status_code}")
                print(f"Chi tiết phản hồi: {resp.text}")
    except Exception as exc:
        print(f"[-] LỖI KHI GỬI: {exc}")

if __name__ == "__main__":
    asyncio.run(main())
