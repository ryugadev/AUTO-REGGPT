# DANH SÁCH FILE - GPT_SIGNUP_HYBRID

---

## 🌟 FILE QUAN TRỌNG NHẤT (ĐỌC ĐẦU TIÊN)

- **[BAT_DAU_O_DAY.md](BAT_DAU_O_DAY.md)**
  - File này! Hướng dẫn bắt đầu.
  - Đọc đầu tiên để biết nên làm gì.
- **[README_NHANH.md](README_NHANH.md)**
  - Tóm tắt toàn bộ: Lệnh, workflow, troubleshooting.
  - File quan trọng thứ 2, đọc ngay sau BAT_DAU_O_DAY.md.

---

## 🎮 FILE .BAT (DOUBLE-CLICK ĐỂ CHẠY)

- **`START_WEB_UI.bat`**
  - **Mục đích:** Bật Web UI
  - **Khi nào dùng:** Mỗi khi muốn sử dụng tool
  - **Cách dùng:** Double-click
- **`STOP_WEB_UI.bat`**
  - **Mục đích:** Tắt Web UI
  - **Khi nào dùng:** Khi muốn dừng server
  - **Cách dùng:** Double-click
- **`RESTART_WEB_UI.bat`**
  - **Mục đích:** Restart Web UI (tắt rồi bật lại)
  - **Khi nào dùng:** Khi server bị lỗi hoặc cần refresh
  - **Cách dùng:** Double-click
- **`setup.bat`**
  - **Mục đích:** Setup lần đầu
  - **Khi nào dùng:** Đã chạy rồi, không cần chạy lại
  - **Cách dùng:** Double-click (nếu cần setup lại)

---

## 📚 FILE HƯỚNG DẪN (ĐỌC KHI CẦN)

- **[LENH_TAT_BAT.md](LENH_TAT_BAT.md)**
  - **Nội dung:** Hướng dẫn chi tiết cách tắt/bật Web UI.
  - **Khi nào đọc:** Khi không biết cách tắt/bật server.
  - **Độ dài:** Trung bình (~200 dòng).
- **[FAQ.md](FAQ.md)**
  - **Nội dung:** Câu hỏi thường gặp + Giải đáp.
  - **Khi nào đọc:** Khi gặp vấn đề hoặc thắc mắc.
  - **Độ dài:** Trung bình (~150 dòng).
- **[GIAI_THICH_QUEUED.md](../GIAI_THICH_QUEUED.md)**
  - **Nội dung:** Giải thích chi tiết trạng thái "queued".
  - **Khi nào đọc:** Khi job bị queued và muốn hiểu tại sao.
  - **Độ dài:** Dài (~300 dòng).
- **[QUICK_START.md](QUICK_START.md)**
  - **Nội dung:** Quick start guide + Performance metrics.
  - **Khi nào đọc:** Muốn overview nhanh về tool.
  - **Độ dài:** Ngắn (~80 dòng).
- **[HUONG_DAN_SU_DUNG.md](../HUONG_DAN_SU_DUNG.md)**
  - **Nội dung:** Hướng dẫn đầy đủ nhất (Web UI + CLI).
  - **Khi nào đọc:** Muốn biết tất cả tính năng.
  - **Độ dài:** Rất dài (~400 dòng).
- **[README.md](../README.md)**
  - **Nội dung:** Documentation gốc (tiếng Việt).
  - **Khi nào đọc:** Muốn hiểu kiến trúc hệ thống.
  - **Độ dài:** Rất dài (~600 dòng).
- **[DANH_SACH_FILE.md](DANH_SACH_FILE.md)**
  - **Nội dung:** File này! Danh sách tất cả file.
  - **Khi nào đọc:** Muốn biết có file nào.
  - **Độ dài:** Trung bình (~200 dòng).

---

## 🔧 FILE TEST & DEBUG

- **`test_import.py`**
  - **Mục đích:** Test imports và config.
  - **Khi nào dùng:** Kiểm tra môi trường có OK không.
  - **Cách dùng:** `.venv\Scripts\python test_import.py`

---

## ⚙️ FILE CẤU HÌNH

- **`.env`**
  - **Nội dung:** Cấu hình môi trường.
  - **Khi nào sửa:** Muốn thay đổi max_concurrent, timeout, proxy.
  - **Ví dụ:**
    ```ini
    HYBRID_MAX_CONCURRENT=2
    HYBRID_JOB_TIMEOUT=240
    HYBRID_OUTLOOK_PROXY=
    ```

---

## 📂 THƯ MỤC QUAN TRỌNG

- **`.venv/`**
  - **Mục đích:** Python virtual environment.
  - **Nội dung:** Python 3.12 + dependencies.
  - **Không nên:** Xóa hoặc sửa.
- **`runtime/`**
  - **Mục đích:** Thư mục output và state.
  - **Nội dung:**
    - `sessions/`       ← Output JSON files
    - `outlook_state/`  ← Token state tracking
    - `outlook_pool/`   ← Pool combo files (tạo ở đây)
    - `profiles/`       ← Browser profiles
    - `har_hybrid/`     ← HAR debug files
- **`web/`**
  - **Mục đích:** Web UI source code.
  - **Nội dung:**
    - `server.py`       ← FastAPI server
    - `manager.py`      ← Job manager
    - `static/`         ← HTML/CSS/JS

---

## 📊 BẢNG TÓM TẮT - NÊN ĐỌC FILE NÀO?

| Tình huống | Đọc file | Độ ưu tiên |
| :--- | :--- | :--- |
| Lần đầu sử dụng | `BAT_DAU_O_DAY` | ⭐⭐⭐⭐⭐ (Bắt buộc) |
| Muốn tóm tắt nhanh | `README_NHANH` | ⭐⭐⭐⭐⭐ (Bắt buộc) |
| Không biết tắt/bật | `LENH_TAT_BAT` | ⭐⭐⭐⭐ |
| Gặp lỗi/thắc mắc | `FAQ` | ⭐⭐⭐⭐ |
| Job bị queued | `GIAI_THICH_QUEUED` | ⭐⭐⭐ |
| Muốn biết tính năng | `HUONG_DAN_SU_DUNG` | ⭐⭐⭐ |
| Muốn hiểu kiến trúc | `README.md` | ⭐⭐ |
| Quick overview | `QUICK_START` | ⭐⭐ |

---

## 🎯 WORKFLOW ĐỌC FILE (KHUYẾN NGHỊ)

### Lần đầu sử dụng:
1. `BAT_DAU_O_DAY.md` (5 phút)
2. `README_NHANH.md` (10 phút)
3. Bắt đầu sử dụng!

### Khi gặp vấn đề:
1. `FAQ.md` (tìm câu hỏi tương tự)
2. `LENH_TAT_BAT.md` (nếu liên quan tắt/bật)
3. `GIAI_THICH_QUEUED.md` (nếu job queued)

### Muốn hiểu sâu:
1. `HUONG_DAN_SU_DUNG.md` (hướng dẫn đầy đủ)
2. `README.md` (kiến trúc + API)

---

## 💡 TIPS

### ✅ Nên:
- Đọc `BAT_DAU_O_DAY.md` trước.
- Đọc `README_NHANH.md` để hiểu tổng quan.
- Bookmark `FAQ.md` để tra cứu nhanh.
- Tạo shortcut `START_WEB_UI.bat` trên Desktop.

### ❌ Không nên:
- Đọc `README.md` đầu tiên (quá dài, dễ overwhelm).
- Bỏ qua `BAT_DAU_O_DAY.md`.
- Đọc tất cả file một lúc.

---

## 🔍 TÌM KIẾM NHANH

| Muốn biết | Đọc file |
| :--- | :--- |
| Cách bật/tắt Web UI | `LENH_TAT_BAT.md` |
| Job bị queued | `GIAI_THICH_QUEUED.md` |
| Lỗi phổ biến | `FAQ.md` |
| Format combo | `README_NHANH.md` |
| Output ở đâu | `README_NHANH.md` |
| Cách dùng CLI | `HUONG_DAN_SU_DUNG.md` |
| Kiến trúc hệ thống | `README.md` |
| Performance metrics | `QUICK_START.md` |
| Cấu hình nâng cao | `HUONG_DAN_SU_DUNG.md` |
| Troubleshooting | `FAQ.md` |

---

## 📞 CẦN TRỢ GIÚP?

Đọc theo thứ tự:
1. `BAT_DAU_O_DAY.md`
2. `README_NHANH.md`
3. `FAQ.md`
4. File liên quan đến vấn đề cụ thể

Vẫn không giải quyết được?
- Test môi trường: `.venv\Scripts\python test_import.py`
- Xem log trong Web UI
- Check file `runtime/outlook_state/*.json`

---

Chúc bạn sử dụng thành công! 🎉

*Nhớ: Bắt đầu với BAT_DAU_O_DAY.md!*
