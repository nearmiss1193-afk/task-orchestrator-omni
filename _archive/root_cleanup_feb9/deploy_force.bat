@echo off
echo 🚀 FORCING SOVEREIGN CLOUD DEPLOYMENT...
echo.
cd c:\Users\nearm\.gemini\antigravity\scratch\empire-unified
echo 🔑 AUTHENTICATING AND DEPLOYING (FORCE)...
call vercel deploy --prod --force
echo.
echo ✅ DEPLOYMENT COMPLETE.
echo check https://empire-sovereign-cloud.vercel.app/hvac.html
pause
