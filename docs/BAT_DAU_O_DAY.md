# 👋 BẮT ĐẦU TỪ ĐÂY!

Chào mừng bạn đến với GPT_SIGNUP_HYBRID! 🎉

---

## ✅ SETUP ĐÃ HOÀN TẤT!

Dự án đã được cài đặt thành công với:
- ✓ Python 3.12.8
- ✓ Virtual environment (`.venv`)
- ✓ Tất cả dependencies
- ✓ Playwright Firefox + Camoufox
- ✓ File cấu hình `.env`
- ✓ Thư mục `runtime/`

---

## 🚀 CÁCH SỬ DỤNG NHANH (3 BƯỚC)

1. **BẬT WEB UI:**
   👉 Double-click: `START_WEB_UI.bat`

2. **MỞ TRÌNH DUYỆT:**
   👉 [http://127.0.0.1:8089/](http://127.0.0.1:8089/)

3. **PASTE COMBO VÀ CHẠY:**
   - Paste combo vào textarea
   - Click **▶ Chạy**
   - Xem kết quả trong Success output

---

## 📚 NÊN ĐỌC FILE NÀO?

### 🌟 ĐỌC ĐẦU TIÊN (QUAN TRỌNG)

- **[README_NHANH.md](README_NHANH.md)**
  - Tóm tắt toàn bộ: Lệnh, workflow, troubleshooting
  - ĐỌC FILE NÀY TRƯỚC!

---

### 📖 ĐỌC KHI CẦN

- **[LENH_TAT_BAT.md](LENH_TAT_BAT.md)**
  - Hướng dẫn chi tiết cách tắt/bật Web UI
  - Troubleshooting khi không tắt được
  - Tạo shortcuts
- **[FAQ.md](FAQ.md)**
  - Câu hỏi thường gặp
  - Giải đáp nhanh các vấn đề phổ biến
- **[GIAI_THICH_QUEUED.md](../GIAI_THICH_QUEUED.md)**
  - Giải thích tại sao job bị "queued"
  - Cách xử lý khi job queued lâu
- **[QUICK_START.md](QUICK_START.md)**
  - Quick start guide
  - Performance metrics
- **[HUONG_DAN_SU_DUNG.md](../HUONG_DAN_SU_DUNG.md)**
  - Hướng dẫn đầy đủ nhất
  - CLI commands
  - Cấu hình nâng cao
- **[README.md](../README.md)**
  - Documentation gốc (tiếng Việt)
  - Kiến trúc hệ thống
  - API reference

---

## 🎮 CÁC FILE .BAT (DOUBLE-CLICK ĐỂ CHẠY)

- **`START_WEB_UI.bat`**
  - Bật Web UI
  - Dùng file này để khởi động!
- **`STOP_WEB_UI.bat`**
  - Tắt Web UI
  - Hoặc nhấn Ctrl+C trong terminal
- **`RESTART_WEB_UI.bat`**
  - Restart Web UI (tắt rồi bật lại)
- **`setup.bat`**
  - Setup lần đầu (đã chạy rồi, không cần chạy lại)

---

## 🔑 THÔNG TIN QUAN TRỌNG

- **Web UI URL:** [http://127.0.0.1:8089/](http://127.0.0.1:8089/)
- **Format combo:** `email|password|refresh_token|client_id`
- **Output format:** `email|password|secret_2fa`
- **Output files:**
  - `runtime/sessions/signup-*.json`
  - `runtime/sessions/signup-*.2fa.json`

---

## ⚡ LỆNH NHANH

- **BẬT:** `START_WEB_UI.bat`
- **TẮT:** `STOP_WEB_UI.bat` hoặc `Ctrl+C`
- **RESTART:** `RESTART_WEB_UI.bat`
- **TEST:** `.venv\Scripts\python test_import.py`

---

## 🎯 WORKFLOW ĐƠN GIẢN

1. `START_WEB_UI.bat`
2. Mở [http://127.0.0.1:8089/](http://127.0.0.1:8089/)
3. Paste combo
4. Click **▶ Chạy**
5. Copy kết quả từ Success output
6. `STOP_WEB_UI.bat` khi xong

---

## ❓ CÂU HỎI THƯỜNG GẶP

- **Q: Job bị "queued" là sao?**
  - A: Đang chờ trong hàng đợi, bình thường! (Xem [GIAI_THICH_QUEUED.md](../GIAI_THICH_QUEUED.md))
- **Q: Làm sao chạy nhiều job cùng lúc?**
  - A: Chọn Mode: Multi trong Web UI, hoặc sửa `HYBRID_MAX_CONCURRENT` trong `.env`
- **Q: Job chạy mất bao lâu?**
  - A: ~30-45 giây/job (signup + 2FA)
- **Q: Làm sao biết job thành công?**
  - A: Status = success 🟢. Copy từ Success output panel.
- **Q: Job bị lỗi thì sao?**
  - A: Click vào job → Xem log → Click Retry (Xem [FAQ.md](FAQ.md) để biết lỗi phổ biến).

---

## 🐛 TROUBLESHOOTING NHANH

### Web UI không mở được:
1. Kiểm tra `START_WEB_UI.bat` có chạy không.
2. Xem terminal có dòng `[web] starting at...`.
3. Thử `Ctrl+F5` trong browser.

### Port 8089 bị chiếm:
1. `STOP_WEB_UI.bat`
2. Đợi 3 giây
3. `START_WEB_UI.bat`

### Lỗi ModuleNotFoundError:
1. Chạy lại `setup.bat`
2. Hoặc: `.venv\Scripts\pip install pydantic typer httpx...`

---

## 📞 CẦN TRỢ GIÚP?

Đọc theo thứ tự:
1. **[README_NHANH.md](README_NHANH.md)** (Bắt đầu ở đây)
2. **[FAQ.md](FAQ.md)** (Câu hỏi thường gặp)
3. **[LENH_TAT_BAT.md](LENH_TAT_BAT.md)** (Lệnh tắt/bật)
4. **[HUONG_DAN_SU_DUNG.md](../HUONG_DAN_SU_DUNG.md)** (Hướng dẫn đầy đủ)

---

## 🎉 SẴN SÀNG SỬ DỤNG!

Bây giờ bạn có thể:
1. Double-click `START_WEB_UI.bat`
2. Mở [http://127.0.0.1:8089/](http://127.0.0.1:8089/)
3. Bắt đầu signup ChatGPT accounts!

Chúc bạn thành công! 🚀

---
*P/S: Đọc [README_NHANH.md](README_NHANH.md) để biết thêm chi tiết!*
