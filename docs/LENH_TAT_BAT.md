# LỆNH TẮT/BẬT WEB UI - HƯỚNG DẪN NHANH

---

## 🚀 CÁCH 1: SỬ DỤNG FILE .BAT (KHUYẾN NGHỊ - DỄ NHẤT)

### ✅ BẬT WEB UI:
👉 Double-click file: `START_WEB_UI.bat`

Hoặc chạy từ Command Prompt/PowerShell:
```powershell
cd e:\BotTele\gpt_signup_hybrid
.\START_WEB_UI.bat
```

### ❌ TẮT WEB UI:
👉 Nhấn **Ctrl+C** trong cửa sổ terminal, hoặc đóng cửa sổ terminal.

---

## 🔧 CÁCH 2: SỬ DỤNG COMMAND LINE

### ✅ BẬT WEB UI:
```powershell
cd e:\BotTele\gpt_signup_hybrid
.venv\Scripts\python -m gpt_signup_hybrid web
```

Hoặc đổi port khác:
```powershell
.venv\Scripts\python -m gpt_signup_hybrid web --port 8090
```

### ❌ TẮT WEB UI:
👉 Nhấn **Ctrl+C** trong terminal.

---

## 🔍 KIỂM TRA WEB UI CÓ ĐANG CHẠY KHÔNG

### Cách 1: Mở trình duyệt
👉 Vào [http://127.0.0.1:8089/](http://127.0.0.1:8089/)
- Nếu mở được → Đang chạy ✅
- Nếu không mở được → Đã tắt ❌

### Cách 2: Kiểm tra port
Chạy lệnh trong CMD:
```cmd
netstat -ano | findstr :8089
```
- Có kết quả `LISTENING` → Đang chạy ✅
- Không có hoặc chỉ có `TIME_WAIT` → Đã tắt ❌

### Cách 3: Kiểm tra process Python
Chạy lệnh:
```cmd
tasklist | findstr python
```
- Có `python.exe` → Có thể đang chạy.
- Không có → Đã tắt ❌

---

## ⚠️ TẮT CƯỠNG CHẾ (KHI CTRL+C KHÔNG HOẠT ĐỘNG)

### Bước 1: Tìm Process ID (PID)
Chạy lệnh:
```cmd
netstat -ano | findstr :8089
```
Ví dụ kết quả:
```text
TCP  127.0.0.1:8089  0.0.0.0:0  LISTENING  12345
                                           ^^^^^ (Process ID)
```

### Bước 2: Kill process
Chạy lệnh:
```cmd
taskkill /F /PID 12345
```

Hoặc tắt toàn bộ các process Python:
```cmd
taskkill /F /IM python.exe
```

---

## 🔄 KHỞI ĐỘNG LẠI (RESTART)

1. Tắt bằng **Ctrl+C**.
2. Đợi 2-3 giây.
3. Bật lại bằng **`START_WEB_UI.bat`**.

Hoặc tạo file `RESTART.bat`:
```bat
@echo off
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul
cd /d "%~dp0"
START_WEB_UI.bat
```

---

## 🎯 SHORTCUTS (TẠO PHÍM TẮT)

Tạo shortcut trên Desktop:
1. Click chuột phải vào `START_WEB_UI.bat`.
2. Chọn **"Create shortcut"**.
3. Kéo shortcut ra Desktop.
4. Đổi tên thành: `"GPT Signup Web UI"`.
5. Thay đổi icon nếu muốn.

*Giờ đây, bạn chỉ cần double-click icon trên Desktop để bật!*

---

## 🐛 TROUBLESHOOTING

### ❌ Lỗi: Port 8089 đã được sử dụng
- **Giải pháp 1:** Tắt process cũ bằng lệnh:
  ```cmd
  taskkill /F /IM python.exe
  ```
- **Giải pháp 2:** Đổi port khác:
  ```powershell
  .venv\Scripts\python -m gpt_signup_hybrid web --port 8090
  ```

### ❌ Lỗi: `ModuleNotFoundError`
- **Giải pháp:** Cài lại dependencies:
  ```powershell
  cd e:\BotTele\gpt_signup_hybrid
  .venv\Scripts\pip install -q pydantic typer httpx curl_cffi pyotp fastapi uvicorn camoufox playwright
  ```

### ❌ Lỗi: `.venv` không tồn tại
- **Giải pháp:** Chạy lại file setup:
  ```cmd
  setup.bat
  ```

### ❌ Web UI không mở được
- Kiểm tra server có đang chạy không (xem terminal).
- URL đúng chưa (`http://127.0.0.1:8089/`).
- Firewall có block không.
- Thử nhấn `Ctrl+F5` để refresh browser.

---

## 📝 TÓM TẮT NHANH

- **BẬT:** Double-click `START_WEB_UI.bat`
- **TẮT:** `Ctrl+C` trong terminal
- **URL:** [http://127.0.0.1:8089/](http://127.0.0.1:8089/)

---
Chúc bạn sử dụng thành công! 🎉
