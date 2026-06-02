@echo off
REM Stop Web UI - Tắt server

cd /d "%~dp0"

echo ═══════════════════════════════════════════════════════════
echo   Stopping Web UI...
echo ═══════════════════════════════════════════════════════════
echo.

echo Killing Python processes...
taskkill /F /IM python.exe 2>nul

if %errorlevel% equ 0 (
    echo.
    echo ═══════════════════════════════════════════════════════════
    echo   √ Web UI stopped successfully!
    echo ═══════════════════════════════════════════════════════════
) else (
    echo.
    echo ═══════════════════════════════════════════════════════════
    echo   - No Web UI process found (already stopped)
    echo ═══════════════════════════════════════════════════════════
)

echo.
pause
