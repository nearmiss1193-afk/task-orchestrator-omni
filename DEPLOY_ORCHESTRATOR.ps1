$env:MODAL_TOKEN_ID = "ak-FY8edcLOBMQB2IYo8M9avy"
$env:MODAL_TOKEN_SECRET = "as-PoM8MK4hlweaVPdWRIFbki"

Write-Host "Deploying v2-master-orchestrator to Modal..."
python -m modal deploy execution.v2.v2_orchestrator

if ($LASTEXITCODE -ne 0) {
    Write-Host "Deployment failed!" -ForegroundColor Red
} else {
    Write-Host "Deployment SUCCESS!" -ForegroundColor Green
}
Read-Host "Press Enter to exit..."
