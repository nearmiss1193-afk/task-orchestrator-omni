"""
SELF-IMPROVEMENT OPTIMIZER
Runs every 2 hours to analyze logs and suggest system improvements.
Deployed to Modal with scheduled execution.
"""
import modal
import json
from datetime import datetime, timedelta

image = modal.Image.debian_slim(python_version="3.11").pip_install("requests", "fastapi[standard]")
app = modal.App("self-improvement-optimizer", image=image)

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
GEMINI_API_KEY = "AIzaSyAfqN89E6mIoKT3OWNKKXrN4xZIqoOHHNo"

@app.function(schedule=modal.Cron("0 */2 * * *"))  # Every 2 hours
def analyze_and_optimize():
    """Scheduled analysis of logs for self-improvement suggestions."""
    import requests
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    # Fetch recent logs (last 24 hours)
    since = (datetime.utcnow() - timedelta(hours=24)).isoformat()
    
    # Get health_logs
    health_logs = []
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/health_logs?created_at=gte.{since}&order=created_at.desc&limit=100",
            headers=headers, timeout=15
        )
        if r.status_code == 200:
            health_logs = r.json()
    except Exception as e:
        print(f"Failed to fetch health_logs: {e}")
    
    # Get webhook_logs
    webhook_logs = []
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/webhook_logs?timestamp=gte.{since}&order=timestamp.desc&limit=100",
            headers=headers, timeout=15
        )
        if r.status_code == 200:
            webhook_logs = r.json()
    except Exception as e:
        print(f"Failed to fetch webhook_logs: {e}")
    
    # Analyze patterns
    patterns = analyze_patterns(health_logs, webhook_logs)
    code_changes = suggest_code_changes(patterns)
    deploy_actions = suggest_deploy_actions(patterns)
    
    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "logs_analyzed": {
            "health_logs": len(health_logs),
            "webhook_logs": len(webhook_logs)
        },
        "patterns": patterns,
        "suggested_code_changes": code_changes,
        "suggested_deploy_actions": deploy_actions
    }
    
    # Log the analysis result to Supabase
    try:
        requests.post(
            f"{SUPABASE_URL}/rest/v1/optimization_logs",
            headers=headers,
            json={
                "timestamp": result["timestamp"],
                "analysis": result,
                "patterns_found": len(patterns),
                "suggestions_count": len(code_changes) + len(deploy_actions)
            },
            timeout=15
        )
    except Exception as e:
        print(f"Failed to log optimization results: {e}")
    
    print(json.dumps(result, indent=2))
    return result


def analyze_patterns(health_logs: list, webhook_logs: list) -> list:
    """Identify recurrent failure patterns from logs."""
    patterns = []
    
    # Analyze health log failures
    health_failures = [log for log in health_logs if log.get("status") != "ok"]
    if health_failures:
        failure_counts = {}
        for log in health_failures:
            component = log.get("component", "unknown")
            failure_counts[component] = failure_counts.get(component, 0) + 1
        
        for component, count in failure_counts.items():
            if count >= 2:
                patterns.append({
                    "type": "recurring_health_failure",
                    "component": component,
                    "occurrences": count,
                    "severity": "high" if count >= 5 else "medium",
                    "description": f"Component '{component}' failed {count} times in last 24h"
                })
    
    # Analyze webhook failures
    webhook_failures = [log for log in webhook_logs if log.get("result_status", 200) >= 400]
    if webhook_failures:
        error_codes = {}
        for log in webhook_failures:
            code = log.get("result_status", 0)
            error_codes[code] = error_codes.get(code, 0) + 1
        
        for code, count in error_codes.items():
            patterns.append({
                "type": "webhook_error_pattern",
                "error_code": code,
                "occurrences": count,
                "severity": "high" if code >= 500 else "medium",
                "description": f"Webhook returned {code} error {count} times"
            })
    
    # Check for fallback activations
    fallback_uses = [log for log in webhook_logs if log.get("forwarded_to") == "fallback"]
    if fallback_uses:
        patterns.append({
            "type": "fallback_activation",
            "occurrences": len(fallback_uses),
            "severity": "medium",
            "description": f"Fallback was activated {len(fallback_uses)} times (primary was down)"
        })
    
    # Check for timeout patterns
    timeout_logs = [
        log for log in health_logs 
        if "timeout" in str(log.get("error", "")).lower()
    ]
    if timeout_logs:
        patterns.append({
            "type": "timeout_pattern",
            "occurrences": len(timeout_logs),
            "severity": "medium",
            "description": f"Detected {len(timeout_logs)} timeout errors"
        })
    
    return patterns


def suggest_code_changes(patterns: list) -> list:
    """Generate code change suggestions based on patterns."""
    suggestions = []
    
    for pattern in patterns:
        if pattern["type"] == "recurring_health_failure":
            suggestions.append({
                "target": f"{pattern['component']}_handler",
                "change": "Add retry logic with exponential backoff",
                "risk_level": "low",
                "test_validation": "Run health check 10x and verify 100% success rate",
                "code_snippet": """
import time
def with_retry(func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if i == max_retries - 1:
                raise
            time.sleep(2 ** i)
"""
            })
        
        elif pattern["type"] == "webhook_error_pattern":
            if pattern["error_code"] >= 500:
                suggestions.append({
                    "target": "webhook_handler",
                    "change": "Add circuit breaker pattern for failing endpoints",
                    "risk_level": "medium",
                    "test_validation": "Simulate 5 failures, verify circuit opens after 3",
                    "code_snippet": """
class CircuitBreaker:
    def __init__(self, threshold=3, reset_timeout=60):
        self.failures = 0
        self.threshold = threshold
        self.reset_timeout = reset_timeout
        self.last_failure = None
        self.is_open = False
"""
                })
        
        elif pattern["type"] == "timeout_pattern":
            suggestions.append({
                "target": "http_clients",
                "change": "Reduce timeout values and add connection pooling",
                "risk_level": "low",
                "test_validation": "Measure p99 latency before/after, should decrease",
                "code_snippet": """
import requests
from requests.adapters import HTTPAdapter
session = requests.Session()
session.mount('https://', HTTPAdapter(pool_connections=10, pool_maxsize=10))
"""
            })
        
        elif pattern["type"] == "fallback_activation":
            suggestions.append({
                "target": "primary_orchestrator",
                "change": "Investigate primary stability - consider keep-alive pings",
                "risk_level": "low",
                "test_validation": "Monitor fallback activations for 24h after fix",
                "code_snippet": """
# Add to Modal cron job
@app.function(schedule=modal.Cron("*/5 * * * *"))
def keep_alive_ping():
    requests.get(PRIMARY_URL + "/health", timeout=10)
"""
            })
    
    return suggestions


def suggest_deploy_actions(patterns: list) -> list:
    """Generate deployment hardening suggestions."""
    actions = []
    
    for pattern in patterns:
        if pattern["severity"] == "high":
            actions.append({
                "action": f"Scale up {pattern.get('component', 'affected service')}",
                "priority": "high",
                "risk_level": "medium",
                "steps": [
                    "Review current resource allocation",
                    "Increase concurrency limits",
                    "Add horizontal scaling policy"
                ],
                "test_validation": "Load test with 2x traffic, verify no degradation"
            })
    
    # General hardening suggestions based on log volume
    if any(p["type"] == "fallback_activation" for p in patterns):
        actions.append({
            "action": "Enable multi-region deployment",
            "priority": "medium",
            "risk_level": "medium",
            "steps": [
                "Deploy backup to secondary AWS region",
                "Configure Cloudflare load balancer for failover",
                "Test failover with synthetic traffic"
            ],
            "test_validation": "Simulate primary failure, verify < 30s failover"
        })
    
    # Always suggest monitoring improvements
    actions.append({
        "action": "Enhance monitoring and alerting",
        "priority": "low",
        "risk_level": "low",
        "steps": [
            "Add Prometheus metrics export",
            "Configure alert thresholds for error rates > 5%",
            "Set up PagerDuty/SMS alerts for critical failures"
        ],
        "test_validation": "Trigger test alert, verify delivery < 60s"
    })
    
    return actions


# To manually trigger: py -m modal run self_improvement_optimizer.py::analyze_and_optimize
