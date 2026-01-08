import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

serve(async (req) => {
    const body = await req.json()

    // Resend sends array of events or single object depending on version. 
    // We assume single object for simplicity or handle array.
    const event = body

    const supabase = createClient(
        Deno.env.get('SUPABASE_URL') ?? '',
        Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    if (event.type === 'email.opened' || event.type === 'email.clicked') {
        const email = event.data.to[0]
        console.log(`Email ${event.type} by ${email}`)

        // Log to leads table metadata
        // Ideally we'd have a separate 'email_logs' table, but updating metadata is a quick win for v2

        // 1. Fetch current metadata
        const { data: lead } = await supabase.from('leads').select('metadata').eq('email', email).single()

        if (lead) {
            const newMeta = lead.metadata || {}
            newMeta.email_interactions = newMeta.email_interactions || []
            newMeta.email_interactions.push({
                type: event.type,
                timestamp: event.created_at,
                url: event.data.link_url // Only for clicks
            })

            await supabase.from('leads').update({ metadata: newMeta }).eq('email', email)
        }
    }

    return new Response("OK", { status: 200 })
})
