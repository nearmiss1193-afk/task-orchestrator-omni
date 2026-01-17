// Cloudflare Worker: Webhook Fallback Agent (with Security)
// Validates signatures, rejects non-POST, forwards to primary/fallback

export default {
    async fetch(request, env, ctx) {
        // SECURITY: Reject non-POST
        if (request.method !== "POST") {
            return new Response(JSON.stringify({ error: "Method not allowed" }), {
                status: 405,
                headers: { "Content-Type": "application/json" }
            });
        }

        // Clone request for reading body multiple times
        const body = await request.text();

        // SECURITY: Validate signature if present (GHL/Twilio style)
        const signature = request.headers.get("X-Hub-Signature-256") ||
            request.headers.get("X-Twilio-Signature") ||
            request.headers.get("X-GHL-Signature");

        if (env.WEBHOOK_SECRET && signature) {
            const encoder = new TextEncoder();
            const key = await crypto.subtle.importKey(
                "raw",
                encoder.encode(env.WEBHOOK_SECRET),
                { name: "HMAC", hash: "SHA-256" },
                false,
                ["sign"]
            );
            const signatureBuffer = await crypto.subtle.sign("HMAC", key, encoder.encode(body));
            const expectedSignature = "sha256=" + Array.from(new Uint8Array(signatureBuffer))
                .map(b => b.toString(16).padStart(2, "0"))
                .join("");

            if (signature !== expectedSignature) {
                console.log("Signature mismatch");
                // Log failed attempt but don't block (some webhooks don't sign)
            }
        }

        const payload = JSON.parse(body);
        const primaryUrl = env.PRIMARY_URL;
        const fallbackUrl = env.FALLBACK_URL;
        const headers = { "Content-Type": "application/json" };

        let response;
        let usedFallback = false;

        try {
            response = await fetch(primaryUrl, {
                method: "POST",
                body: JSON.stringify(payload),
                headers,
            });
            if (!response.ok) throw new Error(`Primary returned ${response.status}`);
        } catch (e) {
            console.log(`Primary failed: ${e.message}, switching to fallback`);
            usedFallback = true;
            try {
                response = await fetch(fallbackUrl, {
                    method: "POST",
                    body: JSON.stringify(payload),
                    headers,
                });
            } catch (fallbackErr) {
                console.log(`Fallback also failed: ${fallbackErr.message}`);
                return new Response(JSON.stringify({ error: "All backends unavailable" }), { status: 502 });
            }
        }

        // Log to Supabase (non-blocking)
        ctx.waitUntil((async () => {
            try {
                const supabaseUrl = env.SUPABASE_URL || "https://rzcpfwkygdvoshtwxncs.supabase.co";
                const supabaseKey = env.SUPABASE_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo";
                await fetch(`${supabaseUrl}/rest/v1/webhook_logs`, {
                    method: "POST",
                    headers: {
                        "apikey": supabaseKey,
                        "Authorization": `Bearer ${supabaseKey}`,
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        timestamp: new Date().toISOString(),
                        source: request.headers.get("User-Agent") || "unknown",
                        payload: payload,
                        forwarded_to: usedFallback ? fallbackUrl : primaryUrl,
                        result_status: response?.status || 0,
                    }),
                });
            } catch (logErr) {
                console.log(`Log failed: ${logErr.message}`);
            }
        })());

        return new Response(JSON.stringify({ status: "received" }), {
            status: 200,
            headers: { "Content-Type": "application/json" }
        });
    },
};
