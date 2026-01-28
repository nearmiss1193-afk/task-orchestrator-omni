// supabase/functions/ensure-campaign-running/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

const MODAL_API = "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run"
const ADMIN_TOKEN = "aiserviceco-admin-2026"  // Corrected admin token

serve(async (req) => {
    const supabase = createClient(
        Deno.env.get("SUPABASE_URL")!,
        Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
    )

    // Get current EST time
    const now = new Date()
    const estTime = new Date(now.toLocaleString("en-US", { timeZone: "America/New_York" }))
    const hour = estTime.getHours()
    const day = estTime.getDay()

    // Log the check
    await supabase.from("scheduler_logs").insert({
        checked_at: now.toISOString(),
        hour,
        day,
        source: "edge_function"
    })

    // Business hours: 8 AM - 8 PM, Mon-Sat (day 1-6, excluding Sunday 0)
    const shouldBeRunning = hour >= 8 && hour < 20 && day >= 1 && day <= 6

    if (!shouldBeRunning) {
        return new Response(JSON.stringify({
            status: "outside_hours",
            hour,
            day,
            message: "Campaign not needed right now"
        }), {
            headers: { "Content-Type": "application/json" }
        })
    }

    // Check current state
    try {
        const stateRes = await fetch(`${MODAL_API}/api/control/state`, {
            signal: AbortSignal.timeout(10000)
        })
        const state = await stateRes.json()

        // Parse campaign_mode - it comes back as escaped JSON string like "\"running\""
        let campaignMode = state?.states?.campaign_mode
        if (typeof campaignMode === "string") {
            // Remove extra quotes if present
            campaignMode = campaignMode.replace(/^"|"$/g, "").replace(/\\"/g, "")
        }

        if (campaignMode === "running") {
            return new Response(JSON.stringify({
                status: "already_running",
                campaign_mode: campaignMode,
                state: state.states
            }), {
                headers: { "Content-Type": "application/json" }
            })
        }

        // Campaign not running during business hours - START IT
        console.log("Campaign not running, starting...")

        const startRes = await fetch(`${MODAL_API}/api/control/campaign/start`, {
            method: "POST",
            headers: {
                "X-Admin-Token": ADMIN_TOKEN,
                "Content-Type": "application/json"
            },
            signal: AbortSignal.timeout(10000)
        })

        const result = await startRes.json()

        // Log the auto-start
        await supabase.from("event_log_v2").insert({
            event_type: "campaign.auto_started",
            source: "scheduler_edge_function",
            payload: { hour, day, result, previous_state: campaignMode }
        })

        return new Response(JSON.stringify({
            status: "started",
            result,
            hour,
            day
        }), {
            headers: { "Content-Type": "application/json" }
        })

    } catch (error) {
        // Log the error
        await supabase.from("event_log_v2").insert({
            event_type: "scheduler.error",
            source: "scheduler_edge_function",
            payload: { error: error.message, hour, day }
        })

        // TODO: Send alert to Dan

        return new Response(JSON.stringify({
            status: "error",
            error: error.message
        }), {
            status: 500,
            headers: { "Content-Type": "application/json" }
        })
    }
})
