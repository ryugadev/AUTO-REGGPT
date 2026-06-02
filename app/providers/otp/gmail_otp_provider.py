"""Auto Gmail OTP provider — thuê Gmail + đọc OTP qua API shopgmail9999."""
from __future__ import annotations

import asyncio
import time
from datetime import datetime
from typing import Any, Callable

import httpx


LogFn = Callable[[str], None]


class AutoGmailOtpError(Exception):
    """Auto Gmail OTP API/config fail (terminal cho job hiện tại)."""


_DEFAULT_BASE_URL = "https://shopgmail9999.com"

# Endpoint paths (relative). Service + api_key truyền qua query, không hardcode.
_EP_SERVICES = "/api/Apiv2/GetListServices"
_EP_STOCK = "/api/Apiv2/GetStockOtpGmail"
_EP_CREATE = "/api/Apiv2/CreateOrder"
_EP_CHECK2 = "/api/Apiv2/CheckOtp2"
_EP_CHECK = "/api/Apiv2/CheckOtp"


def _extract_otp_from_response(data: dict[str, Any]) -> str | None:
    """Lấy OTP từ response check. Hỗ trợ data.otp hoặc data.data.otp."""
    otp = data.get("otp")
    if not otp:
        inner = data.get("data")
        if isinstance(inner, dict):
            otp = inner.get("otp")
    otp = str(otp or "").strip()
    return otp or None


def _split_combo(combo: str) -> tuple[str, str | None]:
    """Tách combo `email|api_url` → (email, api_url|None).

    include_view_link=true → field email có dạng `email@gmail.com|https://.../otp/...`.
    Nếu không có dấu '|' → chỉ có email, api_url = None.
    """
    combo = (combo or "").strip()
    if "|" in combo:
        email, _, api_url = combo.partition("|")
        return email.strip(), (api_url.strip() or None)
    return combo, None


class AutoGmailOtpProvider:
    """Provider thuê Gmail + đọc OTP qua API shopgmail9999.

    Lifecycle:
        1. pre_check()  → check stock → CreateOrder(include_view_link=true)
                          → set self.email + self.api_url + self.order_id
        2. poll_otp()   → ưu tiên đọc OTP qua api_url (reuse Gmail Advanced);
                          fallback CheckOtp2 bằng order_id nếu không có api_url.
    """

    mode_name = "Auto Gmail OTP"

    def __init__(
        self,
        *,
        api_key: str,
        service: str,
        base_url: str | None = None,
        proxy: str | None = None,
    ):
        if not api_key:
            raise AutoGmailOtpError("Missing SHOPGMAIL_API_KEY")
        if not service:
            raise AutoGmailOtpError("Missing SHOPGMAIL_OTP_SERVICE")
        self.api_key = api_key
        self.service = service
        self.base_url = (base_url or _DEFAULT_BASE_URL).rstrip("/")
        self.proxy = proxy.strip() if isinstance(proxy, str) and proxy.strip() else None
        # Resolved sau pre_check
        self.combo: str = ""
        self.email: str = ""
        self.api_url: str | None = None
        self.order_id: str = ""

    # ── HTTP core ────────────────────────────────────────────────────

    async def _api_get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        """GET <base_url><path> với apikey inject. Trả parsed JSON dict.

        KHÔNG log api_key. Raise AutoGmailOtpError khi network/HTTP/JSON fail.
        """
        url = f"{self.base_url}{path}"
        query = dict(params or {})
        query["apikey"] = self.api_key  # inject, không log

        kwargs: dict[str, Any] = {"timeout": 20.0, "follow_redirects": True}
        if self.proxy:
            kwargs["proxy"] = self.proxy

        async with httpx.AsyncClient(**kwargs) as client:
            try:
                resp = await client.get(url, params=query)
            except httpx.HTTPError as exc:
                raise AutoGmailOtpError(
                    f"network error calling {path}: {type(exc).__name__}: {exc}"
                ) from exc

        if resp.status_code != 200:
            raise AutoGmailOtpError(f"HTTP {resp.status_code} from {path}: {resp.text[:200]}")
        try:
            data = resp.json()
        except ValueError as exc:
            raise AutoGmailOtpError(f"response từ {path} không phải JSON") from exc
        if not isinstance(data, dict):
            raise AutoGmailOtpError(f"response từ {path} không phải JSON object")
        return data

    # ── API methods ──────────────────────────────────────────────────

    async def get_otp_services(self) -> list[dict[str, Any]]:
        """GET danh sách service khả dụng."""
        data = await self._api_get(_EP_SERVICES, {})
        services = data.get("data")
        return services if isinstance(services, list) else []

    async def get_otp_stock(self, service: str | None = None) -> int:
        """GET stock của service. Trả int (0 nếu không xác định)."""
        svc = service or self.service
        data = await self._api_get(_EP_STOCK, {"service": svc})
        stock = data.get("stock")
        if stock is None and isinstance(data.get("data"), dict):
            stock = data["data"].get("stock")
        try:
            return int(stock)
        except (TypeError, ValueError):
            return 0

    async def create_otp_order(self, service: str | None = None, quantity: int = 1) -> dict[str, Any]:
        """Tạo order thuê Gmail OTP với include_view_link=true. Trả normalized dict.

        include_view_link=true → field email có dạng combo `email|api_url`
        (reuse pipeline Gmail Advanced). Giữ NGUYÊN combo, không bỏ phần api_url.

        Returns:
            {"combo": ..., "email": ..., "api_url": ...|None,
             "order_id": ..., "service": ..., "status": ...}
        """
        svc = service or self.service
        data = await self._api_get(
            _EP_CREATE,
            {"service": svc, "include_view_link": "true", "quantity": quantity},
        )
        if str(data.get("status", "")).lower() != "success":
            raise AutoGmailOtpError(
                f"CreateOrder failed: {data.get('msg') or data.get('status') or 'unknown'}"
            )
        payload = data.get("data") or {}
        if isinstance(payload, list):
            payload = payload[0] if payload else {}
        if not isinstance(payload, dict):
            raise AutoGmailOtpError("CreateOrder response: data không hợp lệ")
        combo = str(payload.get("email") or "").strip()  # có thể là "email|api_url"
        order_id = str(payload.get("orderid") or payload.get("order_id") or "").strip()
        if not combo or not order_id:
            raise AutoGmailOtpError("CreateOrder response thiếu email/orderid")
        email, api_url = _split_combo(combo)
        if not email:
            raise AutoGmailOtpError("CreateOrder response: combo không có email")
        return {
            "combo": combo,
            "email": email,
            "api_url": api_url,
            "order_id": order_id,
            "service": str(payload.get("service") or svc),
            "status": str(payload.get("status") or "created"),
        }

    async def check_otp(self, order_id: str, getbody: bool = False) -> dict[str, Any]:
        """Check OTP real-time (CheckOtp2). Fallback CheckOtp nếu CheckOtp2 fail."""
        params = {"orderid": order_id, "getbody": "true" if getbody else "false"}
        try:
            return await self._api_get(_EP_CHECK2, params)
        except AutoGmailOtpError:
            # Fallback endpoint cũ (không có getbody)
            return await self._api_get(_EP_CHECK, {"orderid": order_id})

    async def _poll_order_otp(
        self, order_id: str, *, timeout: int = 180, interval: int = 4, log: LogFn = print,
    ) -> str | None:
        """Poll OTP đến khi có hoặc hết timeout. Trả str | None."""
        deadline = time.monotonic() + max(timeout, 1)
        attempt = 0
        while time.monotonic() < deadline:
            attempt += 1
            try:
                data = await self.check_otp(order_id)
                otp = _extract_otp_from_response(data)
                if otp:
                    return otp
            except AutoGmailOtpError as exc:
                if attempt <= 3 or attempt % 5 == 0:
                    log(f"[Auto Gmail OTP] check error attempt {attempt}: {exc}")
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            await asyncio.sleep(min(interval, max(remaining, 0.1)))
        return None

    # ── Provider interface (khớp flow signup hiện tại) ───────────────

    def get_mail_meta(self) -> dict[str, Any]:
        """Metadata gắn vào job/result."""
        return {
            "provider": "auto_gmail_otp",
            "combo": self.combo,
            "email": self.email,
            "api_url": self.api_url,
            "order_id": self.order_id,
            "service": self.service,
        }

    async def pre_check(self, *, log: LogFn = print) -> dict[str, Any]:
        """Check stock → CreateOrder(include_view_link=true) → resolve combo.

        Raises AutoGmailOtpError nếu stock rỗng / create fail.
        """
        log(f"[Auto Gmail OTP] Checking stock for service={self.service}")
        stock = await self.get_otp_stock(self.service)
        log(f"[Auto Gmail OTP] Stock={stock}")
        if stock <= 0:
            raise AutoGmailOtpError("otp_stock_empty")

        log(f"[Auto Gmail OTP] Creating order service={self.service} include_view_link=true")
        order = await self.create_otp_order(self.service, quantity=1)
        self.combo = order["combo"]
        self.email = order["email"]
        self.api_url = order["api_url"]
        self.order_id = order["order_id"]
        log(f"[Auto Gmail OTP] Created combo: email={self.email} api_url={self.api_url}")
        return {
            "combo": self.combo,
            "email": self.email,
            "api_url": self.api_url,
            "order_id": self.order_id,
            "service": self.service,
            "provider": "auto_gmail_otp",
        }

    async def poll_otp(
        self,
        *,
        recipient: str,
        started_at: datetime,
        timeout_seconds: float,
        poll_interval_seconds: float,
        log: LogFn = print,
    ) -> str:
        """Poll OTP cho order đã tạo ở pre_check. Khớp MailProvider Protocol.

        Ưu tiên:
            1. Có api_url → reuse logic Gmail Advanced (đọc OTP từ api_url).
            2. Không có api_url nhưng có order_id → fallback CheckOtp2.
        """
        if self.api_url:
            log(f"[Auto Gmail OTP] Waiting OTP via Gmail Advanced api_url")
            # Lazy import to avoid circular dependency
            from app.providers.mail.gmail_provider import GmailAdvancedProvider
            ga = GmailAdvancedProvider(api_url=self.api_url, email=self.email)
            otp = await ga.poll_otp(
                recipient=recipient or self.email,
                started_at=started_at,
                timeout_seconds=timeout_seconds,
                poll_interval_seconds=poll_interval_seconds,
                log=log,
            )
            log("[Auto Gmail OTP] OTP received")
            return otp

        if not self.order_id:
            raise AutoGmailOtpError("chưa có api_url/order_id — pre_check chưa chạy")
        log(f"[Auto Gmail OTP] Waiting OTP for order_id={self.order_id} (CheckOtp2 fallback)")
        otp = await self._poll_order_otp(
            self.order_id,
            timeout=int(timeout_seconds),
            interval=int(max(poll_interval_seconds, 1)),
            log=log,
        )
        if not otp:
            raise TimeoutError(
                f"OTP timeout after {timeout_seconds}s (order_id={self.order_id})"
            )
        log("[Auto Gmail OTP] OTP received")
        return otp
