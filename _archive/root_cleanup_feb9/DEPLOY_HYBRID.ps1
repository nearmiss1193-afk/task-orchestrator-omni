# DEPLOY_HYBRID.ps1
# Automates the "Option C" Hybrid Architecture Deployment
$SupabaseExe = "C:\Users\nearm\scoop\shims\supabase.exe"

Write-Host "EMPIRE HYBRID DEPLOYMENT PROTOCOL" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# 1. Check for Scoop
# if (!(Get-Command scoop -ErrorAction SilentlyContinue)) {
#     Write-Host "Scoop not found. Installing Scoop..." -ForegroundColor Yellow
#     Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
#     Invoke-Expression (New-Object System.Net.WebClient).DownloadString('https://get.scoop.sh')
# }

# 2. Check for Supabase CLI
# if (!(Get-Command supabase -ErrorAction SilentlyContinue)) {
#     Write-Host "Supabase CLI not found. Installing..." -ForegroundColor Yellow
#     scoop bucket add supabase https://github.com/supabase/scoop-bucket.git
#     scoop install supabase
# }

# 3. Login Check
Write-Host "`nAUTHENTICATION CHECK" -ForegroundColor Cyan
Write-Host "If a browser opens, please log in to Supabase."
& $SupabaseExe login

# 4. Link Project
# 4. Link Project
$PROJECT_ID = "rzcpfwkygdvoshtwxncs"
Write-Host "`nLinking to Project: $PROJECT_ID" -ForegroundColor Cyan
& $SupabaseExe link --project-ref $PROJECT_ID

# 5. Deploy Functions
Write-Host "`nDEPLOYING EDGE FUNCTIONS (The Nervous System)" -ForegroundColor Cyan
& $SupabaseExe functions deploy email-poller --no-verify-jwt
& $SupabaseExe functions deploy auto-responder --no-verify-jwt
& $SupabaseExe functions deploy heartbeat --no-verify-jwt

Write-Host "`nDEPLOYMENT COMPLETE" -ForegroundColor Green
Write-Host "The 'Nerves' are now running on Supabase."
