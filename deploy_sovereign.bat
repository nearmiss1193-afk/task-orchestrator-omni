@echo off
echo ==========================================
echo   SOVEREIGN CLOUD DEPLOYMENT (VERCEL)
echo ==========================================

echo 1. Linking Project...
call vercel link --yes

echo 2. Setting Resend API Key...
echo re_LQZjuKr4_2VekoHapRGGpgemcL2fq6rTP | call vercel env add RESEND_API_KEY production
echo re_LQZjuKr4_2VekoHapRGGpgemcL2fq6rTP | call vercel env add RESEND_API_KEY preview
echo re_LQZjuKr4_2VekoHapRGGpgemcL2fq6rTP | call vercel env add RESEND_API_KEY development

echo 3. Deploying to Production...
call vercel deploy --prod

echo ==========================================
echo   DEPLOYMENT COMPLETE 🚀
echo ==========================================
pause
