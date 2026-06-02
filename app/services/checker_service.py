"""Subscription checker: kiểm tra gói đăng ký (Free / Plus / Pro) của ChatGPT qua access token.

Dùng curl_cffi AsyncSession impersonate="chrome136" cho TLS fingerprint.
"""
from __future__ import annotations

import json
from curl_cffi.requests import AsyncSession


class CheckerError(Exception):
    """Lỗi chung của Checker."""
    pass


class TokenExpiredError(CheckerError):
    """Token hết hạn hoặc không hợp lệ (HTTP 401)."""
    pass


class CloudflareBlockedError(CheckerError):
    """Bị Cloudflare chặn (HTTP 403)."""
    pass


_CHECK_URL = "https://chatgpt.com/backend-api/accounts/check/v4-2023-04-27"
_CF_MARKERS = ("cf-chl", "just a moment", "cloudflare")
_IMPERSONATE = "chrome136"


async def check_subscription(
    access_token: str,
    *,
    proxy: str | None = None,
    timeout: float = 30.0,
) -> str:
    """Gọi API nội bộ của ChatGPT để kiểm tra gói đăng ký (plan).

    Args:
        access_token: Bearer access token thô từ session.
        proxy: Proxy HTTP/HTTPS (nếu có).
        timeout: Thời gian timeout của request.

    Returns:
        Tên gói đăng ký (ví dụ: 'chatgptplusplan', 'chatgptfreeplan', v.v.)

    Raises:
        TokenExpiredError: Nếu token không hợp lệ hoặc hết hạn (401).
        CloudflareBlockedError: Nếu bị chặn bởi Cloudflare (403).
        CheckerError: Nếu gặp các lỗi HTTP khác hoặc parse JSON thất bại.
    """
    proxies = {"http": proxy, "https": proxy} if proxy else None

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "*/*",
        "Origin": "https://chatgpt.com",
        "Referer": "https://chatgpt.com/",
        "x-openai-target-path": "/backend-api/accounts/check/v4-2023-04-27",
        "x-openai-target-route": "/backend-api/accounts/check/v4-2023-04-27",
    }

    async with AsyncSession(impersonate=_IMPERSONATE, proxies=proxies) as session:
        try:
            resp = await session.get(
                _CHECK_URL,
                headers=headers,
                timeout=timeout,
            )
        except Exception as exc:
            raise CheckerError(f"request check plan thất bại: {exc}") from exc

        status = resp.status_code
        body = resp.text

        if status == 401:
            raise TokenExpiredError("Phiên đăng nhập hết hạn hoặc token không chính xác (401).")

        if status == 403:
            body_lower = body.lower()
            if any(marker in body_lower for marker in _CF_MARKERS):
                raise CloudflareBlockedError("Yêu cầu bị Cloudflare chặn (403).")
            raise CheckerError(f"Truy cập bị từ chối (403) — {body[:200]}")

        if status >= 500:
            raise CheckerError(f"Lỗi máy chủ OpenAI ({status}) — {body[:200]}")

        if status != 200:
            raise CheckerError(f"Lỗi phản hồi HTTP {status} — {body[:200]}")

        try:
            data = resp.json()
        except Exception as exc:
            raise CheckerError(f"Không thể parse JSON phản hồi: {exc} — body: {body[:300]}") from exc

        try:
            accounts = data.get("accounts")
            if not accounts:
                raise CheckerError("Không tìm thấy trường 'accounts' trong JSON phản hồi.")

            # Lấy key mặc định hoặc key đầu tiên
            account_key = "default" if "default" in accounts else list(accounts.keys())[0]
            entitlement = accounts[account_key].get("entitlement", {})
            
            # Đọc subscription_plan
            plan = entitlement.get("subscription_plan")
            if not plan:
                has_active = entitlement.get("has_active_subscription", False)
                plan = "chatgptplusplan" if has_active else "chatgptfreeplan"

            plan_str = str(plan)
            if plan_str == "chatgptfreeplan":
                # Gọi kiểm tra xem tài khoản có nhận được ưu đãi Plus 0$/0đ không
                is_eligible = await check_promo_eligibility(access_token, proxy=proxy, timeout=timeout)
                if is_eligible:
                    plan_str = "chatgptfreeplan (Yes Promo)"
                else:
                    plan_str = "chatgptfreeplan (No Promo)"

            return plan_str
        except Exception as exc:
            if isinstance(exc, CheckerError):
                raise
            raise CheckerError(f"Cấu trúc JSON phản hồi không đúng mong đợi: {exc} — body: {body[:300]}")


_CHECKOUT_URL = "https://chatgpt.com/backend-api/payments/checkout"


async def check_promo_eligibility(
    access_token: str,
    *,
    proxy: str | None = None,
    timeout: float = 30.0,
) -> bool:
    """Kiểm tra tài khoản Free có đủ điều kiện nhận ưu đãi 1 tháng Plus $0 (plus-1-month-free) không.

    Gửi thử request checkout lên OpenAI. Nếu trả về checkout_session_id thành công thì đủ điều kiện.
    """
    proxies = {"http": proxy, "https": proxy} if proxy else None

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Origin": "https://chatgpt.com",
        "Referer": "https://chatgpt.com/?promo_campaign=plus-1-month-free",
        "x-openai-target-path": "/backend-api/payments/checkout",
        "x-openai-target-route": "/backend-api/payments/checkout",
    }
    payload = {
        "entry_point": "all_plans_pricing_modal",
        "plan_name": "chatgptplusplan",
        "billing_details": {
            "country": "VN",
            "currency": "VND",
        },
        "promo_campaign": {
            "promo_campaign_id": "plus-1-month-free",
            "is_coupon_from_query_param": False,
        },
        "checkout_ui_mode": "hosted",
    }

    async with AsyncSession(impersonate=_IMPERSONATE, proxies=proxies) as session:
        try:
            resp = await session.post(
                _CHECKOUT_URL,
                headers=headers,
                json=payload,
                timeout=timeout,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("checkout_session_id"):
                    return True
            return False
        except Exception:
            return False
