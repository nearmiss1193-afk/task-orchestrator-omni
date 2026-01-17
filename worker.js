addEventListener("fetch", event => {
    event.respondWith(handleRequest(event.request, event));
});

addEventListener("scheduled", event => {
    event.waitUntil(runHealthCheck());
});

async function handleRequest(request, event) {
    const url = new URL(request.url);
    if (request.method === "POST") {
        // normal webhook dispatch logic
        try {
            const body = await request.json();
            event.waitUntil(logToSupabase("webhook", body));

            // Try primary Modal orchestrator first
            const primaryUrl = "https://nearmiss1193-afk--empire-api-v1-orchestration-api.modal.run/inbound";
            const fallbackUrl = "https://empire-fallback-runner.up.railway.app/webhook";

            let targetUrl = primaryUrl;
            try {
                const resp = await fetch(primaryUrl, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(body)
                });
                if (!resp.ok) throw new Error("Primary failed");
            } catch (e) {
                // Fallback to Railway
                targetUrl = fallbackUrl;
                await fetch(fallbackUrl, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(body)
                });
            }

            return new Response(JSON.stringify({ status: "ok", forwarded_to: targetUrl }), {
                status: 200,
                headers: { "Content-Type": "application/json" }
            });
        } catch (e) {
            return new Response(JSON.stringify({ status: "error", message: e.message }), {
                status: 500,
                headers: { "Content-Type": "application/json" }
            });
        }
    }
    return new Response("Use POST for webhook", { status: 405 });
}

async function runHealthCheck() {
    const primaryUrl = "https://nearmiss1193-afk--empire-api-v1-orchestration-api.modal.run/health";
    let status = "unknown";
    try {
        const resp = await fetch(primaryUrl);
        status = resp.ok ? "healthy" : "unhealthy";
    } catch (e) {
        status = "error";
    }
    await logToSupabase("health_check", { primary: primaryUrl, status, timestamp: new Date().toISOString() });
}

async function logToSupabase(type, payload) {
    const supabaseUrl = "https://rzcpfwkygdvoshtwxncs.supabase.co";
    const supabaseKey = typeof SUPABASE_KEY !== "undefined" ? SUPABASE_KEY : "";
    if (!supabaseKey) return;

    const table = type === "webhook" ? "webhook_logs" : "health_logs";
    try {
        await fetch(`${supabaseUrl}/rest/v1/${table}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "apikey": supabaseKey,
                "Authorization": `Bearer ${supabaseKey}`,
            },
            body: JSON.stringify({
                component: "cloudflare_worker",
                status: type,
                action_taken: type,
                message: JSON.stringify(payload),
                timestamp: new Date().toISOString()
            }),
        });
    } catch (e) {
        console.error("Supabase log failed:", e.message);
    }
}
