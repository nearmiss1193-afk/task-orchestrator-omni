<#
.SYNOPSIS
    Ops Autofix - Production Truth Self-Correcting Script
.DESCRIPTION
    Runs verify_production.py, detects stale brand.json or forbidden numbers,
    provides operator guidance for Vercel redeploy, and checks Modal health.
#>

param(
    [int]$MaxRetries = 3,
    [switch]$SkipModalCheck
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Set-Location $ProjectRoot

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "OPS AUTOFIX - Production Truth Self-Correcting" -ForegroundColor Cyan
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host "=" * 60 -ForegroundColor Cyan

# ============================================================
# STEP 1: Check Modal Health
# ============================================================
if (-not $SkipModalCheck) {
    Write-Host "`n[1/3] Checking Modal API health..." -ForegroundColor Yellow
    
    $modalUrl = "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/health"
    try {
        $response = Invoke-RestMethod -Uri $modalUrl -TimeoutSec 10 -ErrorAction Stop
        if ($response.status -eq "ok") {
            Write-Host "   ✓ Modal API: GREEN" -ForegroundColor Green
        }
        else {
            throw "Unexpected response"
        }
    }
    catch {
        Write-Host "   ✗ Modal API: RED (not responding)" -ForegroundColor Red
        Write-Host ""
        Write-Host "=" * 60 -ForegroundColor Red
        Write-Host "MODAL FIX REQUIRED" -ForegroundColor Red
        Write-Host "=" * 60 -ForegroundColor Red
        Write-Host @"

The Modal API is not responding. This is usually caused by:
1) Old Modal apps holding cron job slots
2) Deploy failed due to workspace limits

FIX STEPS:
----------
1. Go to: https://modal.com/apps/nearmiss1193-afk

2. Delete ALL old apps (click each → Settings → Delete):
   - empire-api-v1
   - empire-api-v2
   - empire-webhooks
   - Any other apps with scheduled functions

3. Redeploy Modal:
   cd $ProjectRoot
   python -m modal deploy modal_orchestrator_v3.py

4. Verify health:
   curl.exe -s "$modalUrl"
   # Expected: {"status":"ok"}

"@ -ForegroundColor Yellow
        exit 1
    }
}

# ============================================================
# STEP 2: Check brand.json Freshness
# ============================================================
Write-Host "`n[2/3] Checking brand.json sync..." -ForegroundColor Yellow

# Get local brand.json
$localBrand = Get-Content "$ProjectRoot\public\brand.json" | ConvertFrom-Json
$localSha = $localBrand.build.sha
$localVersion = $localBrand.build.version

# Get production brand.json
try {
    $prodBrand = Invoke-RestMethod -Uri "https://www.aiserviceco.com/brand.json?ts=$([DateTimeOffset]::Now.ToUnixTimeSeconds())" -TimeoutSec 10
    $prodSha = $prodBrand.build.sha
    $prodVersion = $prodBrand.build.version
    
    if (-not $prodSha) {
        # Old schema uses git_sha
        $prodSha = $prodBrand.git_sha
    }
    
    Write-Host "   Local:      sha=$localSha version=$localVersion"
    Write-Host "   Production: sha=$prodSha version=$prodVersion"
    
    if ($prodSha -eq $localSha -and $prodVersion -eq $localVersion) {
        Write-Host "   ✓ brand.json: SYNCED" -ForegroundColor Green
        $brandSynced = $true
    }
    else {
        Write-Host "   ⚠ brand.json: STALE" -ForegroundColor Yellow
        $brandSynced = $false
    }
}
catch {
    Write-Host "   ✗ Could not fetch production brand.json" -ForegroundColor Red
    $brandSynced = $false
}

# ============================================================
# STEP 3: Run Production Verifier
# ============================================================
Write-Host "`n[3/3] Running production verifier..." -ForegroundColor Yellow

$attempt = 0
$success = $false

while ($attempt -lt $MaxRetries -and -not $success) {
    $attempt++
    Write-Host "`n   Attempt $attempt/$MaxRetries..." -ForegroundColor Gray
    
    $result = python verify_production.py 2>&1
    $exitCode = $LASTEXITCODE
    
    # Parse result for status
    if ($result -match "Status: GREEN") {
        Write-Host "   ✓ Production Verifier: GREEN" -ForegroundColor Green
        $success = $true
    }
    elseif ($result -match "Status: YELLOW") {
        Write-Host "   ⚠ Production Verifier: YELLOW (warnings only)" -ForegroundColor Yellow
        $success = $true
    }
    else {
        Write-Host "   ✗ Production Verifier: RED" -ForegroundColor Red
        
        if (-not $brandSynced -or $attempt -eq 1) {
            Write-Host ""
            Write-Host "=" * 60 -ForegroundColor Yellow
            Write-Host "VERCEL REDEPLOY REQUIRED (without build cache)" -ForegroundColor Yellow
            Write-Host "=" * 60 -ForegroundColor Yellow
            Write-Host @"

Production is serving stale content. Follow these steps:

OPTION A - Vercel Dashboard (Recommended):
------------------------------------------
1. Go to: https://vercel.com/nearmiss1193-9477s-projects/empire-unified
2. Click "Deployments" tab
3. Find latest deployment → Click "..." menu → "Redeploy"
4. CHECK the box "Redeploy with existing Build Cache" is UNCHECKED
5. Click "Redeploy"
6. Wait 30-60 seconds

OPTION B - Force CLI Deploy:
----------------------------
npx vercel --prod --force

After redeploy, press ENTER to verify again...
"@ -ForegroundColor Cyan
            
            if ($attempt -lt $MaxRetries) {
                Read-Host "Press ENTER after Vercel redeploy"
            }
        }
    }
}

# ============================================================
# FINAL RESULT
# ============================================================
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "RESULT" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

if ($success) {
    Write-Host "✓ All checks PASSED" -ForegroundColor Green
    Write-Host ""
    Write-Host "Dashboard: https://www.aiserviceco.com/dashboard.html"
    exit 0
}
else {
    Write-Host "✗ Verification FAILED after $MaxRetries attempts" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual investigation required. Check:" -ForegroundColor Yellow
    Write-Host "  1. Vercel project settings (correct repo/branch?)"
    Write-Host "  2. build.json in repo root"
    Write-Host "  3. public/ folder contents"
    exit 1
}
