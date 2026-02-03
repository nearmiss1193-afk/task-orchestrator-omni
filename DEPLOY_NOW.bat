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
echo 🔍 Running Sovereign Sentinel Link Audit...
python scripts/preflight_link_audit.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 🛑 DEPLOYMENT ABORTED: Link Integrity Violations Found!
    pause
    exit /b %ERRORLEVEL%
)

call vercel deploy --prod
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 🛑 DEPLOYMENT FAILED: Vercel returned error code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ✅ DEPLOYMENT FINISHED.
echo Now running verification (The Absolute Truth)...
python scripts/verify_deployment_truth.py
pause
