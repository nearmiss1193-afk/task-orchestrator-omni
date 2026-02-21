"""
🔍 AUTONOMOUS INSPECTOR — Self-Healing Error Engine
====================================================
Three-stage autonomous error handling: DETECT → DIAGNOSE → REPAIR

Integrates into system_orchestrator and system_heartbeat.
No new CRONs required — piggybacks on existing */5 schedule.

Usage in deploy.py:
    from modules.autonomous_inspector import Inspector, safe_spawn

    # Wrap spawns:
    safe_spawn(some_function, "some_function")

    # In orchestrator catch block:
    inspector = Inspector()
    inspector.handle_crash("system_orchestrator", error)

    # In heartbeat:
    inspector = Inspector()
    inspector.run_inspection_cycle()
"""
import os
import json
import traceback
import re
import requests
from datetime import datetime, timezone, timedelta
from collections import defaultdict

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://rzcpfwkygdvoshtwxncs.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

# Alert targets
ALERT_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
OWNER_PHONE = "+13529368152"
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
ALERT_EMAIL = os.getenv("OWNER_EMAIL", "nearmiss1193@gmail.com")

# Thresholds
MAX_RETRIES = 3
CIRCUIT_BREAKER_THRESHOLD = 3  # failures in window = disable
CIRCUIT_BREAKER_WINDOW_HOURS = 1
ALERT_COOLDOWN_MINUTES = 30  # Don't spam Dan

# ═══════════════════════════════════════════════════════════
# ERROR PATTERN REGISTRY — Known failure types + auto-fixes
# ═══════════════════════════════════════════════════════════

ERROR_PATTERNS = [
    {
        "name": "transient_network",
        "patterns": [
            r"ConnectionError", r"ConnectionRefusedError", r"TimeoutError",
            r"requests\.exceptions\.Timeout", r"requests\.exceptions\.ConnectionError",
            r"socket\.timeout", r"urllib3\.exceptions", r"SSLError",
            r"RemoteDisconnected", r"BrokenPipeError"
        ],
        "action": "retry",
        "max_retries": 3,
        "backoff_seconds": [5, 15, 45],
        "severity": "low",
        "description": "Network/API temporarily unavailable"
    },
    {
        "name": "rate_limit",
        "patterns": [
            r"429", r"RateLimitError", r"rate.?limit", r"Too Many Requests",
            r"quota exceeded", r"throttl"
        ],
        "action": "retry",
        "max_retries": 2,
        "backoff_seconds": [30, 120],
        "severity": "medium",
        "description": "API rate limit hit — will slow down"
    },
    {
        "name": "null_reference",
        "patterns": [
            r"'NoneType' object has no attribute",
            r"'NoneType' object is not subscriptable",
            r"NoneType.*get"
        ],
        "action": "skip_record",
        "severity": "low",
        "description": "Null data from API/DB — skipping bad record"
    },
    {
        "name": "key_error",
        "patterns": [
            r"KeyError:", r"KeyError\("
        ],
        "action": "skip_record",
        "severity": "low",
        "description": "Missing field in data — skipping record"
    },
    {
        "name": "import_error",
        "patterns": [
            r"ImportError", r"ModuleNotFoundError", r"No module named"
        ],
        "action": "alert",
        "severity": "critical",
        "description": "Missing Python package — needs deploy fix"
    },
    {
        "name": "auth_error",
        "patterns": [
            r"401", r"403", r"Unauthorized", r"Forbidden",
            r"Invalid API key", r"invalid_api_key", r"authentication"
        ],
        "action": "circuit_break",
        "severity": "critical",
        "description": "Auth failure — API key may be expired/wrong"
    },
    {
        "name": "db_schema",
        "patterns": [
            r"column .* does not exist", r"relation .* does not exist",
            r"undefined column", r"no such table", r"violates"
        ],
        "action": "alert",
        "severity": "critical",
        "description": "Database schema mismatch — needs code update"
    },
    {
        "name": "cron_limit",
        "patterns": [
            r"reached limit of \d+ cron", r"cron.*limit"
        ],
        "action": "alert",
        "severity": "critical",
        "description": "Modal CRON limit exceeded"
    },
    {
        "name": "memory_error",
        "patterns": [
            r"MemoryError", r"Out of memory", r"OOM"
        ],
        "action": "circuit_break",
        "severity": "critical",
        "description": "Out of memory — function needs optimization"
    },
]

# ═══════════════════════════════════════════════════════════
# SUPABASE HELPERS (direct REST — no client dependency)
# ═══════════════════════════════════════════════════════════

def _sb_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def _sb_insert(table, data):
    """Insert a row into Supabase via REST."""
    try:
        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/{table}",
            headers=_sb_headers(),
            json=data,
            timeout=10
        )
        return resp.status_code in (200, 201)
    except Exception:
        return False

def _sb_query(table, params):
    """Query Supabase via REST."""
    try:
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/{table}",
            headers=_sb_headers(),
            params=params,
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json()
        return []
    except Exception:
        return []

def _sb_update(table, match_params, update_data):
    """Update rows in Supabase via REST."""
    try:
        resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/{table}",
            headers=_sb_headers(),
            params=match_params,
            json=update_data,
            timeout=10
        )
        return resp.status_code in (200, 204)
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════
# INSPECTOR CLASS
# ═══════════════════════════════════════════════════════════

class Inspector:
    """Autonomous error detection, diagnosis, and repair engine."""

    def __init__(self):
        self._last_alert_time = None
        self._circuit_breakers = {}  # {func_name: {"disabled_until": datetime, "count": int}}

    # ──────────────────────────────────────────────
    # STAGE 1: DETECT — Log errors with full context
    # ──────────────────────────────────────────────

    def log_error(self, source: str, exception: Exception, context: dict = None) -> str:
        """Log an error to system_error_log. Returns error ID or None."""
        tb = traceback.format_exception(type(exception), exception, exception.__traceback__)
        tb_str = "".join(tb)[-2000:]  # Last 2000 chars of traceback

        error_data = {
            "source": source[:100],
            "error_type": type(exception).__name__,
            "error_message": str(exception)[:500],
            "traceback": tb_str,
            "status": "new",
            "retry_count": 0,
            "context": json.dumps(context or {}),
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        result = _sb_insert("system_error_log", error_data)
        if result:
            print(f"  🔍 INSPECTOR: Logged {type(exception).__name__} from {source}")
        return result

    # ──────────────────────────────────────────────
    # STAGE 2: DIAGNOSE — Pattern-match errors
    # ──────────────────────────────────────────────

    def diagnose(self, exception: Exception) -> dict:
        """Pattern-match an error against known failure types.
        Returns: {"pattern": {...}, "action": str, "severity": str}
        """
        error_str = f"{type(exception).__name__}: {str(exception)}"
        tb_str = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        full_text = f"{error_str}\n{tb_str}"

        for pattern_def in ERROR_PATTERNS:
            for regex in pattern_def["patterns"]:
                if re.search(regex, full_text, re.IGNORECASE):
                    return {
                        "pattern": pattern_def,
                        "action": pattern_def["action"],
                        "severity": pattern_def["severity"],
                        "name": pattern_def["name"],
                        "description": pattern_def["description"]
                    }

        # Unknown error — default to alert
        return {
            "pattern": None,
            "action": "alert",
            "severity": "high",
            "name": "unknown",
            "description": f"Unknown error: {type(exception).__name__}"
        }

    # ──────────────────────────────────────────────
    # STAGE 3: REPAIR — Auto-fix or escalate
    # ──────────────────────────────────────────────

    def repair(self, source: str, exception: Exception, diagnosis: dict, retry_fn=None) -> dict:
        """Execute the repair action based on diagnosis.
        
        Args:
            source: Function name that failed
            exception: The caught exception
            diagnosis: Result from diagnose()
            retry_fn: Optional callable to retry the failed operation

        Returns:
            {"action_taken": str, "success": bool, "details": str}
        """
        action = diagnosis["action"]
        result = {"action_taken": action, "success": False, "details": ""}

        if action == "retry" and retry_fn:
            result = self._do_retry(source, retry_fn, diagnosis)

        elif action == "skip_record":
            result = self._do_skip(source, exception)

        elif action == "circuit_break":
            result = self._do_circuit_break(source, diagnosis)

        elif action == "alert":
            result = self._do_alert(source, exception, diagnosis)

        else:
            result = self._do_alert(source, exception, diagnosis)

        # Update error log status
        self._update_error_status(source, result["action_taken"])

        return result

    def _do_retry(self, source: str, retry_fn, diagnosis: dict) -> dict:
        """Retry a function with exponential backoff."""
        import time
        backoffs = diagnosis["pattern"].get("backoff_seconds", [5, 15, 45])
        max_retries = diagnosis["pattern"].get("max_retries", MAX_RETRIES)

        for attempt in range(min(max_retries, len(backoffs))):
            wait = backoffs[attempt]
            print(f"  🔄 INSPECTOR: Retry {attempt + 1}/{max_retries} for {source} "
                  f"(waiting {wait}s)...")
            time.sleep(wait)

            try:
                retry_fn()
                print(f"  ✅ INSPECTOR: {source} recovered on retry {attempt + 1}")
                return {
                    "action_taken": f"retried_{attempt + 1}x",
                    "success": True,
                    "details": f"Recovered after {attempt + 1} retries"
                }
            except Exception as retry_err:
                print(f"  ❌ INSPECTOR: Retry {attempt + 1} failed: {retry_err}")

        # All retries exhausted — circuit break
        print(f"  🔴 INSPECTOR: All {max_retries} retries exhausted for {source}")
        return self._do_circuit_break(source, diagnosis)

    def _do_skip(self, source: str, exception: Exception) -> dict:
        """Skip the bad record and continue."""
        print(f"  ⏭️ INSPECTOR: Skipping bad record in {source} "
              f"({type(exception).__name__})")
        return {
            "action_taken": "skip_record",
            "success": True,
            "details": f"Skipped: {str(exception)[:100]}"
        }

    def _do_circuit_break(self, source: str, diagnosis: dict) -> dict:
        """Disable a function for 1 hour to prevent crash loops."""
        disable_until = datetime.now(timezone.utc) + timedelta(hours=CIRCUIT_BREAKER_WINDOW_HOURS)
        self._circuit_breakers[source] = {
            "disabled_until": disable_until,
            "count": self._circuit_breakers.get(source, {}).get("count", 0) + 1
        }

        # Persist to Supabase so it survives restarts
        _sb_insert("system_error_log", {
            "source": source,
            "error_type": "CIRCUIT_BREAKER",
            "error_message": f"Function {source} disabled until {disable_until.isoformat()}",
            "status": "circuit_broken",
            "retry_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        })

        print(f"  🔌 INSPECTOR: CIRCUIT BREAKER — {source} disabled until "
              f"{disable_until.strftime('%H:%M UTC')}")

        # Also alert Dan for circuit breakers
        self._send_alert(
            source,
            f"🔌 Circuit breaker activated for {source}\n"
            f"Reason: {diagnosis['description']}\n"
            f"Disabled until: {disable_until.strftime('%I:%M %p UTC')}\n"
            f"This function will auto-resume after cooldown."
        )

        return {
            "action_taken": "circuit_break",
            "success": True,
            "details": f"Disabled {source} until {disable_until.isoformat()}"
        }

    def _do_alert(self, source: str, exception: Exception, diagnosis: dict) -> dict:
        """Alert Dan — for unfixable issues only."""
        severity = diagnosis["severity"]
        desc = diagnosis["description"]
        err_msg = str(exception)[:200]

        alert_msg = (
            f"🚨 [{severity.upper()}] {desc}\n\n"
            f"Function: {source}\n"
            f"Error: {err_msg}\n"
            f"Pattern: {diagnosis['name']}\n"
            f"Time: {datetime.now(timezone.utc).strftime('%I:%M %p UTC')}\n\n"
            f"Action needed: Check Modal logs."
        )

        sent = self._send_alert(source, alert_msg)

        return {
            "action_taken": "alert_sent" if sent else "alert_failed",
            "success": sent,
            "details": f"Alert {'sent' if sent else 'suppressed (cooldown)'}: {desc}"
        }

    # ──────────────────────────────────────────────
    # CIRCUIT BREAKER CHECK
    # ──────────────────────────────────────────────

    def is_circuit_broken(self, source: str) -> bool:
        """Check if a function is currently circuit-broken."""
        # Check in-memory first
        if source in self._circuit_breakers:
            cb = self._circuit_breakers[source]
            if datetime.now(timezone.utc) < cb["disabled_until"]:
                print(f"  🔌 INSPECTOR: {source} is circuit-broken until "
                      f"{cb['disabled_until'].strftime('%H:%M UTC')}")
                return True
            else:
                # Cooldown expired — re-enable
                del self._circuit_breakers[source]
                print(f"  ✅ INSPECTOR: {source} circuit breaker expired — re-enabled")
                return False

        # Check Supabase for persistent circuit breakers
        since = (datetime.now(timezone.utc) - timedelta(hours=CIRCUIT_BREAKER_WINDOW_HOURS)).isoformat()
        rows = _sb_query("system_error_log", {
            "source": f"eq.{source}",
            "status": "eq.circuit_broken",
            "created_at": f"gte.{since}",
            "select": "created_at",
            "limit": "1"
        })
        if rows:
            print(f"  🔌 INSPECTOR: {source} has active circuit breaker in DB")
            return True

        return False

    # ──────────────────────────────────────────────
    # INSPECTION CYCLE (runs in heartbeat)
    # ──────────────────────────────────────────────

    def run_inspection_cycle(self):
        """Periodic health check — call from system_heartbeat.
        
        Checks:
        1. Error frequency spikes in last hour
        2. Stale circuit breakers to clear
        3. Recurring errors that need escalation
        """
        print("🔍 INSPECTOR: Running inspection cycle...")

        since = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        recent_errors = _sb_query("system_error_log", {
            "created_at": f"gte.{since}",
            "select": "source,error_type,status,created_at",
            "order": "created_at.desc",
            "limit": "50"
        })

        if not recent_errors:
            print("  ✅ INSPECTOR: No errors in last hour — all clear")
            return {"status": "healthy", "errors_1h": 0}

        # Group by source
        by_source = defaultdict(list)
        for err in recent_errors:
            by_source[err.get("source", "unknown")].append(err)

        # Check for functions hitting threshold
        alerts = []
        for source, errors in by_source.items():
            count = len(errors)
            if count >= CIRCUIT_BREAKER_THRESHOLD and not self.is_circuit_broken(source):
                # Auto circuit-break
                print(f"  🔴 INSPECTOR: {source} has {count} errors in 1h — "
                      f"activating circuit breaker")
                self._do_circuit_break(source, {
                    "description": f"{count} failures in 1 hour",
                    "severity": "high"
                })
                alerts.append(source)

        # Summary
        total = len(recent_errors)
        broken = len([s for s in by_source if self.is_circuit_broken(s)])

        summary = {
            "status": "degraded" if alerts else "monitoring",
            "errors_1h": total,
            "unique_sources": len(by_source),
            "circuit_broken": broken,
            "new_breaks": alerts
        }

        print(f"  📊 INSPECTOR: {total} errors from {len(by_source)} sources | "
              f"{broken} circuit-broken")

        return summary

    # ──────────────────────────────────────────────
    # HIGH-LEVEL CRASH HANDLER (for orchestrator)
    # ──────────────────────────────────────────────

    def handle_crash(self, source: str, exception: Exception, retry_fn=None):
        """Full pipeline: detect → diagnose → repair.
        Call this from the orchestrator's except block.
        """
        print(f"\n{'='*60}")
        print(f"🔍 INSPECTOR: Handling crash in {source}")
        print(f"  Error: {type(exception).__name__}: {str(exception)[:200]}")
        print(f"{'='*60}")

        # Stage 1: DETECT & ROUTE TO ABACUS (Phase 5 Auto-Patching)
        self.log_error(source, exception)
        
        try:
            import requests
            requests.post(
                "https://sovereign-empire-api-908fw2.abacusai.app/webhook/system-error",
                json={
                    "source": "modal",
                    "error_type": type(exception).__name__,
                    "error_message": str(exception)[:500],
                    "stack_trace": traceback.format_exc(),
                    "severity": "critical"
                },
                headers={"Authorization": "Bearer sovereign_abacus_webhook_2026_xyz99", "Content-Type": "application/json"},
                timeout=10
            )
            print(f"  🤖 INSPECTOR: Crash telemetry successfully routed to Abacus AI Engineer.")
        except Exception as abacus_err:
            print(f"  ⚠️ INSPECTOR: Failed to route crash to Abacus: {abacus_err}")

        # Stage 2: DIAGNOSE
        diagnosis = self.diagnose(exception)
        print(f"  📋 Diagnosis: {diagnosis['name']} ({diagnosis['severity']})")
        print(f"  📋 Action: {diagnosis['action']}")
        print(f"  📋 Description: {diagnosis['description']}")

        # Stage 3: REPAIR
        result = self.repair(source, exception, diagnosis, retry_fn)
        print(f"  📋 Result: {result['action_taken']} — "
              f"{'✅ Success' if result['success'] else '❌ Failed'}")
        print(f"  📋 Details: {result['details']}")
        print(f"{'='*60}\n")

        return result

    # ──────────────────────────────────────────────
    # ALERTING
    # ──────────────────────────────────────────────

    def _send_alert(self, source: str, message: str) -> bool:
        """Send alert to Dan via SMS webhook + email. Respects cooldown."""
        now = datetime.now(timezone.utc)

        # Check cooldown to avoid spam
        if self._last_alert_time:
            elapsed = (now - self._last_alert_time).total_seconds() / 60
            if elapsed < ALERT_COOLDOWN_MINUTES:
                print(f"  ⏳ INSPECTOR: Alert suppressed (cooldown: "
                      f"{int(ALERT_COOLDOWN_MINUTES - elapsed)}m remaining)")
                return False

        self._last_alert_time = now
        sent = False

        # SMS via GHL webhook
        try:
            resp = requests.post(ALERT_WEBHOOK, json={
                "phone": OWNER_PHONE,
                "message": message[:600],
                "type": "inspector_alert"
            }, timeout=10)
            if resp.status_code in (200, 201):
                sent = True
                print(f"  📱 INSPECTOR: SMS alert sent to Dan")
        except Exception as e:
            print(f"  ⚠️ INSPECTOR: SMS alert failed: {e}")

        # Email via Resend
        if RESEND_API_KEY:
            try:
                requests.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {RESEND_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "from": "Empire Inspector <alerts@aiserviceco.com>",
                        "to": [ALERT_EMAIL],
                        "subject": f"🔍 Inspector Alert: {source}",
                        "html": f"""
                        <div style="font-family: monospace; padding: 20px; background: #0f172a; color: #e2e8f0;">
                            <h2 style="color: #f59e0b;">🔍 Autonomous Inspector Alert</h2>
                            <pre style="color: #94a3b8; white-space: pre-wrap;">{message}</pre>
                            <hr style="border-color: #334155;">
                            <p style="color: #475569; font-size: 12px;">
                                Empire AI Inspector · {now.strftime('%Y-%m-%d %H:%M UTC')}
                            </p>
                        </div>
                        """
                    },
                    timeout=10
                )
                print(f"  📧 INSPECTOR: Email alert sent")
            except Exception:
                pass

        return sent

    def _update_error_status(self, source: str, new_status: str):
        """Update most recent error's status."""
        _sb_update(
            "system_error_log",
            {"source": f"eq.{source}", "status": "eq.new", "order": "created_at.desc", "limit": "1"},
            {"status": new_status}
        )


# ═══════════════════════════════════════════════════════════
# SAFE SPAWN — Drop-in replacement for .spawn()
# ═══════════════════════════════════════════════════════════

# Module-level inspector for safe_spawn
_inspector = Inspector()


def safe_spawn(modal_fn, name: str, *args, **kwargs):
    """Safe wrapper around Modal .spawn() with circuit breaker check.
    
    Usage:
        # Instead of: some_function.spawn()
        safe_spawn(some_function, "some_function")
        
        # With args:
        safe_spawn(some_function, "some_function", lead_id)
    """
    if _inspector.is_circuit_broken(name):
        print(f"  🔌 SKIPPED: {name} is circuit-broken")
        return None

    try:
        return modal_fn.spawn(*args, **kwargs)
    except Exception as e:
        print(f"  ❌ SPAWN FAILED: {name}: {e}")
        _inspector.handle_crash(f"spawn_{name}", e)
        return None


def safe_local(modal_fn, name: str, *args, **kwargs):
    """Safe wrapper around Modal .local() with full inspector pipeline.
    
    Usage:
        # Instead of: some_function.local()
        safe_local(some_function, "some_function")
    """
    if _inspector.is_circuit_broken(name):
        print(f"  🔌 SKIPPED: {name} is circuit-broken")
        return None

    try:
        return modal_fn.local(*args, **kwargs)
    except Exception as e:
        _inspector.handle_crash(name, e, retry_fn=lambda: modal_fn.local(*args, **kwargs))
        return None


# ═══════════════════════════════════════════════════════════
# QUICK TEST
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🔍 Testing Autonomous Inspector...")

    inspector = Inspector()

    # Test diagnosis
    test_errors = [
        ConnectionError("Resend API timeout"),
        KeyError("company_name"),
        ImportError("No module named 'foobar'"),
        ValueError("429 Too Many Requests"),
        AttributeError("'NoneType' object has no attribute 'get'"),
    ]

    for err in test_errors:
        diagnosis = inspector.diagnose(err)
        print(f"  {type(err).__name__}: {str(err)[:40]}")
        print(f"    → {diagnosis['name']} | {diagnosis['action']} | {diagnosis['severity']}")

    print("\n✅ Inspector test complete")
