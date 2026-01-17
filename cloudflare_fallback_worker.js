// AGENT: Cloudflare Webhook Fallback Worker
// Edge webhook endpoint with primary/fallback routing
// Returns structured JSON only

export default {
    // Scheduled trigger - runs every 2 hours to trigger self-improvement optimizer
    async scheduled(event, env, ctx) {
        const optimizeUrl = (env.PRIMARY_URL || "https://nearmiss1193-afk--empire-api-v1-orchestration-api.modal.run") + "/optimize";
        try {
            const response = await fetch(optimizeUrl, { method: "GET", headers: { "Content-Type": "application/json" } });
            const result = await response.json();
            console.log("Self-improvement optimizer result:", JSON.stringify(result));

            // Log to Supabase
            const supabaseUrl = env.SUPABASE_URL || "https://rzcpfwkygdvoshtwxncs.supabase.co";
            const supabaseKey = env.SUPABASE_KEY || "";
            if (supabaseKey) {
                await fetch(`${supabaseUrl}/rest/v1/cron_logs`, {
                    method: "POST",
                    headers: { "apikey": supabaseKey, "Authorization": `Bearer ${supabaseKey}`, "Content-Type": "application/json" },
                    body: JSON.stringify({ trigger: "scheduled", action: "self_improvement_optimizer", result: result, timestamp: new Date().toISOString() })
                });
            }
        } catch (e) {
            console.error("Scheduled optimizer trigger failed:", e.message);
        }
    },

    async fetch(request, env, ctx) {
        const timestamp = new Date().toISOString();

        // Reject non-POST
        if (request.method !== "POST") {
            return new Response(JSON.stringify({
                timestamp,
                source: "webhook",
                forwarded_to: "none",
                status: "error",
                error: "method_not_allowed"
            }), { status: 405, headers: { "Content-Type": "application/json" } });
        }

        const body = await request.text();
        let payload;
        try {
            payload = JSON.parse(body);
        } catch {
            payload = { raw: body };
        }

        // Verify signature if present
        const signature = request.headers.get("X-Hub-Signature-256") ||
            request.headers.get("X-Twilio-Signature") ||
            request.headers.get("X-GHL-Signature");

        if (env.WEBHOOK_SECRET && signature) {
            // HMAC verification (optional, logged only)
            const encoder = new TextEncoder();
            try {
                const key = await crypto.subtle.importKey(
                    "raw", encoder.encode(env.WEBHOOK_SECRET),
                    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
                );
                const sig = await crypto.subtle.sign("HMAC", key, encoder.encode(body));
                const expected = "sha256=" + [...new Uint8Array(sig)].map(b => b.toString(16).padStart(2, "0")).join("");
                if (signature !== expected) {
                    console.log("Signature mismatch (continuing anyway)");
                }
            } catch (e) {
                console.log("Signature check error:", e.message);
            }
        }

        const primaryUrl = env.PRIMARY_URL || "https://nearmiss1193-afk--sovereign-orchestrator-webhook.modal.run";
        const fallbackUrl = env.FALLBACK_URL || "https://empire-fallback-runner.up.railway.app/webhook";
        const headers = { "Content-Type": "application/json" };

        let forwardedTo = "primary";
        let responseStatus = 0;

        // Try primary first
        try {
            const resp = await fetch(primaryUrl, { method: "POST", body: JSON.stringify(payload), headers });
            responseStatus = resp.status;
            if (!resp.ok) throw new Error(`Primary returned ${resp.status}`);
        } catch (e) {
            // Switch to fallback
            forwardedTo = "fallback";
            try {
                const resp = await fetch(fallbackUrl, { method: "POST", body: JSON.stringify(payload), headers });
                responseStatus = resp.status;
            } catch (fallbackErr) {
                responseStatus = 502;
            }
        }

        // Log to Supabase (non-blocking)
        ctx.waitUntil((async () => {
            try {
                const supabaseUrl = env.SUPABASE_URL || "https://rzcpfwkygdvoshtwxncs.supabase.co";
                const supabaseKey = env.SUPABASE_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo";
                await fetch(`${supabaseUrl}/rest/v1/webhook_logs`, {
                    method: "POST",
                    headers: { "apikey": supabaseKey, "Authorization": `Bearer ${supabaseKey}`, "Content-Type": "application/json" },
                    body: JSON.stringify({
                        timestamp,
                        source: request.headers.get("User-Agent") || "webhook",
                        payload,
                        forwarded_to: forwardedTo === "primary" ? primaryUrl : fallbackUrl,
                        result_status: responseStatus
                    })
                });
            } catch (logErr) { /* ignore */ }
        })());

        // Return structured JSON
        return new Response(JSON.stringify({
            timestamp,
            source: "webhook",
            forwarded_to: forwardedTo,
            status: responseStatus >= 200 && responseStatus < 300 ? "ok" : "error"
        }), { status: 200, headers: { "Content-Type": "application/json" } });
    }
};
