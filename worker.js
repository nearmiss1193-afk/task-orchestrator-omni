/**
 * Empire Webhook Fallback + Scheduled Automation + Static Site Worker
 * Handles: static files (dashboard with Basic Auth), webhook routing, health checks
 * Build: 20260117-1227-f854b4e
 */

import { getAssetFromKV } from "@cloudflare/kv-asset-handler";

addEventListener("fetch", event => {
    event.respondWith(handleRequest(event));
});

addEventListener("scheduled", event => {
    event.waitUntil(handleScheduled(event));
});

// Basic Auth check for protected routes - SECRETS ONLY, no fallbacks
function checkBasicAuth(request) {
    // Fail closed: if secrets not configured, deny access
    if (typeof BASIC_AUTH_USER === "undefined" || typeof BASIC_AUTH_PASS === "undefined") {
        console.error("BASIC_AUTH_USER or BASIC_AUTH_PASS not configured");
        return false;
    }

    const authHeader = request.headers.get("Authorization");
    if (!authHeader || !authHeader.startsWith("Basic ")) {
        return false;
    }

    const base64 = authHeader.slice(6);
    const decoded = atob(base64);
    const [user, pass] = decoded.split(":");

    return user === BASIC_AUTH_USER && pass === BASIC_AUTH_PASS;
}

function unauthorized() {
    return new Response("Unauthorized - Sovereign Access Required", {
        status: 401,
        headers: {
            "WWW-Authenticate": 'Basic realm="Sovereign Command Center"',
            "Content-Type": "text/plain"
        }
    });
}

async function handleRequest(event) {
    const request = event.request;
    const url = new URL(request.url);
    const pathname = url.pathname;

    // Protected routes: dashboard and assets
    const isProtectedRoute = pathname === "/" || pathname === "/dashboard.html" || pathname.startsWith("/assets/");

    // Serve static files for dashboard and assets (with Basic Auth)
    if (isProtectedRoute || pathname.endsWith(".html") || pathname.endsWith(".js") || pathname.endsWith(".css") || pathname.endsWith(".png") || pathname.endsWith(".jpg") || pathname.endsWith(".ico")) {

        // Require Basic Auth for protected routes only
        if (isProtectedRoute && !checkBasicAuth(request)) {
            return unauthorized();
        }

        try {
            let response = await getAssetFromKV(event, {
                mapRequestToAsset: (req) => {
                    const url = new URL(req.url);
                    if (url.pathname === "/") {
                        url.pathname = "/dashboard.html";
                    }
                    return new Request(url.toString(), req);
                }
            });

            // Add cache control headers for dashboard
            if (pathname === "/dashboard.html" || pathname === "/") {
                response = new Response(response.body, response);
                response.headers.set("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0");
                response.headers.set("Pragma", "no-cache");
                response.headers.set("Expires", "0");
            }

            return response;
        } catch (e) {
            console.log("Asset not found:", pathname, e.message);
        }
    }

    // Webhook handler (POST requests)
    if (request.method === "POST") {
        try {
            const body = await request.json();
            event.waitUntil(logToSupabase("webhook", body));

            const primaryUrl = "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/inbound";
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

    // Health check endpoint
    if (pathname === "/health" || pathname === "/api/health") {
        return new Response(JSON.stringify({
            status: "ok",
            build: "20260117-1114-2d01424",
            worker: "empire-webhook-fallback",
            timestamp: new Date().toISOString()
        }), {
            status: 200,
            headers: { "Content-Type": "application/json" }
        });
    }

    return new Response("Empire Worker - Use POST for webhook or GET /dashboard.html", { status: 405 });
}

async function handleScheduled(event) {
    const now = new Date();
    const hour = now.getUTCHours();
    const minute = now.getUTCMinutes();
    const baseUrl = "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run";

    console.log(`Scheduled trigger at ${now.toISOString()} (UTC hour: ${hour}, minute: ${minute})`);

    // Always run health check (every 10 min trigger)
    await runEndpoint(baseUrl + "/health", "health_check");

    // KPI Snapshot - every 10 min for self-annealing
    await runEndpoint(baseUrl + "/api/kpi-snapshot", "kpi_snapshot");

    // Reliability Check - every 10 min for auto-heal
    await runEndpoint(baseUrl + "/api/reliability-check", "reliability_check");

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
