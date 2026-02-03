# Smoke Test: SMS Pipeline
# Run this to verify the SMS system is working end-to-end

$BaseUrl = "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run"
$CanonicalVoice = "+18632132505"
$CanonicalSms = "+13527585336"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "SMS PIPELINE SMOKE TEST" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "[1/5] Testing /health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$BaseUrl/health" -TimeoutSec 30
    if ($health.status -eq "ok") {
        Write-Host "  ✅ PASS: API is healthy" -ForegroundColor Green
    }
    else {
        Write-Host "  ❌ FAIL: API unhealthy" -ForegroundColor Red
    }
}
catch {
    Write-Host "  ❌ FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Routing Truth
Write-Host "[2/5] Testing /api/routing/truth..." -ForegroundColor Yellow
try {
    $truth = Invoke-RestMethod -Uri "$BaseUrl/api/routing/truth" -TimeoutSec 30
    $voiceOk = $truth.canonical_voice_number -eq $CanonicalVoice
    $smsOk = $truth.canonical_sms_number -eq $CanonicalSms
    if ($voiceOk -and $smsOk) {
        Write-Host "  ✅ PASS: Canonical numbers correct" -ForegroundColor Green
        Write-Host "     Voice: $($truth.canonical_voice_number)" -ForegroundColor Gray
        Write-Host "     SMS: $($truth.canonical_sms_number)" -ForegroundColor Gray
    }
    else {
        Write-Host "  ❌ FAIL: Number mismatch" -ForegroundColor Red
    }
}
catch {
    Write-Host "  ❌ FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: SMS Reply Generation
Write-Host "[3/5] Testing /api/sms/reply-text..." -ForegroundColor Yellow
try {
    $body = @{
        phone          = "+15551234567"
        message        = "SYNTHETIC_TEST: I need help with AI automation"
        contactId      = "synthetic"
        conversationId = "synthetic"
    } | ConvertTo-Json
    
    $reply = Invoke-RestMethod -Uri "$BaseUrl/api/sms/reply-text" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
    
    if ($reply.ok -eq $true -and $reply.reply_text.Length -gt 20) {
        Write-Host "  ✅ PASS: AI reply generated" -ForegroundColor Green
        Write-Host "     Length: $($reply.reply_text.Length) chars" -ForegroundColor Gray
        Write-Host "     Preview: $($reply.reply_text.Substring(0, [Math]::Min(60, $reply.reply_text.Length)))..." -ForegroundColor Gray
    }
    elseif ($reply.reply_text.Length -gt 10) {
        Write-Host "  ⚠️ WARN: Reply generated but ok=false" -ForegroundColor Yellow
        Write-Host "     Error: $($reply.error)" -ForegroundColor Gray
    }
    else {
        Write-Host "  ❌ FAIL: Empty or short reply" -ForegroundColor Red
    }
}
catch {
    Write-Host "  ❌ FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: SMS Health
Write-Host "[4/5] Testing /api/sms/health..." -ForegroundColor Yellow
try {
    $smsHealth = Invoke-RestMethod -Uri "$BaseUrl/api/sms/health" -TimeoutSec 30
    if ($smsHealth.sms_pipeline_healthy -eq $true) {
        Write-Host "  ✅ PASS: SMS pipeline healthy" -ForegroundColor Green
    }
    else {
        Write-Host "  ⚠️ WARN: Pipeline has issues" -ForegroundColor Yellow
        Write-Host "     Unreplied: $($smsHealth.unreplied_count_60s)" -ForegroundColor Gray
    }
}
catch {
    Write-Host "  ❌ FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Website Phone Numbers
Write-Host "[5/5] Testing website phone numbers..." -ForegroundColor Yellow
try {
    $web = Invoke-WebRequest -Uri "https://www.aiserviceco.com" -UseBasicParsing -TimeoutSec 30
    $hasVoice = $web.Content -match "863.213.2505|863-213-2505|\(863\) 213-2505"
    $hasSms = $web.Content -match "352.758.5336|352-758-5336|\(352\) 758-5336"
    
    if ($hasVoice -and $hasSms) {
        Write-Host "  ✅ PASS: Both canonical numbers found on website" -ForegroundColor Green
    }
    elseif ($hasVoice -or $hasSms) {
        Write-Host "  ⚠️ WARN: Only one number found" -ForegroundColor Yellow
        Write-Host "     Voice: $hasVoice, SMS: $hasSms" -ForegroundColor Gray
    }
    else {
        Write-Host "  ❌ FAIL: No canonical numbers found" -ForegroundColor Red
    }
}
catch {
    Write-Host "  ❌ FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "SMOKE TEST COMPLETE" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
