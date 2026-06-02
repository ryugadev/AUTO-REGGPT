"""Test script để kiểm tra imports và cấu hình."""
import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print()

try:
    import pydantic
    print(f"[OK] pydantic {pydantic.__version__}")
except ImportError as e:
    print(f"[ERR] pydantic: {e}")

try:
    import typer
    print(f"[OK] typer")
except ImportError as e:
    print(f"[ERR] typer: {e}")

try:
    import httpx
    print(f"[OK] httpx")
except ImportError as e:
    print(f"[ERR] httpx: {e}")

try:
    import curl_cffi
    print(f"[OK] curl_cffi")
except ImportError as e:
    print(f"[ERR] curl_cffi: {e}")

try:
    import pyotp
    print(f"[OK] pyotp")
except ImportError as e:
    print(f"[ERR] pyotp: {e}")

try:
    import fastapi
    print(f"[OK] fastapi")
except ImportError as e:
    print(f"[ERR] fastapi: {e}")

try:
    import uvicorn
    print(f"[OK] uvicorn")
except ImportError as e:
    print(f"[ERR] uvicorn: {e}")

try:
    import camoufox
    print(f"[OK] camoufox")
except ImportError as e:
    print(f"[ERR] camoufox: {e}")

try:
    import playwright
    print(f"[OK] playwright")
except ImportError as e:
    print(f"[ERR] playwright: {e}")

print()
print("Testing gpt_signup_hybrid imports...")
try:
    from gpt_signup_hybrid.models import SignupRequest, SignupResult
    print("[OK] gpt_signup_hybrid.models")
except ImportError as e:
    print(f"[ERR] gpt_signup_hybrid.models: {e}")

try:
    from gpt_signup_hybrid.config import load_settings
    print("[OK] gpt_signup_hybrid.config")
    settings = load_settings()
    print(f"  - Runtime dir: {settings.runtime_dir}")
    print(f"  - Browser engine: {settings.browser_engine}")
except ImportError as e:
    print(f"[ERR] gpt_signup_hybrid.config: {e}")

print()
print("All checks completed!")
