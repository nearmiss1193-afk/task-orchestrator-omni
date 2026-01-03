@echo off
echo ==========================================
echo      💾 SOVEREIGN SAVE PROTOCOL 💾
echo ==========================================
echo.

echo [1/4] Staging all files...
git add .

echo [2/4] Committing to local ledger...
set "timestamp=%date% %time%"
git commit -m "Sovereign Save: %timestamp%"

echo [3/4] Pushing to The Vault (GitHub)...
git push origin main

echo [4/4] Deploying to Cloud (Vercel)...
call vercel deploy --prod

echo [5/5] Notifying Stakeholders (Emailing Protocols)...
python modules/comms/notify_save_status.py

echo.
echo ==========================================
echo      ✅ PROTOCOL COMPLETE: SYSTEM SECURE
echo ==========================================
pause
