
import { createClient } from '@supabase/supabase-js';
import * as dotenv from 'dotenv';
import axios from 'axios';

dotenv.config({ path: '.env.local' });

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;
const supabase = createClient(supabaseUrl, supabaseKey);

const GHL_API_TOKEN = process.env.GHL_API_TOKEN || process.env.GHL_PRIVATE_KEY;

async function approveAll() {
    console.log("🚀 Starting Turbo Approval Loop...");

    // 1. Fetch all pending replies
    const { data: pending, error } = await supabase
        .table('staged_replies')
        .select('*')
        .eq('status', 'pending_approval');

    if (error) {
        console.error("❌ Error fetching pending replies:", error);
        return;
    }

    if (!pending || pending.length === 0) {
        console.log("✅ No replies pending approval.");
        return;
    }

    console.log(`📝 Found ${pending.length} replies to approve.`);

    for (const reply of pending) {
        try {
            console.log(`📤 Sending reply to contact ${reply.contact_id}...`);

            // 2. Dispatch via GHL API
            const ghlUrl = "https://services.leadconnectorhq.com/conversations/messages";
            const response = await axios.post(ghlUrl, {
                type: reply.platform || "SMS",
                contactId: reply.contact_id,
                body: reply.draft_content
            }, {
                headers: {
                    'Authorization': `Bearer ${GHL_API_TOKEN}`,
                    'Version': '2021-04-15',
                    'Content-Type': 'application/json'
                }
            });

            if (response.status === 200 || response.status === 201) {
                console.log(`✅ Sent successfully to ${reply.contact_id}`);

                // 3. Update status in Supabase
                await supabase
                    .table('staged_replies')
                    .update({ status: 'sent', sent_at: new Date().toISOString() })
                    .eq('id', reply.id);
            } else {
                console.error(`⚠️ Failed to send to ${reply.contact_id}:`, response.data);
            }
        } catch (err: any) {
            console.error(`❌ Error processing reply ${reply.id}:`, err.response?.data || err.message);
        }
    }

    console.log("🏁 Turbo Approval Mission Complete.");
}

approveAll();
