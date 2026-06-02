"""Test script: Kiểm tra cú pháp, import và logic cơ bản của tính năng Check Live.

Chạy bằng command: python test/test_checker.py
"""
import sys
import os

# Thêm workspace root vào sys.path để import dễ dàng
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_imports():
    print("[-] Checking import checker_api...")
    try:
        from checker_api import check_subscription, CheckerError, TokenExpiredError, CloudflareBlockedError
        print("[+] Import checker_api success!")
        assert check_subscription is not None
        assert CheckerError is not None
        assert TokenExpiredError is not None
        assert CloudflareBlockedError is not None
    except Exception as exc:
        print(f"[!] Error importing checker_api: {exc}")
        sys.exit(1)


async def test_manager_integration():
    print("[-] Checking integration of CheckLiveJobManager in web.manager...")
    try:
        from gpt_signup_hybrid.web.manager import CheckLiveJob, CheckLiveJobManager, get_checker_manager
        print("[+] Import web.manager success!")
        
        # Test class instantiation
        manager = CheckLiveJobManager(max_concurrent=2)
        assert manager.max_concurrent == 2
        manager.set_max_concurrent(3)
        assert manager.max_concurrent == 3
        
        # Test singleton
        singleton = get_checker_manager()
        assert singleton is not None
        assert singleton.max_concurrent == 1
        
        print("[+] CheckLiveJobManager initialization and testing success!")
    except Exception as exc:
        print(f"[!] Error integrating manager: {exc}")
        sys.exit(1)


def test_server_endpoints():
    print("[-] Checking import server endpoints...")
    try:
        from gpt_signup_hybrid.web.server import AddCheckerJobsRequest, SetCheckerConfigRequest
        print("[+] Import FastAPI models success!")
        assert AddCheckerJobsRequest is not None
        assert SetCheckerConfigRequest is not None
    except Exception as exc:
        print(f"[!] Error importing server models: {exc}")
        sys.exit(1)


async def main_async():
    print("=== STARTING CHECK LIVE UNIT TESTS ===")
    test_imports()
    await test_manager_integration()
    test_server_endpoints()
    print("=== ALL CHECK LIVE INTEGRATION TESTS PASSED SUCCESSFULLY! ===")


if __name__ == "__main__":
    if __package__ is None or __package__ == "":
        import subprocess
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        python_exe = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".venv", "Scripts", "python.exe"))
        if not os.path.exists(python_exe):
            python_exe = "python"
        
        print(f"[-] Relaunching as package from parent directory: {parent_dir}")
        res = subprocess.run(
            [python_exe, "-m", "gpt_signup_hybrid.test.test_checker"],
            cwd=parent_dir,
        )
        sys.exit(res.returncode)

    import asyncio
    asyncio.run(main_async())
