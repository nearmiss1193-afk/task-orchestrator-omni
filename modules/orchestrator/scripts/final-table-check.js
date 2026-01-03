const axios = require('axios');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function createTableInPublic() {
    const url = `${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/rpc/execute_sql`; // Note: This requires a custom RPC, which we don't have.
    // Instead, let's try to just use the standard creation script if the user can do it.
    // But since I want to be proactive, I'll try to use the REST API to see if I can create it.
    // Standard Supabase REST API doesn't allow DDL.

    console.log("CRITICAL: Supabase REST API does not allow table creation.");
    console.log("The user's screenshot showed the table in a schema called 'api' but our REST endpoint is looking at 'public'.");
    console.log("I will try one more time to check if 'public.leads' exists after a potential cache refresh.");

    const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
    const checkUrl = `${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/leads?select=*`;

    try {
        const response = await axios.get(checkUrl, {
            headers: { 'apikey': key, 'Authorization': `Bearer ${key}` }
        });
        console.log("✅ TABLE FOUND IN PUBLIC!");
        return true;
    } catch (err) {
        console.log("❌ Table still not in public.");
        return false;
    }
}

createTableInPublic();
