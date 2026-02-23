import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabaseClient';

export const dynamic = 'force-dynamic';

export async function GET() {
    try {
        // Fetch all active bids
        const { data: bids, error: bidErr } = await supabase
            .from('bids')
            .select('*')
            .order('created_at', { ascending: false });

        if (bidErr) {
            console.error("Bid Fetch Error", bidErr);
            return NextResponse.json({ error: bidErr.message }, { status: 500 });
        }

        // Fetch contacts with a niche (potential matches)
        const { data: contacts, error: contactErr } = await supabase
            .from('contacts_master')
            .select('id, company_name, phone, niche, rating')
            .not('niche', 'is', null);

        if (contactErr) {
            console.error("Contact Fetch Error", contactErr);
            return NextResponse.json({ error: contactErr.message }, { status: 500 });
        }

        // The Matchmaker Engine: Associate bids to businesses based on category
        const enrichedBids = bids.map((bid: any) => {
            const matches = contacts.filter((c: any) => {
                if (!c.niche || !bid.category) return false;
                // case insensitive match
                return c.niche.toLowerCase().includes(bid.category.toLowerCase()) ||
                    bid.category.toLowerCase().includes(c.niche.toLowerCase());
            });

            // Generate "Money-in-Pocket" outreach scripts dynamically
            const enrichedMatches = matches.map((m: any) => {
                const script = `Hey ${m.company_name}, the City of Lakeland just posted a ${bid.estimated_budget} bid for ${bid.title}. Based on your ${m.rating}-star rating, you're a perfect match. Want the 1-page summary I made?`;
                return { ...m, outreach_script: script };
            });

            return {
                ...bid,
                matches: enrichedMatches
            };
        });

        return NextResponse.json(enrichedBids, { status: 200 });
    } catch (err: any) {
        console.error('API /bids Error:', err);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
