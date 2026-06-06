"""Guard: Auto CDK retry resume — skip login (có access_token) + skip submit (có order_id).

Chạy: .venv\\Scripts\\python.exe test\\check_autocdk_resume.py
Mock httpx + get_session để không gọi mạng/browser thật.
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
    def __init__(self, payload):
        self._p = payload
    def raise_for_status(self):
        pass
    def json(self):
        return self._p


class _Client:
    """Ghi lại các path được gọi để biết có skip verify/submit không."""
    calls = []
    table = {}
    def __init__(self, *a, **k):
        pass
    async def __aenter__(self):
        return self
    async def __aexit__(self, *a):
        return False
    async def post(self, url, json=None, headers=None):
        path = url.split("baxigpt.com")[-1]
        _Client.calls.append(path)
        if "/api/status" in path:
            return _Resp({"ok": True, "status": "paid"})
        if "/api/code-info" in path:
            return _Resp({"ok": True, "remaining": 1, "total": 1})
        if "/api/submit" in path:
            return _Resp({"ok": True, "order_id": "NEWORDER123"})
        return _Resp({"ok": False, "msg": "?"})


def main() -> int:
    import gpt_signup_hybrid.web.manager as mgr_mod
    from gpt_signup_hybrid.web.manager import AutoCdkJobManager, AutoCdkJob
    import httpx

    orig_client = httpx.AsyncClient
    httpx.AsyncClient = _Client

    # Mock get_session để fail nếu bị gọi (đảm bảo resume KHÔNG login lại)
    login_called = {"n": 0}
    async def _fake_get_session(**kwargs):
        login_called["n"] += 1
        return {"accessToken": "AT_FROM_LOGIN"}
    orig_get_session = mgr_mod.get_session
    mgr_mod.get_session = _fake_get_session

    ok = True
    try:
        mgr = AutoCdkJobManager(max_concurrent=3)

        async def run(job):
            mgr.jobs[job.id] = job
            mgr.order.append(job.id)
            await mgr._run_job(job)
            return job

        # Case 1: job có sẵn access_token + order_id → skip login + skip verify/submit
        _Client.calls = []
        login_called["n"] = 0
        j1 = AutoCdkJob(id="j1", email="a@gmail.com", password="p", cdk_key="BX-1",
                        access_token="AT_EXISTING", order_id="ORD_EXISTING")
        asyncio.run(run(j1))
        c1 = {
            "skip login (không gọi get_session)": login_called["n"] == 0,
            "skip verify (không gọi code-info)": not any("code-info" in c for c in _Client.calls),
            "skip submit (không gọi submit)": not any("submit" in c for c in _Client.calls),
            "có poll status": any("status" in c for c in _Client.calls),
            "status=success": j1.status == "success",
        }
        for k, v in c1.items():
            print(f"{'OK' if v else 'XX'}  [resume] {k}")
            ok = ok and v

        # Case 2: job có access_token nhưng CHƯA submit (order_id=None) → skip login, vẫn submit
        _Client.calls = []
        login_called["n"] = 0
        j2 = AutoCdkJob(id="j2", email="b@gmail.com", password="p", cdk_key="BX-2",
                        access_token="AT_EXISTING")
        asyncio.run(run(j2))
        c2 = {
            "skip login": login_called["n"] == 0,
            "có verify": any("code-info" in c for c in _Client.calls),
            "có submit": any("submit" in c for c in _Client.calls),
            "order_id clear sau success": j2.order_id is None,
            "status=success": j2.status == "success",
        }
        for k, v in c2.items():
            print(f"{'OK' if v else 'XX'}  [has-token] {k}")
            ok = ok and v

        # Case 3: retry_job giữ access_token + order_id
        j3 = AutoCdkJob(id="j3", email="c@gmail.com", password="p", cdk_key="BX-3",
                        access_token="AT3", order_id="ORD3", status="error", error_kind="retriable")
        mgr.jobs["j3"] = j3
        mgr.order.append("j3")
        # retry_job sẽ enqueue → cần event loop; chỉ kiểm field sau retry, hủy worker
        async def _retry_check():
            mgr.retry_job("j3")
            # drain queue để không chạy thật
            try:
                while True:
                    mgr._job_queue.get_nowait()
            except Exception:
                pass
            for w in mgr._workers:
                w.cancel()
        asyncio.run(_retry_check())
        c3 = {
            "retry giữ access_token": j3.access_token == "AT3",
            "retry giữ order_id": j3.order_id == "ORD3",
            "retry reset status=queued": j3.status == "queued",
        }
        for k, v in c3.items():
            print(f"{'OK' if v else 'XX'}  [retry] {k}")
            ok = ok and v

        # Case 4: concurrency set 3 (trong async context vì cần event loop cho workers)
        async def _conc_check():
            mgr.set_max_concurrent(3)
            val = mgr.max_concurrent
            for w in mgr._workers:
                w.cancel()
            return val
        c4 = asyncio.run(_conc_check()) == 3
        print(f"{'OK' if c4 else 'XX'}  [concurrency] set 3 OK")
        ok = ok and c4

    finally:
        httpx.AsyncClient = orig_client
        mgr_mod.get_session = orig_get_session

    print("\n" + ("ALL PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
