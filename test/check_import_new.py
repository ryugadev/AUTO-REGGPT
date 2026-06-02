"""Kiểm tra import toàn bộ module sau khi pull code mới."""
import sys, importlib, traceback

modules = [
    "gpt_signup_hybrid",
    "gpt_signup_hybrid.models",
    "gpt_signup_hybrid.config",
    "gpt_signup_hybrid.mail_providers",
    "gpt_signup_hybrid.outlook_pool",
    "gpt_signup_hybrid.signup",
    "gpt_signup_hybrid.mfa_phase",
    "gpt_signup_hybrid.totp_helper",
    "gpt_signup_hybrid.web.server",
    "gpt_signup_hybrid.web.manager",
    "gpt_signup_hybrid.db",
    "gpt_signup_hybrid.db.engine",
    "gpt_signup_hybrid.db.schema",
    "gpt_signup_hybrid.db.repositories",
]

ok = fail = 0
for m in modules:
    try:
        importlib.import_module(m)
        print(f"✓ {m}")
        ok += 1
    except Exception as e:
        print(f"✗ {m}: {e}")
        traceback.print_exc()
        fail += 1

print(f"\n{'='*50}")
print(f"OK: {ok}  FAIL: {fail}")
sys.exit(1 if fail else 0)
