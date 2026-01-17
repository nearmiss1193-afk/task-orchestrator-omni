/**
 * Empire Webhook Fallback + Scheduled Automation Worker
 * Handles: webhook routing, health checks, prospecting, campaigns, optimization
 */

addEventListener("fetch", event => {
    event.respondWith(handleRequest(event.request, event));
});

addEventListener("scheduled", event => {
    event.waitUntil(handleScheduled(event));
});

async function handleRequest(request, event) {
    const url = new URL(request.url);
    if (request.method === "POST") {
        try {
            const body = await request.json();
            event.waitUntil(logToSupabase("webhook", body));

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
                targetUrl = fallbackUrl;
                await fetch(fallbackUrl, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(body)
                });
            }

            return new Response(JSON.stringify({ status: "ok", forwarded_to: targetUrl }), {
                status: 200, headers: { "Content-Type": "application/json" }
            });
        } catch (e) {
            return new Response(JSON.stringify({ status: "error", message: e.message }), {
                status: 500, headers: { "Content-Type": "application/json" }
            });
        }
    }
    return new Response("Use POST for webhook", { status: 405 });
}

async function handleScheduled(event) {
    const now = new Date();
    const hour = now.getUTCHours();
    const minute = now.getUTCMinutes();
    const baseUrl = "https://nearmiss1193-afk--empire-api-v1-orchestration-api.modal.run";

    console.log(`Scheduled trigger at ${now.toISOString()} (UTC hour: ${hour}, minute: ${minute})`);

    // Always run health check (every 10 min trigger)
    await runEndpoint(baseUrl + "/health", "health_check");

    // 8 AM CT Campaign (14:00 UTC, minute 0)
    if (hour === 14 && minute < 10) {
        console.log("Running 8 AM CT campaign...");
        await runEndpoint(baseUrl + "/campaign", "campaign_8am");
    }

    // Prospecting every 4 hours (0, 4, 8, 12, 16, 20 UTC)
    if (hour % 4 === 0 && minute < 10) {
        console.log("Running prospecting...");
        await runEndpoint(baseUrl + "/prospect", "prospecting");
    }

    // Optimizer every 2 hours (even hours)
    if (hour % 2 === 0 && minute < 10) {
        console.log("Running optimizer...");
        await runEndpoint(baseUrl + "/optimize", "optimizer");
    }
}

async function runEndpoint(url, action) {
    let status = "unknown";
    let result = null;
    try {
        const resp = await fetch(url, { method: "GET", headers: { "Content-Type": "application/json" } });
        status = resp.ok ? "success" : "failed";
        try { result = await resp.json(); } catch { }
        console.log(`${action}: ${status}`, JSON.stringify(result));
    } catch (e) {
        status = "error";
        console.error(`${action} failed:`, e.message);
    }

    await logToSupabase("cron_" + action, { status, result, timestamp: new Date().toISOString() });
    return { action, status, result };
}

async function logToSupabase(type, payload) {
    const supabaseUrl = "https://rzcpfwkygdvoshtwxncs.supabase.co";
    const supabaseKey = typeof SUPABASE_KEY !== "undefined" ? SUPABASE_KEY : "";
    if (!supabaseKey) return;

    const table = type.startsWith("cron_") ? "cron_logs" : (type === "webhook" ? "webhook_logs" : "health_logs");
    try {
        await fetch(`${supabaseUrl}/rest/v1/${table}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "apikey": supabaseKey,
                "Authorization": `Bearer ${supabaseKey}`,
            },
            body: JSON.stringify({
                trigger: "cloudflare_scheduled",
                action: type,
                result: payload,
                timestamp: new Date().toISOString()
            }),
        });
    } catch (e) {
        console.error("Supabase log failed:", e.message);
    }
}
