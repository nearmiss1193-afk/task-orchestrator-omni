$env:MODAL_TOKEN_ID = "ak-FY8edcLOBMQB2IYo8M9avy"
$env:MODAL_TOKEN_SECRET = "as-PoM8MK4hlweaVPdWRIFbki"

Write-Host "Stopping conflicting Modal apps to free up Cron slots..."

# empire-api-v3 (Created Jan 21)
Write-Host "Stopping empire-api-v3..."
python -m modal app stop empire-api-v3

# empire-overseer (Created Jan 22 - likely duplicates Orchestrator logic)
Write-Host "Stopping empire-overseer..."
python -m modal app stop empire-overseer

# v2-outreach-engine (Ephemeral/Stuck)
Write-Host "Stopping v2-outreach-engine..."
python -m modal app stop v2-outreach-engine

Write-Host "Cleanup Complete!"
Write-Host "You can now run .\DEPLOY_ORCHESTRATOR.ps1" -ForegroundColor Green
Read-Host "Press Enter to exit..."
