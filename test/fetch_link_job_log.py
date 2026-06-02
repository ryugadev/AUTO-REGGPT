import asyncio
import httpx

async def main():
    print("=== DÒNG GHI CHÚ LOG CỦA CÁC JOB GET LINK ===")
    url = "http://127.0.0.1:8089/api/link/jobs"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10.0)
            if resp.status_code != 200:
                print(f"[-] Không thể gọi API: HTTP {resp.status_code}")
                return
            
            data = resp.json()
            jobs = data.get("jobs", [])
            if not jobs:
                print("[-] Không tìm thấy job nào trong bộ nhớ!")
                return
                
            for idx, job in enumerate(jobs):
                print(f"\n[{idx+1}] Job ID: {job.get('id')} | Email: {job.get('email')} | Status: {job.get('status')}")
                # Gọi endpoint lấy chi tiết job
                log_url = f"http://127.0.0.1:8089/api/link/jobs/{job.get('id')}"
                log_resp = await client.get(log_url, timeout=10.0)
                if log_resp.status_code == 200:
                    lines = log_resp.json().get("log_lines", [])
                    print("--- CHI TIẾT LOGS ---")
                    for line in lines:
                        print(f"  {line}")
                else:
                    print("  [-] Không thể lấy chi tiết logs cho job này.")
    except Exception as exc:
        print(f"[-] Lỗi kết nối máy chủ: {exc}")

if __name__ == "__main__":
    asyncio.run(main())
