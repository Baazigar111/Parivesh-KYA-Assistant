@echo off
title PARIVESH KYA Assistant - ngrok Static Tunnel Launcher
cd /d "%~dp0"

echo ========================================================
echo   Cleaning existing processes on port 8501...
echo ========================================================
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM streamlit.exe >nul 2>&1
taskkill /F /IM ngrok.exe >nul 2>&1

echo.
echo ========================================================
echo   Launching PARIVESH KYA Assistant + ngrok Tunnel
echo ========================================================
echo.

:: 1. Start Streamlit in a separate command window
start "PARIVESH Streamlit Backend" ".\venv\Scripts\python.exe" -m streamlit run app.py --server.port 8501 --server.headless true

:: 2. Wait 4 seconds for Streamlit to bind to 8501
timeout /t 4 /nobreak >nul

echo.
echo Starting secure public tunnel at:
echo https://glitter-scrambled-defensive.ngrok-free.dev
echo.

:: 3. Launch ngrok using your static domain
ngrok.exe http --domain=glitter-scrambled-defensive.ngrok-free.dev 8501

pause