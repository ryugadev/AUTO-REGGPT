# FAQ - FREQUENTLY ASKED QUESTIONS

---

## ❓ Job bị "queued" là sao?

✅ **Đây là trạng thái BÌNH THƯỜNG!**

`Queued` = Đang chờ trong hàng đợi để được xử lý.

### Lý do:
- **Mode Single:** Chỉ chạy 1 job/lần → Jobs khác phải chờ.
- **Mode Multi:** Chạy tối đa 3 jobs song song (hoặc cấu hình khác) → Job thứ 4+ phải chờ.
- **Stagger delay:** Đợi 5-10s giữa các job (chống spam).

### Giải pháp:
- Đợi job đang running hoàn thành.
- Đổi sang Mode Multi để chạy nhiều job hơn.
- Kiên nhẫn, job sẽ tự chuyển sang "running".

*Chi tiết: Xem file [GIAI_THICH_QUEUED.md](../GIAI_THICH_QUEUED.md)*

---

## ❓ Làm sao để chạy nhiều job cùng lúc?

### Cách 1: Trong Web UI
👉 Chọn **Mode: Multi** (mặc định tối đa 3 song song).

### Cách 2: Sửa file `.env`
1. Thay đổi cấu hình: `HYBRID_MAX_CONCURRENT=5`
2. Restart Web UI.

### Khuyến nghị:
- **RAM 8GB:** 1-2 jobs
- **RAM 16GB:** 2-3 jobs
- **RAM 32GB:** 3-5 jobs

---

## ❓ Job chạy mất bao lâu?

**Thời gian trung bình:** 25-35 giây/job

### Chi tiết (Breakdown):
- **Phase 1 (Browser signup):** ~25s
- **Phase 2 (Enable 2FA):** ~5s
- **Stagger delay:** 5-10s (nếu ở Multi mode)

**Tổng cộng (Total):** 30-45s/job

---

## ❓ Làm sao biết job thành công?

### Trong Web UI:
- **Job status:** success 🟢
- **Success output panel:** Hiện `email|password|secret_2fa`
- Click **"Copy all"** để copy kết quả.

### Files output:
- `runtime/sessions/signup-*.json` (session + token)
- `runtime/sessions/signup-*.2fa.json` (2FA secret)

---

## ❓ Job bị lỗi thì làm sao?

### Bước 1: Xem log
👉 Click vào job lỗi → Xem log panel → Tìm dòng `[error]` hoặc `[fatal]`.

### Bước 2: Retry
👉 Click vào job lỗi → Click **"Retry"**.

### Bước 3: Kiểm tra combo
- Combo có đúng format không?
- Refresh token còn valid không?

### Lỗi phổ biến:
- **OTP timeout:** Combo hết hạn hoặc mail chậm.
- **registration_disallowed:** IP bị block → Đổi proxy.
- **invalid_grant:** Refresh token chết → Dùng combo khác.

---

## ❓ Format combo là gì?

**Format:** `email|password|refresh_token|client_id`

### Ví dụ:
`user@hotmail.com|pass123|M.C548_BAY...|9e5f94bc-e8a4-4e73-b8be-63364c29d753`

### Giải thích:
- **email:** Email Outlook/Hotmail.
- **password:** Password (không dùng cho refresh flow).
- **refresh_token:** Token Microsoft Graph (bắt đầu bằng `M.C...`).
- **client_id:** UUID client ID (36 ký tự).

---

## ❓ Headless là gì?

`Headless` = Chạy browser ẩn (không hiện cửa sổ).

### Ưu điểm:
- ✓ Tiết kiệm tài nguyên.
- ✓ Không làm phiền khi làm việc khác.
- ✓ Chạy nhanh hơn.

### Nhược điểm:
- ✗ Không xem được browser đang làm gì.
- ✗ Khó debug khi có lỗi.

### Khuyến nghị:
- Bật **Headless** khi chạy batch (nhiều jobs).
- Tắt **Headless** khi test hoặc debug.

---

## ❓ Làm sao để dừng tất cả jobs?

- **Trong Web UI:** Click **"■ Stop All"**.
- **Hoặc:** Nhấn **Ctrl+C** trong terminal (để dừng toàn bộ server).

---

## ❓ Làm sao để xóa jobs đã xong?

- **Trong Web UI:** Click **"Clear done"**.

### Lợi ích:
- Giải phóng RAM.
- Giao diện gọn gàng hơn.
- Tránh memory leak.

### Khuyến nghị:
- Clear done sau mỗi 10-20 jobs.
- Backup output trước khi clear.

---

## ❓ Output lưu ở đâu?

**Thư mục:** `runtime/sessions/`

### Files:
- `signup-YYYYMMDD-HHMMSS-email.json` (session + token)
- `signup-YYYYMMDD-HHMMSS-email.2fa.json` (2FA secret)

### Nội dung:
- Session token (để login)
- Access token (để gọi API)
- 2FA secret (để gen TOTP code)
- User ID, Account ID
- Cookies

---

## ❓ Làm sao để gen TOTP code từ secret?

### Lệnh chạy (Command):
```bash
.venv\Scripts\python -m gpt_signup_hybrid totp SECRET_BASE32
```

### Ví dụ:
```bash
.venv\Scripts\python -m gpt_signup_hybrid totp DKDCLDHEHC7PNSSYK3CVF6JPWA6HTDNK
```

### Kết quả (Output):
```json
{
  "code": "863534",
  "valid_for_seconds": 11
}
```

---

## ❓ Web UI không mở được?

### Kiểm tra:
1. **Server có đang chạy không?**
   - Xem terminal có dòng `[web] starting at...`.
2. **Port 8089 có bị chiếm không?**
   - Đổi port: `python -m gpt_signup_hybrid web --port 8090`
3. **Firewall có block không?**
   - Tắt firewall tạm thời để test.
4. **Browser cache?**
   - Ctrl+F5 để refresh.

---

## ❓ Làm sao để update code?

1. **Dừng Web UI:** Nhấn `Ctrl+C` trong terminal.
2. **Pull code mới:**
   ```bash
   git pull
   ```
3. **Update dependencies:**
   ```bash
   .venv\Scripts\pip install --upgrade -r requirements.txt
   ```
4. **Restart Web UI:**
   ```bash
   .\START_WEB_UI.bat
   ```

---

## ❓ Cần hỗ trợ thêm?

### Tài liệu:
- **[QUICK_START.md](QUICK_START.md)** - Hướng dẫn nhanh.
- **[HUONG_DAN_SU_DUNG.md](../HUONG_DAN_SU_DUNG.md)** - Hướng dẫn chi tiết.
- **[GIAI_THICH_QUEUED.md](../GIAI_THICH_QUEUED.md)** - Giải thích trạng thái queued.
- **[README.md](../README.md)** - Documentation đầy đủ.

### Test:
- `test_import.py` - Test imports và config.

### Debug:
- Bật `--har` để capture network requests.
- Xem log trong Web UI.
- Check runtime `outlook_state/*.json`.

---

Chúc bạn sử dụng thành công! 🎉
