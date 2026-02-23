import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabaseClient';

export const dynamic = 'force-dynamic';

export async function GET() {
    try {
        // Fetch upcoming/recent estate sales
        const { data: sales, error: salesErr } = await supabase
            .from('estate_sales')
            .select('*')
            .order('created_at', { ascending: false });

        if (salesErr) {
            console.error("Estate Sales Fetch Error", salesErr);
            return NextResponse.json({ error: salesErr.message }, { status: 500 });
        }

        // Fetch contacts for matchmaking (Realtors, Junk Removal, etc.)
        const { data: contacts, error: contactErr } = await supabase
            .from('contacts_master')
            .select('id, company_name, phone, niche, rating')
            .not('niche', 'is', null);

        if (contactErr) {
            console.error("Contact Fetch Error", contactErr);
            return NextResponse.json({ error: contactErr.message }, { status: 500 });
        }

        // Matchmaker Logic
        const enrichedSales = sales.map((sale: any) => {
            const matches = contacts.filter((c: any) => {
                if (!c.niche || !sale.intent_classification) return false;

                const nicheUpper = c.niche.toUpperCase();
                const intentUpper = sale.intent_classification.toUpperCase();

                // Realtors want Moving / Estate clearing
                if (nicheUpper.includes('REAL ESTATE') || nicheUpper.includes('REALTOR')) {
                    return intentUpper.includes('MOVING') || intentUpper.includes('ESTATE CLEARING');
                }

                // Junk Removers want everything, but especially garage/liquidation
                if (nicheUpper.includes('JUNK REMOVAL') || nicheUpper.includes('CLEAN OUT')) {
                    return true;
                }

                return false;
            });

            const enrichedMatches = matches.map((m: any) => {
                // Dynamic Outreach Scripting based on Niche
                let script = "";
                if (m.niche.toUpperCase().includes('REAL ESTATE') || m.niche.toUpperCase().includes('REALTOR')) {
                    script = `Hey ${m.company_name}, verified Moving Sale happening this weekend at ${sale.address || 'Lakeland'}. Usually means a listing is imminent. Do you want the homeowner dossier?`;
                } else if (m.niche.toUpperCase().includes('JUNK REMOVAL')) {
                    script = `Hey ${m.company_name}, huge ${sale.sale_type} ending this weekend in Lakeland. Want me to ping them Sunday afternoon offering to haul the leftover trash?`;
                } else {
                    script = `Hey ${m.company_name}, new high-intent event (${sale.sale_type}) detected. Related to your niche?`;
                }
                return { ...m, outreach_script: script };
            });

            return {
                ...sale,
                matches: enrichedMatches
            };
        });

        return NextResponse.json(enrichedSales, { status: 200 });
    } catch (err: any) {
        console.error('API /intents Error:', err);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
