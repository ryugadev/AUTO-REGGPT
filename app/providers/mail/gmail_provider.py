"""Gmail Advanced mail provider and factory (checkotpgmail.live API)."""
from __future__ import annotations

import asyncio
import time
from datetime import datetime
from pathlib import Path

import httpx

from .base import MailProvider


class GmailAdvancedParseError(Exception):
    """Parse input line fail cho Gmail Advanced mode."""


class GmailAdvancedProvider:
    """Provider poll OTP qua API checkotpgmail.live.

    Input format: email|api_url
    API response:
        {
            "ok": true,
            "order_id": "...",
            "service": "chatgpt",
            "email": "...",
            "status": "success",
            "mail_status": "live",
            "otp": "123456",       ← poll đến khi non-empty
            "otp_history": [...],
            "timeout_sec": 600,
            ...
        }

    Poll logic: gọi GET api_url liên tục, khi field `otp` có giá trị 6 số → return.
    Nếu `status` != "success" hoặc `ok` != true → báo lỗi.
    """

    def __init__(self, *, api_url: str, email: str = ""):
        if not api_url:
            raise ValueError("Gmail Advanced api_url is required")
        self.api_url = api_url
        self.email = email

    @classmethod
    def parse_line(cls, line: str) -> tuple[str, str]:
        """Parse line → (email, api_url).

        Hỗ trợ 2 format:
            - email|api_url  (cũ)
            - api_url        (chỉ paste link, email sẽ lấy từ API response)

        Raises GmailAdvancedParseError nếu format sai.
        """
        stripped = line.strip()
        # Format 1: chỉ URL (bắt đầu bằng http)
        if stripped.startswith(("http://", "https://")):
            return "", stripped
        # Format 2: email|url
        parts = stripped.split("|", 1)
        if len(parts) != 2:
            raise GmailAdvancedParseError(
                f"format phải là email|api_url hoặc chỉ api_url, nhận: {line[:80]}"
            )
        email_part = parts[0].strip()
        url_part = parts[1].strip()
        if not email_part or "@" not in email_part:
            raise GmailAdvancedParseError(f"email không hợp lệ: {email_part!r}")
        if not url_part.startswith(("http://", "https://")):
            raise GmailAdvancedParseError(f"api_url phải bắt đầu bằng http(s)://: {url_part[:60]}")
        return email_part, url_part

    async def pre_check(self, *, log) -> None:
        """Gọi API 1 lần để verify mail_status == 'live' trước khi chạy signup.

        Side-effects:
            - Nếu self.email rỗng (URL-only input) → tự fill email từ response.
            - Nếu mail_status != 'live' → raise ValueError (job fail ngay).
        """
        log(f"[otp:gmail_advanced] pre-check: {self.api_url}")
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            try:
                response = await client.get(self.api_url)
            except httpx.HTTPError as exc:
                raise ValueError(
                    f"Gmail Advanced pre-check failed (network): {type(exc).__name__}: {exc}"
                ) from exc

        if response.status_code != 200:
            raise ValueError(
                f"Gmail Advanced pre-check HTTP {response.status_code}: {response.text[:200]}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise ValueError(f"Gmail Advanced pre-check: response không phải JSON") from exc

        # Extract email nếu chưa có (URL-only mode)
        api_email = str(data.get("email") or "").strip()
        if not self.email and api_email:
            self.email = api_email
            log(f"[otp:gmail_advanced] email from API: {self.email}")

        # Check ok field
        if not data.get("ok"):
            status = data.get("status", "unknown")
            raise ValueError(
                f"Gmail Advanced pre-check failed: ok=false, status={status}"
            )

        # Check mail_status
        mail_status = str(data.get("mail_status") or "").strip().lower()
        if mail_status != "live":
            raise ValueError(
                f"Gmail Advanced pre-check: mail_status='{mail_status}' (cần 'live') — "
                f"email={api_email or self.email}, dừng job."
            )

        log(f"[otp:gmail_advanced] pre-check OK: mail_status=live, email={self.email}")

    async def poll_otp(
        self,
        *,
        recipient: str,
        started_at: datetime,
        timeout_seconds: float,
        poll_interval_seconds: float,
        log,
    ) -> str:
        deadline = time.monotonic() + max(timeout_seconds, 1.0)
        log(f"[otp:gmail_advanced] polling {self.email} (timeout {timeout_seconds:.0f}s)")
        log(f"[otp:gmail_advanced] api: {self.api_url}")

        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            attempt = 0
            while True:
                attempt += 1
                try:
                    response = await client.get(self.api_url)
                    if response.status_code != 200:
                        log(f"[otp:gmail_advanced] HTTP {response.status_code} attempt {attempt}")
                    else:
                        data = response.json()
                        # Check API errors
                        if not data.get("ok"):
                            status = data.get("status", "unknown")
                            log(f"[otp:gmail_advanced] api ok=false status={status} attempt {attempt}")
                            # Nếu status rõ ràng là lỗi terminal → raise
                            if status in ("expired", "cancelled", "not_found"):
                                raise TimeoutError(
                                    f"Gmail Advanced API error: status={status} for {self.email}"
                                )
                        else:
                            otp = str(data.get("otp") or "").strip()
                            if otp and len(otp) == 6 and otp.isdigit():
                                log(f"[otp:gmail_advanced] found OTP {otp} (attempt {attempt})")
                                return otp

                            # Check otp_history — lấy code mới nhất nếu có
                            otp_history = data.get("otp_history")
                            if isinstance(otp_history, list) and otp_history:
                                # otp_history có thể là list string hoặc list dict
                                latest = otp_history[-1]
                                if isinstance(latest, dict):
                                    code = str(latest.get("otp") or latest.get("code") or "").strip()
                                else:
                                    code = str(latest).strip()
                                if code and len(code) == 6 and code.isdigit():
                                    log(f"[otp:gmail_advanced] found OTP from history {code} (attempt {attempt})")
                                    return code

                            if attempt <= 3 or attempt % 5 == 0:
                                log(f"[otp:gmail_advanced] waiting... otp='{otp}' attempt {attempt}")
                except (httpx.HTTPError, ValueError) as exc:
                    log(f"[otp:gmail_advanced] error attempt {attempt}: {exc}")

                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError(
                        f"OTP timeout after {timeout_seconds}s for {self.email} (gmail_advanced)"
                    )
                await asyncio.sleep(min(poll_interval_seconds, remaining))


def build_provider_gmail_advanced(
    *, email: str, api_url: str,
) -> GmailAdvancedProvider:
    return GmailAdvancedProvider(api_url=api_url, email=email)


def build_provider_auto_gmail_otp(
    *, api_key: str, service: str, proxy: str | None = None,
):
    """Factory cho Auto Gmail OTP provider.

    api_key + service inject từ Settings (.env), KHÔNG hardcode trong code.
    Sử dụng lazy import để tránh circular import với OTP provider.
    """
    from app.providers.otp.gmail_otp_provider import AutoGmailOtpProvider
    return AutoGmailOtpProvider(api_key=api_key, service=service, proxy=proxy)
