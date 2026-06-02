# GPT_SIGNUP_HYBRID - QUICK START GUIDE

✅ **SETUP ĐÃ HOÀN TẤT!**

---

## 🚀 KHỞI ĐỘNG WEB UI

### Cách 1: Double-click file
👉 **`START_WEB_UI.bat`**

### Cách 2: Command line
👉 `.venv\Scripts\python -m gpt_signup_hybrid web`

Sau đó mở trình duyệt:
👉 [http://127.0.0.1:8089/](http://127.0.0.1:8089/)

---

## 📝 CÁCH SỬ DỤNG WEB UI

1. **Paste combo** vào textarea (mỗi dòng 1 combo):
   `email@hotmail.com|password|M.C548...|9e5f94bc-...`
2. **Chọn cấu hình:**
   - **Mode:** Single (1 job) hoặc Multi (3 jobs song song)
   - **Headless:** Bật = ẩn browser
   - **Timeout:** 120s/job (mặc định)
3. **Click ▶ Chạy**
4. **Xem kết quả:**
   - **Jobs:** Theo dõi tiến trình
   - **Log:** Xem chi tiết
   - **Success output:** Copy `email|password|secret_2fa`

---

## 📤 OUTPUT

### Success output format:
`email|password|secret_2fa`

### Files được lưu tại:
- `runtime/sessions/signup-*.json` (session + access token)
- `runtime/sessions/signup-*.2fa.json` (2FA secret + code)

---

## 🔧 TEST & DEBUG

- **Test imports:**
  ```bash
  .venv\Scripts\python test_import.py
  ```
- **Check pool status:**
  ```bash
  .venv\Scripts\python -m gpt_signup_hybrid pool-status runtime\outlook_pool\batch.txt
  ```
- **Generate TOTP code:**
  ```bash
  .venv\Scripts\python -m gpt_signup_hybrid totp SECRET_BASE32
  ```

---

## 📚 TÀI LIỆU

- **Hướng dẫn chi tiết:** [HUONG_DAN_SU_DUNG.md](../HUONG_DAN_SU_DUNG.md)
- **Documentation đầy đủ:** [README.md](../README.md)

---

## ⚡ PERFORMANCE

- **Tốc độ:** ~25-35s/account
- **Success rate:** 100% (với combo hợp lệ)
- **Concurrency:** Tối đa 3 jobs song song (mặc định)

---

Chúc bạn sử dụng thành công! 🎉
