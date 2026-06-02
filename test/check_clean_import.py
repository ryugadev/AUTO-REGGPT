"""Check that all refactored modules in app/ and their compatibility wrappers at root import successfully without errors."""
from __future__ import annotations
import sys
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root))
    
    modules_to_test = [
        # New app modules
        "app.core.config",
        "app.core.settings",
        "app.core.constants",
        "app.core.logging",
        "app.core.exceptions",
        "app.models",
        "app.models.account",
        "app.models.session",
        "app.models.result",
        "app.workflows.browser_workflow",
        "app.workflows.http_workflow",
        "app.workflows.session_workflow",
        "app.workflows.mfa_workflow",
        "app.workflows.signup_workflow",
        "app.providers.mail.base",
        "app.providers.mail.worker_provider",
        "app.providers.mail.outlook_provider",
        "app.providers.mail.gmail_provider",
        "app.providers.otp.gmail_otp_provider",
        "app.services.payment_service",
        "app.services.checker_service",
        "app.infrastructure.database",
        "app.infrastructure.database.engine",
        "app.infrastructure.database.schema",
        "app.infrastructure.database.repositories",
        "app.infrastructure.database.migrate",
        "app.infrastructure.browser.retry",
        "app.infrastructure.browser.nextauth",
        "app.utils.helpers",
        
        # Compatibility wrappers at root
        "config",
        "models",
        "browser_phase",
        "http_phase",
        "session_phase",
        "mfa_phase",
        "mail_providers",
        "auto_gmail_otp_provider",
        "payment_link",
        "checker_api",
        "signup",
        "totp_helper",
        "random_profile",
        "db",
    ]
    
    failed = False
    print("Testing module imports...")
    for mod_name in modules_to_test:
        try:
            __import__(mod_name)
            print(f"  [OK]  {mod_name}")
        except Exception as exc:
            print(f"  [ERR] {mod_name}: {exc}")
            import traceback
            traceback.print_exc()
            failed = True
            
    if failed:
        print("Import check failed.")
        sys.exit(1)
    else:
        print("All modules imported successfully without errors!")
        sys.exit(0)

if __name__ == "__main__":
    main()
