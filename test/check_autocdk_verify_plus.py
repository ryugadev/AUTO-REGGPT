"""Guard: Auto CDK verify Plus thật qua /backend-api/accounts/check.

Kiểm tra 4 case:
  1. baxigpt báo paid + Plus thật       → success (giữ nguyên)
  2. baxigpt báo paid + Plus chưa active → mark fail terminal (override sai)
  3. baxigpt báo fail/timeout + Plus thật → override SUCCESS
  4. baxigpt báo fail + Plus chưa active → giữ error

Chạy: .venv\\Scripts\\python.exe test\\check_autocdk_verify_plus.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

PKG_ROOT = Path(__file__).resolve().parent.parent
ROOT = PKG_ROOT.parent
for p in (str(ROOT), str(PKG_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)


class _Resp:
    def __init__(self, p): self._p = p
    def raise_for_status(self): pass
    def json(self): return self._p


class _Client:
    """Mock baxigpt API; status response tuỳ test set."""
    table = {}  # path → response payload (single hoặc list để pop)

    def __init__(self, *a, **k): pass
    async def __aenter__(self): return self
    async def __aexit__(self, *a): return False
    async def post(self, url, json=None, headers=None):
        path = url.split("baxigpt.com")[-1]
        v = _Client.table.get(path)
        if isinstance(v, list):
            return _Resp(v.pop(0) if len(v) > 1 else v[0])
        return _Resp(v or {"ok": False, "msg": "?"})


def main() -> int:
    import gpt_signup_hybrid.web.manager as mgr_mod
    from gpt_signup_hybrid.web.manager import AutoCdkJobManager, AutoCdkJob
    import httpx

    orig_client = httpx.AsyncClient
    httpx.AsyncClient = _Client

    # Mock check_subscription qua patch app.services.checker_service.check_subscription
    # nhưng manager.py import nó cục bộ trong _autocdk_verify_plus → patch module đó
    import app.services.checker_service as svc
    orig_check = svc.check_subscription
    plan_to_return = {"plan": "chatgptplusplan"}

    async def _fake_check(token, **kw):
        return plan_to_return["plan"]
    svc.check_subscription = _fake_check

    ok = True
    try:
        async def run_case(name, *, baxigpt_paid: bool, plan: str):
            plan_to_return["plan"] = plan
            _Client.table = {
                "/api/code-info": {"ok": True, "remaining": 1, "total": 1},
                "/api/submit": {"ok": True, "order_id": "ORD"},
                "/api/status": (
                    {"ok": True, "status": "paid"} if baxigpt_paid
                    else {"ok": True, "status": "failed"}
                ),
            }
            mgr = AutoCdkJobManager(max_concurrent=1)
            job = AutoCdkJob(
                id=f"j_{name}", email="x@x", password="p", cdk_key="BX",
                access_token="AT_PRE",  # skip login
            )
            mgr.jobs[job.id] = job
            mgr.order.append(job.id)
            await mgr._run_job(job)
            return job

        # Case 1: baxigpt paid + Plus thật → success
        j = asyncio.run(run_case("1", baxigpt_paid=True, plan="chatgptplusplan"))
        c1 = j.status == "success"
        print(f"{'OK' if c1 else 'XX'}  [1] paid + Plus thật → success (got {j.status})")
        ok = ok and c1

        # Case 2: baxigpt paid + chưa Plus → fail terminal (override báo sai)
        j = asyncio.run(run_case("2", baxigpt_paid=True, plan="chatgptfreeplan"))
        c2 = j.status == "error" and j.error_kind == "terminal"
        print(f"{'OK' if c2 else 'XX'}  [2] paid + free → error terminal (got {j.status}/{j.error_kind})")
        ok = ok and c2

        # Case 3: baxigpt fail + Plus thật → override SUCCESS
        j = asyncio.run(run_case("3", baxigpt_paid=False, plan="chatgptplusplan"))
        c3 = j.status == "success"
        print(f"{'OK' if c3 else 'XX'}  [3] baxigpt fail + Plus thật → SUCCESS (got {j.status})")
        ok = ok and c3

        # Case 4: baxigpt fail + chưa Plus → giữ error
        j = asyncio.run(run_case("4", baxigpt_paid=False, plan="chatgptfreeplan"))
        c4 = j.status == "error"
        print(f"{'OK' if c4 else 'XX'}  [4] baxigpt fail + free → error (got {j.status})")
        ok = ok and c4

    finally:
        httpx.AsyncClient = orig_client
        svc.check_subscription = orig_check

    print("\n" + ("ALL PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
