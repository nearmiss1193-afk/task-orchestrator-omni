const { execSync } = require('child_process');

const envs = {
    "NEXT_PUBLIC_SUPABASE_URL": "https://rzcpfwkygdvoshtwxncs.supabase.co",
    "NEXT_PUBLIC_SUPABASE_ANON_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo",
    "SUPABASE_SERVICE_ROLE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo",
    "VAPI_PRIVATE_KEY": "c23c884d-0008-4b14-ad5d-530e98d0c9da",
    "TWILIO_ACCOUNT_SID": "ACc18098596806342a3047c5b841288a55",
    "TWILIO_AUTH_TOKEN": "709de5fed508fdb4fa7fd0a7d9284228",
    "TWILIO_FROM_NUMBER": "+18632608351",
    "RESEND_API_KEY": "re_6q5Rx16W_NJbL5Mj44uFy6u1e1MFAq8gy",
    "AYRSHARE_API_KEY": "7488VFR-7T04PE9-J4GF3D5-3VHQ0A3" // Make sure this is fine
};

console.log("Starting Vercel Cloud Environment Repair (Patch 2) ...");

for (const [key, value] of Object.entries(envs)) {
    console.log(`Repairing ${key}...`);
    try {
        execSync(`vercel env rm ${key} production -y`, { stdio: 'ignore' });
    } catch (e) { }

    try {
        const out = execSync(`vercel env add ${key} production`, { input: value, stdio: 'pipe' });
        console.log(`✅ Successfully injected ${key}: ${out.toString().trim()}`);
    } catch (e) {
        console.error(`❌ Failed to inject ${key}`);
    }
}

console.log("Vercel Cloud Repair Complete. Triggering Redepoyment...");
try {
    execSync('vercel --prod --yes', { stdio: 'inherit' });
} catch (e) { }
