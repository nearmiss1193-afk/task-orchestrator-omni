const axios = require('axios');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function checkAnitgravity() {
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
    const schemas = ['public', 'api'];

    for (const schema of schemas) {
        const url = `${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/anitgravity?select=*`;
        console.log(`Checking 'anitgravity' in schema '${schema}'...`);

        try {
            const response = await axios.get(url, {
                headers: {
                    'apikey': key,
                    'Authorization': `Bearer ${key}`,
                    'Accept-Profile': schema
                }
            });

            console.log(`✅ FOUND! Schema: ${schema}`);
            console.log('Columns:', Object.keys(response.data[0] || {}));
            return;
        } catch (err) {
            console.log(`❌ Not in '${schema}':`, err.response?.data?.message || err.message);
        }
    }
}

checkAnitgravity();
