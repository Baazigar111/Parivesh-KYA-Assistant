@echo off
title PARIVESH KYA Assistant - Cloudflare Tunnel Launcher
cd /d "%~dp0"

echo ========================================================
echo   Launching PARIVESH KYA Assistant + Cloudflare Tunnel
echo ========================================================
echo.

:: Start Streamlit in the background
start "Streamlit Server" /b ".\venv\Scripts\python.exe" -m streamlit run app.py --server.port 8501 --server.headless true

:: Wait 3 seconds for Streamlit to initialize
timeout /t 3 /nobreak >nul

echo.
echo Starting secure public Cloudflare Tunnel...
echo.
cloudflared tunnel --url http://localhost:8501
pause
