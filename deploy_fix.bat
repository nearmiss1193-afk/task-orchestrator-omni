@echo off
echo 🚀 Launching Sovereign Cloud Fixes...
echo.
cd c:\Users\nearm\.gemini\antigravity\scratch\empire-unified
echo 🔑 AUTHENTICATING...
call vercel deploy --prod
echo.
echo ✅ DEPLOYMENT COMPLETE.
echo check https://empire-sovereign-cloud.vercel.app/dashboard.html
pause
