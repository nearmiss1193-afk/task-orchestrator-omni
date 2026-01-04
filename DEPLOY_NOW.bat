@echo off
echo 🛑 STOP! READ THIS CAREFULLY.
echo.
echo We need to authenticate Vercel to deploy the updates.
echo A browser window might open, or you might see a link below.
echo.
echo 1. If asked to log in, please do so.
echo 2. Wait for "Production: https://..." to appear.
echo.
cd c:\Users\nearm\.gemini\antigravity\scratch\empire-unified
call vercel deploy --prod
echo.
echo ✅ DEPLOYMENT FINISHED.
echo Now running verification (The Shopper)...
python modules/qa/link_validator.py
pause
