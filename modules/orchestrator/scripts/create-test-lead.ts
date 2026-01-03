import * as dotenv from 'dotenv';
import * as path from 'path';
import { supabase } from '../lib/supabase';

// Load environment variables
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function createTestLead() {
    console.log('--- CREATING TEST LEAD ---');

    const testLead = {
        email: 'test@example.com',
        website_url: 'https://example.com',
        status: 'new'
    };

    try {
        const { data, error } = await supabase
            .from('leads')
            .upsert([testLead], { onConflict: 'email' })
            .select();

        if (error) throw error;

        console.log('[SUCCESS] Test lead created/reset:', data);
    } catch (error: any) {
        console.error('Failed to create test lead:', error.message);
    }
}

createTestLead();
