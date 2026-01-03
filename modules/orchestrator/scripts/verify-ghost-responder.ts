
import axios from 'axios';
import { createClient } from '@supabase/supabase-js';
import * as dotenv from 'dotenv';

dotenv.config({ path: '.env.local' });

const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL || '',
    process.env.SUPABASE_SERVICE_ROLE_KEY || ''
);

const WEBHOOK_URL = "https://nearmiss1193-afk--ghl-omni-automation-ghl-webhook.modal.run";

async function verifyGhostResponder() {
    console.log("🧪 Verifying Ghost Responder (Turbo Mode)...");

    const { data: contact } = await supabase.from('contacts_master').select('ghl_contact_id').limit(1).single();
    if (!contact) {
        console.error("❌ No contact found in Supabase. Create one first.");
        return;
    }

    const contactId = contact.ghl_contact_id;
    console.log(`Using Contact ID: ${contactId}`);

    const payload = {
        type: "InboundMessage",
        contact_id: contactId,
        message: {
            body: "that sounds interesting, how do I sign up or get more info?",
            provider: "sms"
        }
    };

    try {
        console.log("📡 Sending Mock Webhook...");
        const res = await axios.post(WEBHOOK_URL, payload);
        console.log("Webhook Response:", res.data);

        console.log("⏳ Waiting 10s for AI processing...");
        await new Promise(r => setTimeout(r, 10000));

        console.log("🔍 Checking staged_replies table...");
        const { data: reply, error } = await supabase
            .from('staged_replies')
            .select('*')
            .eq('contact_id', contactId)
            .order('created_at', { ascending: false })
            .limit(1)
            .single();

        if (error) throw error;

        console.log("✅ Ghost Responder Result:");
        console.log(`- Status: ${reply.status}`);
        console.log(`- Draft: ${reply.draft_content}`);
        console.log(`- Confidence: ${reply.confidence}`);

        if (reply.status === 'sent') {
            console.log("🚀 SUCCESS: Turbo Mode Auto-Sent the reply!");
        } else {
            console.log("⚠️ STAGED: Reply requires manual approval (confidence below threshold).");
        }

    } catch (e: any) {
        console.error("❌ Verification Failed:", e.message);
    }
}

verifyGhostResponder();
