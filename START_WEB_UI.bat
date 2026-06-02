@echo off
REM Quick start script - Khởi động Web UI nhanh
REM Double-click file này để chạy Web UI

cd /d "%~dp0"

echo ═══════════════════════════════════════════════════════════
echo   gpt_signup_hybrid - Web UI
echo   Starting server at http://127.0.0.1:8089/
echo ═══════════════════════════════════════════════════════════
echo.
echo Press Ctrl+C to stop the server
echo.

.venv\Scripts\python -m gpt_signup_hybrid web --host 127.0.0.1 --port 8089

pause
