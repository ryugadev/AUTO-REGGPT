"""Session models for signup hybrid."""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class BrowserHandoff(BaseModel):
    """Output Phase 1 — context để Phase 2 dùng."""

    cookies: list[dict[str, Any]] = Field(default_factory=list, description="Playwright cookies dict list.")
    state_param: str = Field(..., description="OAuth state lấy từ URL /authorize?...&state=<...>.")
    device_id: str = Field(..., description="ext-oai-did UUID (cũng là id field cho /sentinel/req).")
    auth_session_logging_id: str = Field(..., description="Logging ID từ /api/auth/signin/openai redirect URL.")
    callback_redirect_uri: str = Field(
        default="https://chatgpt.com/api/auth/callback/openai",
        description="redirect_uri của OAuth (giống nhau cho mọi run, copy từ HAR).",
    )
    callback_url: str = Field(
        ...,
        description="Full callback URL (kèm code + state) trả về từ create_account, dùng cho Phase 2.",
    )

    # Cookies Phase 2 cần dùng (helpers)
    @property
    def cookies_dict_for(self) -> dict[str, dict[str, str]]:
        """Map domain → {name: value} cho dễ inject vào curl_cffi."""
        out: dict[str, dict[str, str]] = {}
        for c in self.cookies:
            domain = (c.get("domain") or "").lstrip(".")
            out.setdefault(domain, {})[c["name"]] = c["value"]
        return out
