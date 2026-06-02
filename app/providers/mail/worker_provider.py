"""Worker mail provider (Cloudflare Worker logs API)."""
from __future__ import annotations

import asyncio
import ssl
import time
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote

import httpx

from app.core.config import warn_insecure_tls
from .base import _extract_otp, _parse_dt


class WorkerMailProvider:
    """Cloudflare Worker logs API.

    Worker trả JSON:
        - list trực tiếp [{to, subject, body, date, ...}, ...]
        - hoặc dict {messages|items|logs|emails|data: [...]}
    """

    def __init__(self, *, logs_url: str, api_key: str | None, insecure_tls: bool = False):
        if not logs_url:
            raise ValueError("Worker logs_url is required")
        self.logs_url = logs_url
        self.api_key = api_key
        self.insecure_tls = insecure_tls
        if insecure_tls:
            warn_insecure_tls("mail_providers.WorkerMailProvider")

    @staticmethod
    def _normalize(payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            for key in ("messages", "items", "logs", "emails", "data"):
                value = payload.get(key)
                if isinstance(value, list):
                    return value
        return []

    async def poll_otp(
        self,
        *,
        recipient: str,
        started_at: datetime,
        timeout_seconds: float,
        poll_interval_seconds: float,
        log,
    ) -> str:
        mailbox = recipient.strip().lower()
        if not mailbox:
            raise ValueError("recipient is required")

        headers: dict[str, str] = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        if self.insecure_tls:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            verify: Any = ctx
        else:
            verify = True

        deadline = time.monotonic() + max(timeout_seconds, 1.0)
        log(f"[otp:worker] polling {mailbox} (timeout {timeout_seconds:.0f}s)")

        async with httpx.AsyncClient(verify=verify, timeout=20.0, follow_redirects=True) as client:
            attempt = 0
            while True:
                attempt += 1
                try:
                    response = await client.get(
                        f"{self.logs_url}?mail={quote(mailbox)}",
                        headers=headers,
                    )
                    if response.status_code != 200:
                        log(f"[otp:worker] HTTP {response.status_code} attempt {attempt}")
                    else:
                        messages = self._normalize(response.json())
                        # Sort mới nhất trước dựa theo date field.
                        # Nếu message không có date (iCloud worker có thể không trả) →
                        # KHÔNG đảo vị trí: giữ thứ tự gốc từ API bằng cách gán
                        # timestamp = epoch 0 (bị đẩy cuối khi reverse=True sort).
                        # Nếu TẤT CẢ messages không có date → skip sort giữ nguyên API order.
                        has_any_date = False
                        for m in messages:
                            if _parse_dt(m.get("date") or m.get("receivedAt") or m.get("created_at")):
                                has_any_date = True
                                break
                        if has_any_date:
                            messages.sort(
                                key=lambda m: (
                                    _parse_dt(m.get("date") or m.get("receivedAt") or m.get("created_at"))
                                    or datetime.min.replace(tzinfo=timezone.utc)
                                ),
                                reverse=True,
                            )
                        for msg in messages:
                            msg_to = str(msg.get("to") or "").strip().lower()
                            if msg_to and msg_to != mailbox:
                                continue
                            msg_dt = _parse_dt(msg.get("date") or msg.get("receivedAt") or msg.get("created_at"))
                            if msg_dt is not None and msg_dt < started_at:
                                continue
                            subject = str(msg.get("subject") or "")
                            body = (
                                msg.get("bodyText") or msg.get("text") or msg.get("body")
                                or msg.get("htmlBody") or msg.get("content") or msg.get("html") or ""
                            )
                            code = _extract_otp(subject, str(body))
                            if code:
                                log(f"[otp:worker] found {code} (attempt {attempt})")
                                return code
                except (httpx.HTTPError, ValueError) as exc:
                    log(f"[otp:worker] error attempt {attempt}: {exc}")

                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError(f"OTP timeout after {timeout_seconds}s for {mailbox}")
                await asyncio.sleep(min(poll_interval_seconds, remaining))

    async def poll_all_codes(
        self,
        *,
        recipient: str,
        started_at: datetime,
        log,
    ) -> list[str]:
        """Lấy TẤT CẢ OTP codes mới (sau started_at) trong 1 lần call API.

        Return list unique codes theo thứ tự API trả về (có thể mới nhất trước hoặc sau
        tuỳ worker). Không block/poll — chỉ fetch 1 lần.
        Dùng cho case: sau khi nhận 1 code, fetch lại để bắt thêm mail delay.
        """
        mailbox = recipient.strip().lower()
        if not mailbox:
            return []

        headers: dict[str, str] = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        if self.insecure_tls:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            verify: Any = ctx
        else:
            verify = True

        try:
            async with httpx.AsyncClient(verify=verify, timeout=20.0, follow_redirects=True) as client:
                response = await client.get(
                    f"{self.logs_url}?mail={quote(mailbox)}",
                    headers=headers,
                )
                if response.status_code != 200:
                    return []
                messages = self._normalize(response.json())
                codes: list[str] = []
                seen: set[str] = set()
                for msg in messages:
                    msg_to = str(msg.get("to") or "").strip().lower()
                    if msg_to and msg_to != mailbox:
                        continue
                    msg_dt = _parse_dt(msg.get("date") or msg.get("receivedAt") or msg.get("created_at"))
                    if msg_dt is not None and msg_dt < started_at:
                        continue
                    subject = str(msg.get("subject") or "")
                    body = (
                        msg.get("bodyText") or msg.get("text") or msg.get("body")
                        or msg.get("htmlBody") or msg.get("content") or msg.get("html") or ""
                    )
                    code = _extract_otp(subject, str(body))
                    if code and code not in seen:
                        seen.add(code)
                        codes.append(code)
                return codes
        except Exception:
            return []


def build_provider_worker(
    *, logs_url: str, api_key: str | None, insecure_tls: bool = False,
) -> WorkerMailProvider:
    return WorkerMailProvider(logs_url=logs_url, api_key=api_key, insecure_tls=insecure_tls)
