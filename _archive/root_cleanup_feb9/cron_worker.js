/**
 * Empire 24/7 Cron Scheduler
 * Pure scheduling worker - no static assets
 * Triggers Modal endpoints on schedule for autonomous operation
 */

export default {
    async scheduled(event, env, ctx) {
        const now = new Date();
        const hour = now.getUTCHours();
        const minute = now.getUTCMinutes();
        const dayOfWeek = now.getUTCDay(); // 0=Sunday, 6=Saturday
        const baseUrl = env.MODAL_API_URL || "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run";

        console.log(`[CRON] Triggered at ${now.toISOString()} (UTC h:${hour} m:${minute} dow:${dayOfWeek})`);

        const results = [];

        // Always run on every 10-min trigger
        results.push(await callEndpoint(baseUrl + "/health", "health"));
        results.push(await callEndpoint(baseUrl + "/api/kpi-snapshot", "kpi_snapshot"));
        results.push(await callEndpoint(baseUrl + "/api/reliability-check", "reliability_check"));

        // 8 AM CT Campaign (14:00 UTC, weekdays only, minute 0)
        if (hour === 14 && minute < 10 && dayOfWeek >= 1 && dayOfWeek <= 5) {
            console.log("[CRON] Running 8 AM CT campaign...");
            results.push(await callEndpoint(baseUrl + "/campaign", "campaign_8am"));
        }

        // Prospecting every 4 hours (0, 4, 8, 12, 16, 20 UTC)
        if (hour % 4 === 0 && minute < 10) {
            console.log("[CRON] Running prospecting...");
            results.push(await callEndpoint(baseUrl + "/prospect", "prospecting"));
        }

        // Optimizer every 2 hours
        if (hour % 2 === 0 && minute < 10) {
            console.log("[CRON] Running optimizer...");
            results.push(await callEndpoint(baseUrl + "/optimize", "optimizer"));
        }

        // Policy optimizer every hour
        if (minute < 10) {
            console.log("[CRON] Running policy optimizer...");
            results.push(await callEndpoint(baseUrl + "/api/policy-optimize", "policy_optimizer"));
        }

        console.log(`[CRON] Complete. Results:`, JSON.stringify(results));
    },

    async fetch(request, env, ctx) {
        const url = new URL(request.url);

        // Health check
        if (url.pathname === "/health" || url.pathname === "/") {
            return new Response(JSON.stringify({
                status: "ok",
                worker: "empire-cron-scheduler",
                purpose: "24/7 autonomous Modal API trigger",
                timestamp: new Date().toISOString(),
                endpoints_triggered: [
                    "/health",
                    "/api/kpi-snapshot",
                    "/api/reliability-check",
                    "/campaign (8am CT weekdays)",
                    "/prospect (every 4h)",
                    "/optimize (every 2h)",
                    "/api/policy-optimize (hourly)"
                ]
            }), {
                status: 200,
                headers: { "Content-Type": "application/json" }
            });
        }

        // Manual trigger endpoint
        if (url.pathname === "/trigger") {
            const baseUrl = env.MODAL_API_URL;
            const results = await Promise.all([
                callEndpoint(baseUrl + "/health", "health"),
                callEndpoint(baseUrl + "/api/kpi-snapshot", "kpi_snapshot"),
                callEndpoint(baseUrl + "/api/reliability-check", "reliability_check")
            ]);
            return new Response(JSON.stringify({ status: "ok", results }), {
                status: 200,
                headers: { "Content-Type": "application/json" }
            });
        }

        return new Response("Empire Cron Scheduler - 24/7 Autonomy", { status: 200 });
    }
};

async function callEndpoint(url, action) {
    let status = "unknown";
    let result = null;
    const start = Date.now();

    try {
        const resp = await fetch(url, {
            method: "GET",
            headers: { "Content-Type": "application/json" }
        });
        status = resp.ok ? "success" : "failed";
        try { result = await resp.json(); } catch { }
        console.log(`[${action}] ${status} (${Date.now() - start}ms)`);
    } catch (e) {
        status = "error";
        result = e.message;
        console.error(`[${action}] Error: ${e.message}`);
    }

    return { action, status, latency_ms: Date.now() - start };
}
