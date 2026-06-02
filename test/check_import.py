import os
import sys

# Thêm thư mục cha (e:\\BotTele) vào sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

try:
    from gpt_signup_hybrid.config import load_settings
    from gpt_signup_hybrid.models import SignupRequest, SignupResult
    from gpt_signup_hybrid.mail_providers import build_provider_gmail_advanced
    from gpt_signup_hybrid.browser_phase import run_browser_phase
    from gpt_signup_hybrid.signup import run_signup
    from gpt_signup_hybrid.web.mail_modes import get_registry
    from gpt_signup_hybrid.web.server import app
    print("All crucial gpt_signup_hybrid imports succeeded!")
    sys.exit(0)
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
