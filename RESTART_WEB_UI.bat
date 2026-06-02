@echo off
REM Restart Web UI - Tắt và bật lại server

cd /d "%~dp0"

echo ═══════════════════════════════════════════════════════════
echo   Restarting Web UI...
echo ═══════════════════════════════════════════════════════════
echo.

echo [1/3] Stopping old processes...
taskkill /F /IM python.exe 2>nul
if %errorlevel% equ 0 (
    echo   √ Stopped
) else (
    echo   - No process running
)

echo.
echo [2/3] Waiting 3 seconds...
timeout /t 3 /nobreak >nul
echo   √ Ready

echo.
echo [3/3] Starting Web UI...
echo   → http://127.0.0.1:8089/
echo.

.venv\Scripts\python -m gpt_signup_hybrid web --host 127.0.0.1 --port 8089

pause
