# gpt_signup_hybrid

Module signup ChatGPT tự động dùng **Camoufox + curl_cffi**.

- **Camoufox** đi qua flow signup thật (click, type tên, type tuổi, set password) — Sentinel SDK collect đủ data → bypass anti-abuse.
- **curl_cffi** chỉ làm việc nhẹ ở Phase 2: extract session-token + gọi `/api/auth/session` để lấy access_token.
- **Auto enable 2FA** (TOTP) sau khi signup → output `email|password|secret_2fa`.

Avg ~35s/account (có password), success rate 100%.

---

## 1. Setup — 1 lệnh

### macOS / Linux

```bash
bash gpt_signup_hybrid/setup.sh
```

### Windows

Double-click `setup.bat` hoặc:

```cmd
cd gpt_signup_hybrid
setup.bat
```

Script tự động:
1. Tạo Python venv (`.venv`).
2. Install dependencies: `pydantic typer httpx curl_cffi pyotp fastapi uvicorn camoufox playwright`.
3. Install Playwright Firefox browser.
4. Fetch Camoufox binary.
5. Tạo `.env` mặc định.
6. Tạo thư mục `runtime/`.
7. **Start web UI** tại `http://127.0.0.1:8089/`.

### Yêu cầu

- Python 3.11+ (recommend 3.12).
- macOS hoặc Windows (Linux cần Xvfb cho headless Camoufox).
- Internet connection.

### Chạy lại (đã setup)

```bash
# macOS/Linux
.venv/bin/python -m gpt_signup_hybrid web

# Windows
.venv\Scripts\python -m gpt_signup_hybrid web
```

---

## 2. Quick start

### Web UI (recommend)

```bash
bash gpt_signup_hybrid/setup.sh
# → http://127.0.0.1:8089/
```

1. Paste combo Outlook vào textarea (mỗi dòng 1 combo `email|password|refresh_token|client_id`).
2. (Optional) Set "Password mặc định" — để trống thì random 12 ký tự.
3. (Optional) Set "Timeout" — mặc định 120s/job.
4. Chọn Mode: Single (1 job) / Multi (max 3 song song).
5. Headless: bật = ẩn browser, tắt = xem trực tiếp.
6. Click **▶ Chạy**.
7. Xem progress realtime ở panel Jobs + Log.
8. Success output: `email|password|secret_2fa` — copy all.
9. **■ Stop All** dừng tất cả. **Clear done** giải phóng RAM.

### CLI

### Mode A — iCloud mail qua Worker `icloud-cf-mail`

Email `*@icloud.com` được forward về Cloudflare Worker (cấu hình mặc định trong CLI):

```bash
.venv/bin/python -m gpt_signup_hybrid signup --email foo@icloud.com
```

Default Worker URL = `https://icloud-cf-mail.n5pskgzs9g.workers.dev/logs`, key = `12345678@`.

### Mode B — Outlook/Hotmail combo (Microsoft Graph)

Mỗi combo có format `email|password|refresh_token|client_id`:

```text
benjaminreiddavis8195@hotmail.com|benjamin@669178|M.C524_BL2.0...|9e5f94bc-e8a4-4e73-b8be-63364c29d753
```

Chạy 1 combo (qua file để tránh leak shell history):

```bash
echo 'mail|pass|M.C...|9e5f94bc-...' > runtime/outlook_pool/single.txt
.venv/bin/python -m gpt_signup_hybrid signup --outlook-combo-file runtime/outlook_pool/single.txt
```

### Mode C — Pool nhiều combo (recommend cho batch)

```bash
# Pool format: 1 combo / dòng. Comment bằng #.
cat > runtime/outlook_pool/batch.txt <<EOF
mail1@hotmail.com|pwd1|M.C548_BAY...|9e5f94bc-e8a4-4e73-b8be-63364c29d753
mail2@outlook.com|pwd2|M.C525_BAY...|9e5f94bc-e8a4-4e73-b8be-63364c29d753
mail3@hotmail.com|pwd3|M.C530_BL2...|9e5f94bc-e8a4-4e73-b8be-63364c29d753
EOF

# Chạy: pool tự pick combo còn khả dụng, mark used sau khi success.
.venv/bin/python -m gpt_signup_hybrid signup --outlook-pool runtime/outlook_pool/batch.txt
```

Chạy lệnh tiếp theo sẽ pick combo kế tiếp:

```bash
.venv/bin/python -m gpt_signup_hybrid signup --outlook-pool runtime/outlook_pool/batch.txt
```

Xem status pool:

```bash
.venv/bin/python -m gpt_signup_hybrid pool-status runtime/outlook_pool/batch.txt
# {"total": 3, "used_for_signup": 1, "available": 2, "terminal_error": 0}
```

---

## 3. CLI options

```text
.venv/bin/python -m gpt_signup_hybrid signup [OPTIONS]
```

| Option | Default | Mô tả |
|---|---|---|
| `--email` | (auto từ combo) | Email đăng ký. Tự derive từ phần đầu Outlook combo. |
| `--name` | `ChatGPT User` | Tên hiển thị (input form `/about-you`). |
| `--birthdate` | `2000-01-01` | YYYY-MM-DD, dùng để compute age. |
| `--smail` | `--email` | Mailbox poll OTP (nếu khác email form). |
| `--mail-provider` | auto | `worker` / `outlook`. Auto-detect: `outlook` nếu có combo, ngược lại `worker`. |
| `--logs-url` | `https://icloud-cf-mail.n5pskgzs9g.workers.dev/logs` | [worker] Worker logs API. |
| `--api-key` | `12345678@` | [worker] Bearer cho Worker. |
| `--insecure-tls/--secure-tls` | bật | [worker] Bỏ verify TLS (host có `_`). |
| `--outlook-combo` | `null` | [outlook] Combo inline (không recommend, lộ shell history). |
| `--outlook-combo-file` | `null` | [outlook] File chứa 1 combo. |
| `--outlook-pool` | `null` | [outlook] File pool nhiều combo, auto pick. |
| `--headless/--headed` | `--headed` | Camoufox visible / hidden. |
| `--off-font` | tắt | Tắt camoufox font randomization (fix hex glyph box). |
| `--profile-template/--fresh-profile` | bật | Clone `runtime/profiles/camoufox_template`. |
| `--proxy` | `null` | HTTP/HTTPS proxy cho Phase 1 + Phase 2. |
| `--otp-timeout` | `180.0` | Hard deadline đợi OTP (giây). |
| `--otp-interval` | `4.0` | Gap giữa 2 lần poll. |
| `--sentinel-timeout` | `30.0` | Timeout đợi OTP form ready trên `/email-verification`. |
| `--har/--no-har` | tắt | Bật HAR capture Phase 1 cho debug. Output `runtime/har_hybrid/<ts>.har`. |
| `--output, -o` | `runtime/sessions/signup-<ts>-<email>.json` | Output JSON path. |

### 3.1 Subcommand `totp` — gen TOTP code

Gen 6-digit code từ secret base32 (lấy từ `enable-2fa` hoặc nhập tay từ Authenticator app):

```bash
.venv/bin/python -m gpt_signup_hybrid totp <SECRET>
.venv/bin/python -m gpt_signup_hybrid totp DKDCLDHEHC7PNSSYK3CVF6JPWA6HTDNK
# {
#   "code": "863534",
#   "valid_for_seconds": 11
# }
```

Có account để gen `otpauth://` URI cho QR code:
```bash
.venv/bin/python -m gpt_signup_hybrid totp <SECRET> --account foo@hotmail.com
```

### 3.2 Subcommand `enable-2fa` — bật 2FA cho account

Cần `access_token` từ SignupResult JSON. Flow: `POST /mfa/enroll` (lấy secret) → `POST /mfa/user/activate_enrollment` (verify với code TOTP).

```bash
.venv/bin/python -m gpt_signup_hybrid enable-2fa \
  -f runtime/sessions/signup-20260519-115540-foo_at_hotmail.com.json
```

Output `<session-file>.2fa.json`:
```json
{
  "email": "foo@hotmail.com",
  "two_factor": {
    "secret": "DKDCLDHEHC7PNSSYK3CVF6JPWA6HTDNK",
    "factor_id": "6a0bedbc94f48191be17",
    "session_id": "...",
    "first_code": "863534",
    "activated": true,
    "provisioning_uri": "otpauth://totp/ChatGPT?secret=DKDCLDHEHC7PNSSYK3CVF6JPWA6HTDNK&issuer=ChatGPT",
    "mfa_info": { "mfa_enabled": true, ... }
  }
}
```

Options:
- `--enroll-only` — chỉ lấy secret, không activate (để mày tự confirm sau qua UI).
- `--proxy` — HTTP/HTTPS proxy.
- `--output / -o` — custom path output.

### 3.3 Web UI — `python -m gpt_signup_hybrid web`

Server FastAPI nhỏ gọn (no auth, dùng local) cho batch signup + 2FA qua browser:

```bash
.venv/bin/python -m gpt_signup_hybrid web
# [web] starting at http://127.0.0.1:8089/
```

Open `http://127.0.0.1:8089/` trong browser:

- **Textarea paste combo** (nhiều dòng `email|pass|refresh|client_id`).
- **Job list** — mỗi job có status (queued/running/success/error) + nút retry / xoá.
- **Log panel** — click 1 job để xem log realtime.
- **Success output** — format `email|secret|first_code` mỗi dòng, copy all.
- **Error output** — list email lỗi + reason.
- **Mode** — Single (1 job/lần) / Multi (max 3 song song).
- **Headless toggle** — bật để ẩn cửa sổ Camoufox (chạy nền), tắt để xem trực tiếp browser thao tác.

Click 1 job → log realtime hiển thị bên dưới. Xoá job khỏi list → cũng xoá khỏi textarea (theo email).

Backend API (REST):

| Method | Path | Mô tả |
|---|---|---|
| GET | `/api/jobs` | List jobs + max_concurrent. |
| POST | `/api/jobs` | Body `{"combos": "..."}` — add jobs từ textarea. |
| GET | `/api/jobs/<id>` | Detail job. |
| GET | `/api/jobs/<id>/log` | Toàn bộ log lines. |
| POST | `/api/jobs/<id>/retry` | Reset state + chạy lại. |
| DELETE | `/api/jobs/<id>` | Cancel + xoá. |
| GET | `/api/config` | `{max_concurrent, headless}`. |
| POST | `/api/config` | Body `{"max_concurrent": 1\|3, "headless": true\|false}` (cả 2 đều optional). |
| GET | `/api/events` | SSE stream (snapshot + job updates + log lines). |

Options `web` command:

```bash
.venv/bin/python -m gpt_signup_hybrid web --host 0.0.0.0 --port 8089
.venv/bin/python -m gpt_signup_hybrid web --reload    # dev hot-reload
```



---

## 4. Pool management — chi tiết

### 4.1 Format pool file

```text
# Comment dòng đầu (#)
email1@hotmail.com|password1|refresh_token_1|client_id_1
email2@outlook.com|password2|refresh_token_2|client_id_2
```

- 1 combo / dòng. Phải có đủ 4 phần phân cách `|`.
- `client_id` Outlook desktop: `8b4ba9dd-3ea5-4e5f-86f1-ddba2230dcf2`.
- `client_id` Outlook mobile: `9e5f94bc-e8a4-4e73-b8be-63364c29d753` (test cả 2 đều work cho Graph API).
- Email trùng trong cùng pool sẽ bị reject.

### 4.2 State tracker

Mỗi combo có 1 state file `runtime/outlook_state/<email>.json`:

```json
{
  "email": "...",
  "client_id": "9e5f94bc-...",
  "refresh_token": "M.C...",
  "last_refresh_at": "2026-05-19T03:30:00+00:00",
  "expires_in": 3599,
  "scope": "https://graph.microsoft.com/.default ...",
  "used_for_signup": true,
  "used_at": "2026-05-19T03:35:00+00:00"
}
```

- `used_for_signup: true` → pool skip lần sau.
- `last_error` chứa terminal pattern → pool skip:
  - `registration_disallowed` — OpenAI block.
  - `invalid_grant` — refresh_token chết.
  - `AADSTS50173` / `AADSTS70008` — token revoked/expired.

Token rotate sau mỗi lần refresh — runner persist vào state file. **Không xoá state file** vì lần sau dùng combo gốc sẽ bị `invalid_grant`.

### 4.3 Selection logic

```python
for combo in pool:
    state = read_state(combo.email)
    if state.get("used_for_signup"):
        skip
    if state.get("last_error") matches TERMINAL_ERRORS:
        skip
    # Hydrate refresh_token mới nhất từ state
    yield combo
```

Pool yield combo đầu tiên còn dùng được. Nếu hết → exit 1 với message rõ ràng.

### 4.4 Sau khi run

- Success → `mark_signup_success` → `used_for_signup: true` + clear `last_error`.
- Fail terminal (registration_disallowed, invalid_grant) → `mark_signup_failure` ghi `last_error` → skip lần sau.
- Fail transient (timeout, network) → cũng ghi `last_error` nhưng không match terminal pattern → vẫn được retry lần sau.

---

## 5. Architecture

```
gpt_signup_hybrid/
├── __init__.py          # exports public API
├── __main__.py          # python -m gpt_signup_hybrid → CLI
├── cli.py               # typer CLI: signup_cmd, pool_status_cmd, totp_cmd, enable_2fa_cmd, web_cmd
├── config.py            # reuse signup_runner.Settings (đọc .env)
├── models.py            # SignupRequest, SignupResult, BrowserHandoff
├── mail_providers.py    # WorkerMailProvider + OutlookMailProvider
├── outlook_pool.py      # parse pool, pick combo, mark state
├── browser_phase.py     # Phase 1 — Camoufox flow (chính)
├── http_phase.py        # Phase 2 — extract session-token + access_token
├── mfa_phase.py         # Enable 2FA TOTP qua /mfa/enroll + /mfa/activate
├── totp_helper.py       # Gen 6-digit code từ secret base32 (pyotp)
├── signup.py            # orchestrator
└── web/                 # FastAPI web UI
    ├── __init__.py
    ├── server.py        # API endpoints + SSE stream
    ├── manager.py       # JobManager: queue + concurrency + broadcast
    └── static/
        ├── index.html
        ├── style.css
        └── app.js
```

### 5.1 Phase 1 — Camoufox (~25-30s)

1. **Bootstrap NextAuth** (~3s): `goto chatgpt.com/` → `fetch /api/auth/csrf` → `POST /api/auth/signin/openai?login_hint=<email>` → trả URL `auth.openai.com/api/accounts/authorize?...&state=...`.
2. **Goto authorize URL** (~2s): server set ~10 cookies session, redirect `/email-verification`. **Server tự gửi OTP qua mail lúc này.**
3. **Đợi OTP form ready** (~1s): selector `input[name="code"]`.
4. **Poll OTP** (~2-10s) qua `MailProvider`:
   - Worker (icloud): GET Worker logs với Bearer header.
   - Outlook: refresh access_token → Graph API GET `/me/messages` (Inbox + Junk Email folder) → regex 6-digit code, filter sender chứa `openai.com`.
5. **Type OTP + click submit** (~1s).
6. **Branch**:
   - **signup**: navigate `/about-you` → fill form name + age (force click vì label che) → click submit (~6s).
   - **login** (account đã reg): navigate thẳng về callback URL.
7. **Capture callback URL** từ ctx-level request listener (`chatgpt.com/api/auth/callback/openai?code=..&state=..`).
8. **Đợi NextAuth process callback** (~3-5s): cookies `__Secure-next-auth.session-token` (chunked thành `.0`/`.1`) + `_account` xuất hiện.
9. **Exfil cookies + đóng browser**.

### 5.2 Phase 2 — curl_cffi (~0.2s)

1. Extract cookies chatgpt.com từ handoff:
   - `__Secure-next-auth.session-token` (single) hoặc `.0`/`.1` (chunked) → ghép lại.
   - `_account` → account_id.
2. Build curl_cffi Session impersonate Firefox 135, inject cookies.
3. GET `chatgpt.com/api/auth/session` → access_token JWT + user.id.

### 5.3 Mail providers

#### `WorkerMailProvider`

- GET `<logs_url>?mail=<email>` với header `Authorization: Bearer <api_key>`.
- Parse JSON response (list trực tiếp hoặc `{messages|items|logs|emails|data: [...]}`).
- Filter messages mới hơn `started_at`, regex 6 digits.

#### `OutlookMailProvider`

- POST `login.microsoftonline.com/consumers/oauth2/v2.0/token` với `grant_type=refresh_token` → access_token + new refresh_token.
- Persist token mới ra `runtime/outlook_state/<email>.json`.
- GET `graph.microsoft.com/v1.0/me/mailFolders?$filter=displayName eq 'Inbox'` → folder ID.
- GET `me/mailFolders/<id>/messages?$top=10&$orderby=receivedDateTime desc&$select=...`.
- Lặp lại folder `Junk Email` (mail OpenAI thi thoảng vào spam).
- Filter: chỉ accept sender chứa `openai.com` (hoặc subject chứa `openai`) để tránh nhặt nhầm OTP từ Microsoft.

---

## 6. Output JSON

`runtime/sessions/signup-<ts>-<email>.json`:

```json
{
  "success": true,
  "email": "calumbrooksjebp@outlook.com",
  "user_id": "user-yfNPJmidFXvIHbKYELyqHyDh",
  "account_id": "957d5570-ddd2-42b1-9faf-6eddc0beef3a",
  "session_token": "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..xxx",
  "access_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjE5MzQ0..yyy",
  "cookies": [
    {"name": "_account", "value": "...", "domain": "chatgpt.com", "path": "/", "secure": false},
    {"name": "__Secure-next-auth.session-token.0", "value": "...", "domain": ".chatgpt.com", "path": "/", "secure": true},
    {"name": "__Secure-next-auth.session-token.1", "value": "...", "domain": ".chatgpt.com", "path": "/", "secure": true},
    {"name": "__Secure-oai-is", "value": "...", "domain": ".chatgpt.com", "path": "/", "secure": true}
  ],
  "phase1_seconds": 28.73,
  "phase2_seconds": 0.22,
  "otp_seconds":   6.78,
  "error": null
}
```

Field quan trọng:
- `session_token` — `__Secure-next-auth.session-token` JWT (NextAuth). Nếu chunked, runner tự ghép `.0` + `.1`.
- `access_token` — Bearer JWT cho `/backend-api/`.
- `cookies` — list cookies chatgpt.com dạng Playwright dict, inject vào browser khác để dùng tiếp.

---

## 7. Dùng output

### 7.1 Inject session vào Playwright

```python
import json
from playwright.async_api import async_playwright

data = json.load(open("runtime/sessions/signup-xxx.json"))
async with async_playwright() as pw:
    browser = await pw.firefox.launch(headless=False)
    ctx = await browser.new_context()
    await ctx.add_cookies(data["cookies"])
    page = await ctx.new_page()
    await page.goto("https://chatgpt.com/")  # đã login sẵn
```

### 7.2 Gọi `/backend-api/` bằng access_token

```python
import json, httpx
data = json.load(open("runtime/sessions/signup-xxx.json"))
headers = {"Authorization": f"Bearer {data['access_token']}"}
r = httpx.get("https://chatgpt.com/backend-api/me", headers=headers)
print(r.json())
```

### 7.3 Đẩy sang `signup_runner.checkout_api`

```bash
.venv/bin/python -m signup_runner checkout-api \
  --access-token "$(jq -r .access_token runtime/sessions/signup-xxx.json)" \
  --session-token "$(jq -r .session_token runtime/sessions/signup-xxx.json)" \
  --billing-email "$(jq -r .email runtime/sessions/signup-xxx.json)" \
  --billing-name "ChatGPT User"
```

---

## 8. Failure modes & debug

### 8.1 Phase 1 timeout đến `/email-verification`

```
BrowserPhaseError: không đến được /email-verification: ...
```

Nguyên nhân:
- IP bị Cloudflare bounce → đổi proxy / network khác.
- Profile template bị poison cookies cũ → `--fresh-profile`.
- Camoufox font glyph hex → `--off-font`.

### 8.2 OTP timeout

```
TimeoutError: OTP timeout after 180s for ...
```

#### Worker:
- Email không có forwarder vào Worker. Test thủ công:
  ```bash
  curl -H 'Authorization: Bearer 12345678@' \
    'https://icloud-cf-mail.n5pskgzs9g.workers.dev/logs?mail=foo@icloud.com'
  ```

#### Outlook:
- Combo expire (refresh_token chết). Verify:
  ```bash
  .venv/bin/python -c "import httpx; r = httpx.post('https://login.microsoftonline.com/consumers/oauth2/v2.0/token', data={'client_id':'9e5f94bc-e8a4-4e73-b8be-63364c29d753','scope':'https://graph.microsoft.com/.default offline_access','refresh_token':'M.C...','grant_type':'refresh_token'}); print(r.status_code, r.text[:200])"
  ```
- Mail OpenAI vào folder khác Inbox/Junk Email. Tao chỉ check 2 folder này.

### 8.3 Phase 1 fail ở `/about-you`: `registration_disallowed`

```
HttpPhaseError: create_account failed: HTTP 400 registration_disallowed
```

Sentinel SDK detect form không có user interaction. Đây là bug cũ, hiện đã fix bằng cách type tên + tuổi vào form thật. Nếu vẫn gặp:
- IP đã trigger anti-abuse — đổi proxy.
- Email/domain blacklist — đổi combo.

### 8.4 Phase 1 fail: timeout đợi `/about-you` sau OTP

```
BrowserPhaseError: không đến được /about-you sau khi submit OTP
```

OTP sai hoặc đã expire. Chạy lại từ đầu (server gửi OTP mới).

### 8.5 Phase 1 fail: timeout `__Secure-next-auth.session-token`

```
BrowserPhaseError: timeout 30.0s waiting __Secure-next-auth.session-token
```

NextAuth callback xử lý chậm hoặc bị Cloudflare challenge. Tăng `--sentinel-timeout` hoặc retry.

### 8.6 Outlook combo: `invalid_grant`

```
OutlookComboError: refresh failed HTTP 400: {"error":"invalid_grant",...}
```

`refresh_token` cũ đã rotate. State file `runtime/outlook_state/<email>.json` lưu token mới nhất — nếu file mất hoặc đã reset, phải xin combo mới.

### 8.7 Bật HAR debug

```bash
.venv/bin/python -m gpt_signup_hybrid signup --outlook-pool runtime/outlook_pool/batch.txt --har
```

HAR lưu vào `runtime/har_hybrid/hybrid-<ts>.har`. Phân tích:

```bash
.venv/bin/python -m signup_runner parse-har runtime/har_hybrid/hybrid-xxx.har --domain auth.openai.com
```

---

## 9. Performance

### 9.1 Timing breakdown (avg trên 5 combo @hotmail.com)

| Stage | Duration | Note |
|---|---|---|
| Camoufox cold start | 2-3s | Profile clone + browser launch |
| chatgpt.com load + bootstrap | 3-4s | NextAuth csrf + signin + redirect |
| Goto authorize → /email-verification | 2-3s | Cloudflare challenge + Sentinel iframe |
| Đợi OTP form ready | <1s | |
| Poll OTP | 2-10s | Outlook Graph API ~6s, Worker icloud <1s |
| Type OTP + submit + nav /about-you | 1-2s | |
| Sentinel SDK fire `oai-sc` cookie | <1s | |
| Fill name + age + click submit | 4-5s | Form render delay |
| Capture callback URL + đợi session-token | 3-5s | NextAuth process |
| Phase 2 (curl_cffi) | 0.2s | Extract + GET /api/auth/session |
| **Total** | **~25-30s** | |

### 9.2 Tối ưu đã apply

| Tối ưu | Tiết kiệm |
|---|---|
| Bỏ `_simulate_user_activity(11s)` (form interactions ở `/about-you` đã đủ data Sentinel) | -11s |
| Bỏ `wait_for(mouse_task, 3s)` sau OTP | -3s |
| `sleep` sau type name 0.4s → 0.2s | -0.2s |
| `sleep` trước submit form 0.8s → 0.3s | -0.5s |
| `sleep` sau session ready 2s → 0.3s | -1.7s |

### 9.3 Không thể tối ưu thêm

- Camoufox cold start ~2s (mỗi run launch Firefox profile riêng).
- Cloudflare challenge ~2s mỗi cross-domain navigation.
- React render `/about-you` form ~3-4s (delay bên client OpenAI).
- NextAuth callback xử lý ~3-5s (server-side).

---

## 10. So sánh với `signup_runner` (full Camoufox)

| | `gpt_signup_hybrid` | `signup_runner` |
|---|---|---|
| Tốc độ trung bình | **~27s** | 25-30s |
| Setup phức tạp | Vừa (cần combo Outlook hoặc Worker) | Vừa (cần Worker) |
| Browser thời lượng | ~25s | ~25s |
| Stable khi OpenAI patch SDK | ✅ (browser tự xử Sentinel) | ✅ |
| Có Codex device-auth export | ❌ | ✅ |
| Có flow Trial/Payment | ❌ | ✅ |
| Pool combo Outlook | ✅ | ❌ |
| Outlook/Hotmail mailbox | ✅ | ❌ (chỉ Worker icloud-cf-mail) |
| Phù hợp dùng khi | Batch signup mass với combo Outlook | Production cần trial/payment |

Hai module **không thay thế nhau** mà bổ sung. Hybrid mạnh ở batch + Outlook combo. Signup_runner mạnh ở flow trial/payment + Codex auth.

---

## 11. Limitations đã biết

1. **Không refresh access_token tự động** — JWT expire sau ~10 ngày. Phải re-auth.
2. **Cloudflare clearance ngắn hạn** — cookie `cf_clearance` valid ~30 phút. Không reuse handoff cho lần khác.
3. **Phụ thuộc Worker icloud-cf-mail** (mode A) — Worker down thì OTP poll fail.
4. **OpenAI rate-limit per IP** — không nên >5 signup/giờ trên 1 IP. Dùng proxy rotate.
5. **Outlook không support sub-address** (`+`) — mỗi combo gắn 1 email duy nhất, không thể alias.
6. **Refresh_token rotate sau mỗi call** — phải persist state, không reuse combo gốc.
7. **`oai-sc` cookie chỉ set sau khi browser load `/about-you`** — Phase 2 không thể replay create_account thuần HTTP, phải dùng browser cho toàn bộ Phase 1.
8. **Tuổi tự compute từ birthdate** — runner dùng `2000-01-01` default → age = 25/26 (tuỳ năm hiện tại). Nếu cần age cụ thể, override `--birthdate`.

---

## 12. Workflow điển hình

```bash
# 1. Tạo pool file 10 combo
cat > runtime/outlook_pool/oct2026.txt <<EOF
mail1@hotmail.com|pwd1|M.C548...|9e5f94bc-...
mail2@outlook.com|pwd2|M.C525...|9e5f94bc-...
...
mail10@hotmail.com|pwd10|M.C530...|9e5f94bc-...
EOF

# 2. Check status pool
.venv/bin/python -m gpt_signup_hybrid pool-status runtime/outlook_pool/oct2026.txt

# 3. Chạy 10 lần, mỗi lần pool tự pick combo kế tiếp
for i in {1..10}; do
  .venv/bin/python -m gpt_signup_hybrid signup --outlook-pool runtime/outlook_pool/oct2026.txt
  sleep 3   # đợi 3s giữa các signup để giảm rate-limit
done

# 4. Output ở runtime/sessions/signup-*.json
ls runtime/sessions/

# 5. Pool status: 10 used + 0 available
.venv/bin/python -m gpt_signup_hybrid pool-status runtime/outlook_pool/oct2026.txt

# 6. Inject session đầu tiên vào browser khác để verify
.venv/bin/python -m signup_runner check-auth \
  --path runtime/sessions/signup-<ts>-<email>.json --kind any
```

---

## 13. Roadmap

- [ ] Loop tự động qua pool (`--loop N`) thay vì gọi nhiều lần.
- [ ] Retry tự động với combo khác khi gặp transient error.
- [ ] FastAPI server tương tự `signup_runner.api`.
- [ ] Auto-detect form layout `/about-you` (date picker vs age input) qua React props.
- [ ] Convert output sang format `session.json` mà `signup_runner.checkout_api` đọc trực tiếp.
- [ ] Support GMail combo qua App Password / OAuth.

---

## 14. Test results

Test thực tế ngày 2026-05-19 trên 5 combo `*@hotmail.com` mới:

| # | Email | Total | OTP | Status |
|---|---|---|---|---|
| 1 | benjamindanewilson5795 | 28.95s | 6.78s | ✅ user-kGK15... |
| 2 | charlesryanwhite5155 | 25.38s | 2.05s | ✅ user-LuAh6... |
| 3 | benjaminwadetaylor1465 | 27.70s | 6.56s | ✅ user-MElQA... |
| 4 | jamesglenmartin8510 | 27.78s | 6.50s | ✅ user-15pP4... |
| 5 | lucassagethompson6849 | 27.83s | 6.20s | ✅ user-ZXH1N... |

**5/5 success, avg 27.5s.**
