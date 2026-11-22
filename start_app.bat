@echo off
title Tata AIA Life Insurance - Auto Form Filler
color 0B
echo ================================================================
echo           TATA AIA LIFE INSURANCE - AUTO FORM FILLER
echo ================================================================
echo.
echo Starting OCR and Handwriting Form Filling Server...
echo Starting 5G Cloud Tunnel for Samsung Galaxy Phone...
echo.

cd /d "%~dp0"

:: Start Cloudflare 5G tunnel in background window (explicit IPv4 to prevent IPv6 refusal)
start "Tata AIA 5G Cloud Tunnel" /min cloudflared.exe tunnel --url http://127.0.0.1:8000

:: Start web dashboard
start "" http://localhost:8000

:: Start FastAPI backend
python server.py
pause
