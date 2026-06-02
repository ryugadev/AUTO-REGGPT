"""Check Auto Gmail OTP provider + registry integration + input behavior.

Chạy: .venv\\Scripts\\python.exe test\\check_auto_gmail_otp.py
Không cần network — mock httpx.AsyncClient.
"""
from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

# Cho phép import package khi chạy trực tiếp
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gpt_signup_hybrid.auto_gmail_otp_provider import (
    AutoGmailOtpProvider,
    AutoGmailOtpError,
)


# ─── Fake httpx ───────────────────────────────────────────────────────


class _FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.text = str(payload)

    def json(self):
        return self._payload


class _FakeAsyncClient:
    """Mock httpx.AsyncClient — route theo path, trả response từ script."""

    # Mỗi key path → list response (pop dần) hoặc 1 response cố định.
    routes: dict = {}
    # Capture params của lần GET gần nhất theo path.
    captured: dict = {}

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def get(self, url, params=None):
        for key, resp in _FakeAsyncClient.routes.items():
            if key in url:
                _FakeAsyncClient.captured[key] = dict(params or {})
                if isinstance(resp, list):
                    return resp.pop(0) if len(resp) > 1 else resp[0]
                return resp
        raise AssertionError(f"unexpected URL: {url}")


def _patch_httpx(monkey_routes: dict) -> None:
    import gpt_signup_hybrid.auto_gmail_otp_provider as mod
    _FakeAsyncClient.routes = monkey_routes
    _FakeAsyncClient.captured = {}
    mod.httpx.AsyncClient = _FakeAsyncClient  # type: ignore[attr-defined]


# ─── Tests ────────────────────────────────────────────────────────────


def test_1_create_order_success():
    _patch_httpx({
        "CreateOrder": _FakeResponse({
            "status": "success",
            "msg": "order created successfully!",
            "data": {
                "email": "test@gmail.com|https://checkotpgmail.live/otp/abc?t=123",
                "orderid": "order123",
                "service": "chatgpt",
                "status": "success",
                "otp": "",
            },
        }),
    })
    p = AutoGmailOtpProvider(api_key="k", service="chatgpt")
    order = asyncio.run(p.create_otp_order("chatgpt"))
    # Combo giữ nguyên email|api_url
    assert order["combo"] == "test@gmail.com|https://checkotpgmail.live/otp/abc?t=123", order
    assert order["email"] == "test@gmail.com", order
    assert order["api_url"].startswith("https://checkotpgmail.live/otp/"), order
    assert order["order_id"] == "order123", order
    # include_view_link phải là "true"
    captured = _FakeAsyncClient.captured.get("CreateOrder", {})
    assert captured.get("include_view_link") == "true", captured
    # apikey được inject (nhưng không được log — chỉ check tồn tại)
    assert captured.get("apikey") == "k", "apikey phải được inject vào params"
    print("✓ test_1 create order success (include_view_link=true, combo giữ nguyên)")


def test_2_poll_otp_via_gmail_advanced():
    # pre_check set api_url → poll_otp reuse GmailAdvancedProvider (poll api_url).
    # Patch httpx của CẢ auto provider lẫn gmail advanced (cùng module httpx? không —
    # GmailAdvancedProvider ở mail_providers.py dùng httpx riêng). Patch luôn.
    import gpt_signup_hybrid.mail_providers as mp_mod

    class _GAClient:
        seq = [
            _FakeResponse({"ok": False, "status": "pending", "otp": ""}),
            _FakeResponse({"ok": True, "status": "success", "mail_status": "live",
                           "email": "test@gmail.com", "otp": "123456"}),
        ]
        def __init__(self, *a, **k): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *a): return False
        async def get(self, url, params=None):
            return _GAClient.seq.pop(0) if len(_GAClient.seq) > 1 else _GAClient.seq[0]

    mp_mod.httpx.AsyncClient = _GAClient  # type: ignore[attr-defined]

    p = AutoGmailOtpProvider(api_key="k", service="chatgpt")
    p.api_url = "https://checkotpgmail.live/otp/abc?t=123"
    p.email = "test@gmail.com"
    otp = asyncio.run(p.poll_otp(
        recipient="test@gmail.com",
        started_at=datetime.now(timezone.utc),
        timeout_seconds=20,
        poll_interval_seconds=0,
        log=lambda m: None,
    ))
    assert otp == "123456", otp
    print("✓ test_2 poll OTP via Gmail Advanced api_url")


def test_2b_poll_otp_fallback_checkotp2():
    # Không có api_url → fallback CheckOtp2. Lần 1 rỗng, lần 2 trả OTP.
    _patch_httpx({
        "CheckOtp2": [
            _FakeResponse({"status": "success", "data": {"otp": ""}}),
            _FakeResponse({"status": "success", "data": {"email": "x@gmail.com", "otp": "654321"}}),
        ],
    })
    p = AutoGmailOtpProvider(api_key="k", service="chatgpt")
    p.order_id = "order123"
    p.api_url = None
    otp = asyncio.run(p.poll_otp(
        recipient="x@gmail.com",
        started_at=datetime.now(timezone.utc),
        timeout_seconds=20,
        poll_interval_seconds=0,
        log=lambda m: None,
    ))
    assert otp == "654321", otp
    print("✓ test_2b poll OTP fallback CheckOtp2")


def test_3_stock_empty():
    _patch_httpx({
        "GetStockOtpGmail": _FakeResponse({"status": "success", "stock": 0}),
    })
    p = AutoGmailOtpProvider(api_key="k", service="chatgpt")
    try:
        asyncio.run(p.pre_check(log=lambda m: None))
        raise AssertionError("expected AutoGmailOtpError")
    except AutoGmailOtpError as exc:
        assert "otp_stock_empty" in str(exc), exc
    print("✓ test_3 stock empty → otp_stock_empty")


def test_3b_pre_check_normalize():
    # stock > 0 + CreateOrder combo → pre_check trả normalize đầy đủ.
    _patch_httpx({
        "GetStockOtpGmail": _FakeResponse({"status": "success", "stock": 5}),
        "CreateOrder": _FakeResponse({
            "status": "success",
            "data": {
                "email": "test@gmail.com|https://checkotpgmail.live/otp/abc?t=123",
                "orderid": "order123",
                "service": "chatgpt",
                "status": "success",
            },
        }),
    })
    p = AutoGmailOtpProvider(api_key="k", service="chatgpt")
    result = asyncio.run(p.pre_check(log=lambda m: None))
    assert result["combo"] == "test@gmail.com|https://checkotpgmail.live/otp/abc?t=123", result
    assert result["email"] == "test@gmail.com", result
    assert result["api_url"].startswith("https://checkotpgmail.live/otp/"), result
    assert result["order_id"] == "order123", result
    assert result["provider"] == "auto_gmail_otp", result
    # State provider set đúng
    assert p.email == "test@gmail.com"
    assert p.api_url and p.api_url.startswith("https://")
    assert p.get_mail_meta()["combo"] == result["combo"]
    print("✓ test_3b pre_check normalize combo/email/api_url/order_id")


def test_4_registry_integration():
    from gpt_signup_hybrid.web.mail_modes import get_registry, get_spec, serialize_for_api
    reg = get_registry()
    assert "auto_gmail_otp" in reg, list(reg.keys())
    spec = get_spec("auto_gmail_otp")
    assert spec.label == "Auto Gmail OTP", spec.label
    # Mode cũ vẫn còn
    for old in ("outlook", "worker", "gmail_advanced"):
        assert old in reg, f"missing old mode {old}"
    # build provider qua factory
    from gpt_signup_hybrid.mail_providers import build_provider_auto_gmail_otp
    prov = build_provider_auto_gmail_otp(api_key="k", service="demo")
    assert prov.mode_name == "Auto Gmail OTP"
    # serialize cho UI
    modes = serialize_for_api()
    assert any(m["id"] == "auto_gmail_otp" for m in modes)
    print("✓ test_4 registry integration")


def test_5_input_empty_creates_one_job():
    from gpt_signup_hybrid.web.manager import JobManager
    mgr = JobManager(max_concurrent=1)

    async def _run():
        # Không enqueue worker thật — chỉ kiểm add_jobs tạo job.
        jobs = mgr.add_jobs([], mail_mode="auto_gmail_otp")
        return jobs

    # add_jobs gọi _ensure_workers (tạo asyncio task) → cần event loop
    async def _wrap():
        jobs = mgr.add_jobs([], mail_mode="auto_gmail_otp")
        # stop workers để loop kết thúc sạch
        mgr.stop_all()
        for w in mgr._workers:
            w.cancel()
        return jobs

    jobs = asyncio.run(_wrap())
    assert len(jobs) == 1, f"expected 1 job, got {len(jobs)}"
    assert jobs[0].mail_mode == "auto_gmail_otp"
    print("✓ test_5 input empty → 1 job")


def test_6_missing_config_raises():
    try:
        AutoGmailOtpProvider(api_key="", service="demo")
        raise AssertionError("expected error for missing api_key")
    except AutoGmailOtpError as exc:
        assert "SHOPGMAIL_API_KEY" in str(exc), exc
    try:
        AutoGmailOtpProvider(api_key="k", service="")
        raise AssertionError("expected error for missing service")
    except AutoGmailOtpError as exc:
        assert "SHOPGMAIL_OTP_SERVICE" in str(exc), exc
    print("✓ test_6 missing config raises")


def test_7_soldout_status():
    """Khi run_signup fail với otp_stock_empty → job.status = 'soldout', không phải 'error'."""
    from gpt_signup_hybrid.web import manager as mgr_mod
    from gpt_signup_hybrid.models import SignupResult

    mgr = mgr_mod.JobManager(max_concurrent=1)

    async def _fake_stock_empty(request, *, log=print):
        log("[Auto Gmail OTP] Stock=0")
        return SignupResult(
            success=False,
            email="pending@auto-gmail-otp.local",
            error="AutoGmailOtpError: otp_stock_empty",
        )

    async def _fake_other_error(request, *, log=print):
        return SignupResult(
            success=False,
            email="x@gmail.com",
            error="TimeoutError: OTP timeout after 300s",
        )

    async def _run_one(fake_fn):
        mgr_mod.run_signup = fake_fn  # type: ignore[attr-defined]
        from gpt_signup_hybrid.web.mail_modes import AUTO_GMAIL_OTP_PENDING_EMAIL
        jid = "testjob1"
        job = mgr_mod.Job(id=jid, email=AUTO_GMAIL_OTP_PENDING_EMAIL, combo="__auto__", mail_mode="auto_gmail_otp")
        mgr.jobs[jid] = job
        mgr.order.append(jid)
        await mgr._run_job(job)
        return job

    job = asyncio.run(_run_one(_fake_stock_empty))
    assert job.status == "soldout", f"expected soldout, got {job.status}"
    assert job.error is None, f"soldout không nên có error, got {job.error!r}"

    # Reset + test lỗi thật vẫn là error
    mgr.jobs.clear()
    mgr.order.clear()
    job2 = asyncio.run(_run_one(_fake_other_error))
    assert job2.status == "error", f"expected error, got {job2.status}"
    assert job2.error and "timeout" in job2.error.lower(), job2.error
    print("✓ test_7 soldout vs error status")


if __name__ == "__main__":
    test_1_create_order_success()
    test_2_poll_otp_via_gmail_advanced()
    test_2b_poll_otp_fallback_checkotp2()
    test_3_stock_empty()
    test_3b_pre_check_normalize()
    test_4_registry_integration()
    test_5_input_empty_creates_one_job()
    test_6_missing_config_raises()
    test_7_soldout_status()
    print("\nALL PASS")
