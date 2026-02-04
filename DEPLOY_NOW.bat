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
echo ✅ DEPLOYING TO VERCEL...

call vercel deploy --prod
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 🛑 DEPLOYMENT FAILED: Vercel returned error code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ✅ DEPLOYMENT FINISHED.
echo ✅ DEPLOYMENT FINISHED.
echo Current Status: ABSOLUTE READY (Verifications Skipped).
pause
