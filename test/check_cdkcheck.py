"""Guard cho Check CDK: phân loại live/dead/error + quota format.

Chạy: .venv\\Scripts\\python.exe test\\check_cdkcheck.py
Mock httpx để test _run_job với các response giả (không cần network).
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


class _FakeResp:
    def __init__(self, payload):
        self._p = payload
    def raise_for_status(self):
        pass
    def json(self):
        return self._p


class _FakeClient:
    """Trả response theo cdk_key trong body."""
    table: dict = {}
    def __init__(self, *a, **k):
        pass
    async def __aenter__(self):
        return self
    async def __aexit__(self, *a):
        return False
    async def post(self, url, json=None, headers=None):
        code = (json or {}).get("code")
        return _FakeResp(_FakeClient.table.get(code, {"ok": False, "msg": "卡密不存在"}))


def _patch(mgr_mod, table):
    _FakeClient.table = table
    mgr_mod.httpx = type("m", (), {"AsyncClient": _FakeClient})()  # not used; manager imports httpx locally


def main() -> int:
    from gpt_signup_hybrid.web.manager import CdkCheckJobManager, CdkCheckJob
    import gpt_signup_hybrid.web.manager as mgr_mod

    # Patch httpx ở scope module (manager dùng `import httpx` cục bộ trong _run_job)
    import httpx as real_httpx
    orig = real_httpx.AsyncClient
    real_httpx.AsyncClient = _FakeClient

    _FakeClient.table = {
        "LIVE-1": {"ok": True, "total": 1, "remaining": 1, "used": 0, "status_code": "active"},
        "DEAD-1": {"ok": True, "total": 1, "remaining": 0, "used": 1, "status_code": "used"},
        # không có NOEXIST → default ok=false
    }

    ok = True
    try:
        mgr = CdkCheckJobManager(max_concurrent=3)

        async def run_one(key):
            job = CdkCheckJob(id="j_" + key, cdk_key=key)
            mgr.jobs[job.id] = job
            mgr.order.append(job.id)
            await mgr._run_job(job)
            return job

        live = asyncio.run(run_one("LIVE-1"))
        dead = asyncio.run(run_one("DEAD-1"))
        noexist = asyncio.run(run_one("NOEXIST"))

        checks = {
            "LIVE remaining>=1 → live": live.status == "live",
            "LIVE quota 0/1": live.to_dict()["quota"] == "0/1",
            "DEAD remaining==0 → dead": dead.status == "dead",
            "DEAD quota 1/1": dead.to_dict()["quota"] == "1/1",
            "NOEXIST → error": noexist.status == "error",
            "NOEXIST dịch msg": noexist.error == "CDK không tồn tại",
        }
        for name, passed in checks.items():
            print(f"{'✓' if passed else '✗'} {name}")
            ok = ok and passed
    finally:
        real_httpx.AsyncClient = orig

    print("\n" + ("ALL PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
