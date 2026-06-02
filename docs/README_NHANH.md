# GPT_SIGNUP_HYBRID - README NHANH

---

## ⚡ LỆNH NHANH

- **🟢 BẬT WEB UI:** Double-click: `START_WEB_UI.bat`
- **🔴 TẮT WEB UI:** Double-click: `STOP_WEB_UI.bat` (Hoặc nhấn **Ctrl+C** trong terminal).
- **🔄 RESTART WEB UI:** Double-click: `RESTART_WEB_UI.bat`
- **🌐 MỞ WEB UI:** [http://127.0.0.1:8089/](http://127.0.0.1:8089/)

---

## 📁 CÁC FILE QUAN TRỌNG

### 🚀 Khởi động:
- `START_WEB_UI.bat` - Bật Web UI
- `STOP_WEB_UI.bat` - Tắt Web UI
- `RESTART_WEB_UI.bat` - Restart Web UI
- `setup.bat` - Setup lần đầu (đã chạy rồi)

### 📚 Hướng dẫn:
- `README_NHANH.md` - File này (hướng dẫn nhanh)
- `QUICK_START.md` - Quick start guide
- `HUONG_DAN_SU_DUNG.md` - Hướng dẫn chi tiết
- `LENH_TAT_BAT.md` - Lệnh tắt/bật chi tiết
- `GIAI_THICH_QUEUED.md` - Giải thích trạng thái queued
- `FAQ.md` - Câu hỏi thường gặp
- `README.md` - Documentation đầy đủ

### 🔧 Test & Debug:
- `test_import.py` - Test imports và config

---

## 📂 THƯ MỤC OUTPUT

```text
runtime/
├── sessions/           ← Output JSON files (session + 2FA)
├── outlook_state/      ← Token state tracking
├── outlook_pool/       ← Pool combo files (tạo ở đây)
├── profiles/           ← Browser profiles
└── har_hybrid/         ← HAR debug files
```

---

## 🎯 WORKFLOW CƠ BẢN

1. **Bật Web UI:**
   👉 Double-click `START_WEB_UI.bat`
2. **Mở trình duyệt:**
   👉 [http://127.0.0.1:8089/](http://127.0.0.1:8089/)
3. **Paste combo** (mỗi dòng 1 combo):
   `email@hotmail.com|password|M.C548...|9e5f94bc-...`
4. **Chọn cấu hình:**
   - **Mode:** Single hoặc Multi
   - **Headless:** Bật/Tắt
   - **Timeout:** 120s (mặc định)
5. **Click ▶ Chạy**
6. **Xem kết quả:**
   - **Jobs panel:** Theo dõi tiến trình
   - **Log panel:** Xem chi tiết
   - **Success output:** Copy `email|password|secret_2fa`
7. **Tắt Web UI khi xong:**
   👉 Double-click `STOP_WEB_UI.bat` hoặc nhấn `Ctrl+C`

---

## 🔑 FORMAT COMBO

`email|password|refresh_token|client_id`

### Ví dụ:
`user@hotmail.com|pass123|M.C548_BAY...|9e5f94bc-e8a4-4e73-b8be-63364c29d753`

---

## 📤 OUTPUT FORMAT

### Success output (Web UI):
`email|password|secret_2fa`

### Files (`runtime/sessions/`):
- `signup-*.json` (session + access token)
- `signup-*.2fa.json` (2FA secret + code)

---

## ⚙️ CẤU HÌNH NÂNG CAO

Sửa file `.env`:
- `HYBRID_MAX_CONCURRENT=2` — Số job chạy đồng thời (1-10)
- `HYBRID_JOB_TIMEOUT=240` — Timeout mỗi job (giây)
- `HYBRID_OUTLOOK_PROXY=` — Proxy (để trống = không dùng)

---

## 🐛 TROUBLESHOOTING NHANH

- **❌ Port 8089 bị chiếm:**
  👉 Double-click `STOP_WEB_UI.bat` → Đợi 3s → Double-click `START_WEB_UI.bat`
- **❌ Web UI không mở được:**
  1. Kiểm tra terminal có dòng `[web] starting at...`
  2. Thử `Ctrl+F5` trong browser
  3. Thử [http://localhost:8089/](http://localhost:8089/)
- **❌ Job bị lỗi:**
  1. Click vào job → Xem log
  2. Click **Retry** để thử lại
  3. Kiểm tra combo có đúng format không
- **❌ Job queued lâu:**
  👉 Xem `FAQ.md` hoặc `GIAI_THICH_QUEUED.md`

---

## 📞 CẦN TRỢ GIÚP?

### Xem các file hướng dẫn:
- `FAQ.md` — Câu hỏi thường gặp
- `LENH_TAT_BAT.md` — Lệnh tắt/bật chi tiết
- `HUONG_DAN_SU_DUNG.md` — Hướng dẫn đầy đủ
- `GIAI_THICH_QUEUED.md` — Giải thích queued

### Test môi trường:
`.venv\Scripts\python test_import.py`

---

Chúc bạn sử dụng thành công! 🎉

*Nhớ:*
- **✅ BẬT:** `START_WEB_UI.bat`
- **❌ TẮT:** `STOP_WEB_UI.bat` hoặc `Ctrl+C`
- **🔄 RESTART:** `RESTART_WEB_UI.bat`
- **🌐 URL:** [http://127.0.0.1:8089/](http://127.0.0.1:8089/)
