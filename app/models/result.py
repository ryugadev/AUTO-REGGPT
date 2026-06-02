"""Result models for signup hybrid."""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class SignupResult(BaseModel):
    """Output cuối: session token NextAuth + metadata."""

    success: bool
    email: str
    password: str | None = Field(default=None, description="Password đã set khi register.")
    name: str | None = Field(default=None, description="Tên hiển thị đã dùng.")
    age: int | None = Field(default=None, description="Tuổi đã dùng (compute từ birthdate).")
    user_id: str | None = None
    account_id: str | None = None
    session_token: str | None = Field(default=None, description="__Secure-next-auth.session-token JWT.")
    access_token: str | None = Field(default=None, description="Bearer JWT cho /backend-api/.")
    cookies: list[dict[str, Any]] = Field(default_factory=list, description="Cookies sau callback (chatgpt.com).")
    phase1_seconds: float = 0.0
    phase2_seconds: float = 0.0
    otp_seconds: float = 0.0
    mail_meta: dict[str, Any] | None = Field(default=None, description="Metadata từ mail provider.")
    error: str | None = None
