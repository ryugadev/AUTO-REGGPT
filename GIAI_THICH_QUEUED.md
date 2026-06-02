# 🔍 GIẢI THÍCH TRẠNG THÁI "QUEUED"

## ❓ "Queued" là gì?

**Queued** = **Đang chờ trong hàng đợi** để được xử lý.

Đây là trạng thái **BÌNH THƯỜNG**, không phải lỗi!

---

## 📊 Các trạng thái của Job

```
queued 🟡  →  running 🔵  →  success 🟢
                          ↘  error 🔴
                          ↘  cancelled ⚫
```

1. **queued** 🟡 - Đang chờ trong hàng đợi
2. **running** 🔵 - Đang chạy (browser đang hoạt động)
3. **success** 🟢 - Hoàn thành thành công
4. **error** 🔴 - Gặp lỗi
5. **cancelled** ⚫ - Đã bị hủy

---

## 🎯 Tại sao job bị "queued"?

### **Lý do 1: Giới hạn số job chạy đồng thời** ⭐ (Phổ biến nhất)

Web UI sử dụng **Worker Pool Pattern** để kiểm soát số lượng job chạy cùng lúc:

#### **Mode Single** (mặc định):
```
Max concurrent: 1 job
├─ Job 1: running 🔵
├─ Job 2: queued 🟡 ← Chờ Job 1 xong
├─ Job 3: queued 🟡 ← Chờ Job 1, 2 xong
└─ Job 4: queued 🟡 ← Chờ Job 1, 2, 3 xong
```

#### **Mode Multi**:
```
Max concurrent: 3 jobs (có thể điều chỉnh trong .env)
├─ Job 1: running 🔵
├─ Job 2: running 🔵
├─ Job 3: running 🔵
├─ Job 4: queued 🟡 ← Chờ 1 trong 3 job trên xong
└─ Job 5: queued 🟡 ← Chờ tiếp
```

**Tại sao giới hạn?**
- Mỗi job mở 1 browser (Camoufox) → tốn RAM (~500MB/browser)
- Chạy quá nhiều job cùng lúc → máy lag, browser crash
- OpenAI có thể phát hiện nhiều request từ cùng IP → block

---

### **Lý do 2: Stagger delay (chống spam)**

Khi chạy Multi mode, hệ thống có cơ chế **stagger** (trì hoãn) giữa các job:

```python
# Trong code manager.py
_stagger_min_seconds = 5.0   # Tối thiểu 5s giữa 2 job
_stagger_max_seconds = 10.0  # Tối đa 10s (random)
```

**Ví dụ:**
```
00:00 - Job 1 bắt đầu running
00:07 - Job 2 bắt đầu running (đợi 7s)
00:15 - Job 3 bắt đầu running (đợi 8s)
```

**Tại sao cần stagger?**
- Tránh nhiều browser khởi động cùng lúc → giảm tải CPU
- Tránh OpenAI phát hiện pattern spam
- Tăng success rate

---

### **Lý do 3: Job vừa mới được thêm vào**

Khi bạn click "▶ Chạy":
1. Jobs được tạo với trạng thái `queued`
2. Được đưa vào queue (hàng đợi)
3. Worker sẽ lấy job ra và chuyển sang `running`

**Timeline:**
```
[0s]  Click "Chạy" → Job created (queued)
[1s]  Worker pick job → Job running
[30s] Job hoàn thành → Job success
```

---

## ⚙️ Cấu hình Max Concurrent

### **Trong Web UI:**
```
Mode dropdown:
- Single: 1 job/lần
- Multi: 3 jobs song song (mặc định)
```

### **Trong file .env:**
```env
# Điều chỉnh số job chạy đồng thời (1-10)
HYBRID_MAX_CONCURRENT=2

# Timeout mỗi job (giây)
HYBRID_JOB_TIMEOUT=240

# Stagger delay (giây)
# Không có trong .env, phải sửa code manager.py
```

### **Khuyến nghị:**
```
RAM 8GB:  max_concurrent = 1-2
RAM 16GB: max_concurrent = 2-3
RAM 32GB: max_concurrent = 3-5
```

---

## 🔧 Cách xử lý khi job "queued" lâu

### **1. Kiểm tra có job nào đang running không**
Trong Web UI, xem panel **Jobs**:
- Nếu có job `running` → Đợi job đó xong
- Nếu không có job `running` → Có thể bị lỗi

### **2. Kiểm tra log**
Click vào job `queued` → Xem log panel:
```
[12:34:56] [stagger] đợi 7.3s trước khi start
```
→ Job đang đợi stagger delay, sẽ chạy sau vài giây

### **3. Tăng max_concurrent**
Nếu muốn chạy nhiều job hơn:
1. Đổi Mode từ **Single** → **Multi**
2. Hoặc sửa `.env`:
   ```env
   HYBRID_MAX_CONCURRENT=5
   ```
3. Restart Web UI

### **4. Cancel job không cần thiết**
Nếu có quá nhiều job `queued`:
- Click **■ Stop All** để hủy tất cả
- Hoặc click vào từng job → Delete

### **5. Clear done jobs**
Sau khi jobs hoàn thành:
- Click **Clear done** để giải phóng RAM
- Jobs `success`/`error` sẽ bị xóa khỏi memory

---

## 📈 Monitoring Queue

### **Trong Web UI:**
```
Jobs panel header:
"15 total | 3 running | 8 queued | 4 success"
```

### **Trong code (manager.py):**
```python
# Xem queue size
queue_size = manager._job_queue.qsize()

# Xem số worker đang chạy
num_workers = len(manager._workers)

# Xem max concurrent
max_concurrent = manager.max_concurrent
```

---

## 💡 Tips để tối ưu

### **1. Batch processing hiệu quả:**
```
✅ Tốt: Paste 10 combo → Chạy Multi mode
❌ Tệ: Paste 100 combo → Chạy Single mode (mất nhiều giờ)
```

### **2. Sử dụng pool:**
```bash
# Tạo pool file với nhiều combo
notepad runtime\outlook_pool\batch.txt

# Chạy từng batch nhỏ (10-20 combo/lần)
# Tránh paste quá nhiều combo 1 lúc
```

### **3. Monitor RAM:**
```
Task Manager → Performance → Memory
Nếu RAM > 90% → Giảm max_concurrent
```

### **4. Clear done thường xuyên:**
```
Sau mỗi 10-20 jobs success → Click "Clear done"
→ Giải phóng RAM, tránh memory leak
```

---

## 🐛 Troubleshooting

### **Job queued mãi không chạy:**
```
Nguyên nhân: Worker bị crash hoặc stuck
Giải pháp:
1. Click "■ Stop All"
2. Restart Web UI (Ctrl+C → Chạy lại)
3. Paste lại combo
```

### **Job queued → running → queued lại:**
```
Nguyên nhân: Job bị retry tự động
Giải pháp: Xem log để biết lý do retry
```

### **Tất cả jobs đều queued, không có running:**
```
Nguyên nhân: Worker pool chưa khởi động
Giải pháp:
1. Đợi 5-10s
2. Nếu vẫn không chạy → Restart Web UI
```

---

## 📊 Performance Metrics

### **Thời gian trung bình:**
```
queued → running:  1-10s (tùy stagger)
running → success: 25-35s (signup + 2FA)
Total per job:     30-45s
```

### **Throughput:**
```
Single mode: ~2-3 jobs/phút
Multi (3):   ~5-6 jobs/phút
Multi (5):   ~8-10 jobs/phút
```

---

## 🎓 Kết luận

**"Queued" là trạng thái bình thường**, không phải lỗi!

✅ **Bình thường:**
- Job queued vài giây → running
- Có nhiều jobs queued khi chạy batch

❌ **Bất thường:**
- Job queued > 1 phút mà không chạy
- Tất cả jobs queued, không có running

**Giải pháp:** Đợi hoặc restart Web UI nếu stuck.

---

**Chúc bạn sử dụng thành công! 🎉**
