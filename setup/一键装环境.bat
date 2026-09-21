@echo off
chcp 65001 >nul
title Setup Python Environment
echo ============================================================
echo  Setting up the Python environment for this project.
echo  First run takes about 3-10 minutes. Do not close this window.
echo ============================================================
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_env.ps1" %*
echo.
if errorlevel 1 (
    echo [FAILED] Environment setup failed. See the messages above.
) else (
    echo [DONE] Close this window, then run: python code\run_all.py
)
pause
