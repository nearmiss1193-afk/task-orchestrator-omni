
import { createClient } from '@supabase/supabase-js';
import { NextResponse } from 'next/server';

const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL || '',
    process.env.SUPABASE_SERVICE_ROLE_KEY || ''
);

/**
 * MISSION: Build the Webhook receiver (Upgraded).
 * Accepts POST requests from GHL, parses data, and saves to contacts_master.
 */
export async function POST(req: Request) {
    try {
        const payload = await req.json();
        console.log("[Webhook] Received GHL Payload:", payload);

        const trigger_type = payload.type || 'contact_created';
        const email = payload.email || payload.contact?.email;
        const website_url = payload.website || payload.contact?.website;
        const full_name = payload.name || payload.contact?.name || "Unknown Lead";
        const ghl_contact_id = payload.contact_id || payload.id;
        const phone = payload.phone || payload.contact?.phone;

        // Mapping custom fields if present
        const custom_fields = payload.customFields || payload.contact?.customFields || {};

        if (!email && !ghl_contact_id) {
            return NextResponse.json({ error: "Missing required contact data" }, { status: 400 });
        }

        const { data, error } = await supabase
            .from('contacts_master')
            .upsert({
                email,
                website_url,
                full_name,
                ghl_contact_id,
                phone,
                raw_research: { trigger: trigger_type, custom_fields },
                status: 'new'
            }, { onConflict: 'ghl_contact_id' })
            .select();

        if (error) {
            console.error("[Webhook] Supabase Error:", error);
            return NextResponse.json({ error: "Database save failed" }, { status: 500 });
        }

        return NextResponse.json({
            status: "success",
            message: "Contact captured in master table",
            contact_id: data[0]?.id
        });

    } catch (error) {
        console.error("[Webhook] Parse Error:", error);
        return NextResponse.json({ error: "Invalid payload" }, { status: 400 });
    }
}
