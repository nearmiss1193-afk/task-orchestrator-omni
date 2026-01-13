"""
🌐 MULTI-CLOUD FAILOVER CONTROLLER
===================================
Active-passive failover across multiple cloud providers.

Architecture:
  PRIMARY   → Modal (empire-sovereign-v2)
  BACKUP 1  → GCP Cloud Run (if Modal fails)
  BACKUP 2  → GitHub Actions (cron jobs only)
  BACKUP 3  → Local (continuous_swarm.py)

Pattern: "One fails, other starts"
- Health checks every 60 seconds
- Automatic promotion of backup to primary
- Auto-demotion when primary recovers
"""
import os
import sys
import time
import requests
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from enum import Enum
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()


class ProviderStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


@dataclass
class CloudProvider:
    name: str
    health_url: str
    deploy_command: Optional[str] = None
    priority: int = 0  # Lower = higher priority
    status: ProviderStatus = ProviderStatus.UNKNOWN
    last_check: Optional[datetime] = None
    consecutive_failures: int = 0


class MultiCloudController:
    """
    Controls failover between multiple cloud providers.
    """
    
    def __init__(self):
        self.providers: List[CloudProvider] = [
            CloudProvider(
                name="Modal Primary",
                health_url="https://nearmiss1193--empire-sovereign-v2-health.modal.run",
                deploy_command="python -m modal deploy modal_deploy.py",
                priority=1
            ),
            CloudProvider(
                name="GCP Cloud Run",
                health_url=os.getenv("GCP_HEALTH_URL", ""),  # Set after deploying to GCP
                deploy_command="gcloud run deploy empire-backup --source .",
                priority=2
            ),
            CloudProvider(
                name="Local Swarm",
                health_url="http://localhost:8080/health",  # Local dashboard
                deploy_command="python continuous_swarm.py",
                priority=3
            ),
        ]
        
        self.active_provider: Optional[CloudProvider] = None
        self.check_interval = 60  # seconds
        self.failure_threshold = 3  # consecutive failures before failover
        self.recovery_threshold = 2  # consecutive successes before failback
        
        # Supabase for state persistence
        self.supabase = None
        self._init_supabase()
    
    def _init_supabase(self):
        """Initialize Supabase client for state persistence."""
        try:
            from supabase import create_client
            url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
            key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            if url and key:
                self.supabase = create_client(url, key)
        except:
            pass
    
    def log(self, msg: str, level: str = "INFO"):
        """Log with timestamp and optionally to Supabase."""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] [{level}] {msg}")
        
        if self.supabase:
            try:
                self.supabase.table("system_logs").insert({
                    "level": level,
                    "event_type": "FAILOVER_CONTROLLER",
                    "message": msg,
                    "metadata": {
                        "active_provider": self.active_provider.name if self.active_provider else None,
                        "timestamp": ts
                    }
                }).execute()
            except:
                pass
    
    def check_health(self, provider: CloudProvider) -> ProviderStatus:
        """Check health of a single provider."""
        if not provider.health_url:
            return ProviderStatus.UNKNOWN
        
        try:
            resp = requests.get(provider.health_url, timeout=10)
            provider.last_check = datetime.now()
            
            if resp.status_code == 200:
                provider.consecutive_failures = 0
                provider.status = ProviderStatus.HEALTHY
                return ProviderStatus.HEALTHY
            elif resp.status_code in [500, 502, 503, 504]:
                provider.consecutive_failures += 1
                provider.status = ProviderStatus.DOWN
                return ProviderStatus.DOWN
            else:
                provider.status = ProviderStatus.DEGRADED
                return ProviderStatus.DEGRADED
                
        except requests.exceptions.Timeout:
            provider.consecutive_failures += 1
            provider.status = ProviderStatus.DOWN
            return ProviderStatus.DOWN
        except requests.exceptions.ConnectionError:
            provider.consecutive_failures += 1
            provider.status = ProviderStatus.DOWN
            return ProviderStatus.DOWN
        except Exception as e:
            self.log(f"Health check error for {provider.name}: {e}", "ERROR")
            provider.status = ProviderStatus.UNKNOWN
            return ProviderStatus.UNKNOWN
    
    def check_all_providers(self) -> Dict[str, ProviderStatus]:
        """Check health of all providers."""
        results = {}
        for provider in self.providers:
            status = self.check_health(provider)
            results[provider.name] = status
            self.log(f"{provider.name}: {status.value}")
        return results
    
    def get_best_healthy_provider(self) -> Optional[CloudProvider]:
        """Get the highest priority healthy provider."""
        healthy = [p for p in self.providers if p.status == ProviderStatus.HEALTHY]
        if not healthy:
            return None
        return min(healthy, key=lambda p: p.priority)
    
    def failover_to(self, provider: CloudProvider):
        """Failover to a specific provider."""
        old = self.active_provider.name if self.active_provider else "None"
        self.log(f"🔄 FAILOVER: {old} → {provider.name}", "WARN")
        
        # Deploy if needed
        if provider.deploy_command and provider.name == "Local Swarm":
            self._ensure_local_running()
        
        self.active_provider = provider
        self._send_alert(
            "Failover Activated",
            f"Active provider changed from {old} to {provider.name}"
        )
    
    def _ensure_local_running(self):
        """Ensure local swarm is running."""
        # Check if Python processes are running
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq python.exe"],
                capture_output=True, text=True
            )
            if "python.exe" not in result.stdout.lower():
                self.log("Starting local swarm as failover...")
                subprocess.Popen(
                    ["python", "continuous_swarm.py"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
                )
        except:
            pass
    
    def _send_alert(self, subject: str, message: str):
        """Send email alert."""
        resend_key = os.getenv("RESEND_API_KEY")
        if not resend_key:
            return
        
        try:
            requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {resend_key}"},
                json={
                    "from": "Empire AI <alerts@aiserviceco.com>",
                    "to": [os.getenv("GHL_EMAIL", "nearmiss1193@gmail.com")],
                    "subject": f"🚨 {subject}",
                    "html": f"<h2>{subject}</h2><p>{message}</p><p>Time: {datetime.now().isoformat()}</p>"
                },
                timeout=10
            )
        except:
            pass
    
    def run_control_loop(self):
        """Main control loop - monitors and fails over."""
        self.log("=" * 60)
        self.log("🌐 MULTI-CLOUD FAILOVER CONTROLLER STARTING")
        self.log("=" * 60)
        
        for p in self.providers:
            self.log(f"  {p.priority}. {p.name}: {p.health_url or 'N/A'}")
        
        self.log("")
        
        while True:
            try:
                # 1. Check all providers
                self.check_all_providers()
                
                # 2. Get best healthy provider
                best = self.get_best_healthy_provider()
                
                if best is None:
                    self.log("⚠️ NO HEALTHY PROVIDERS - ensuring local fallback", "WARN")
                    self._ensure_local_running()
                    
                elif self.active_provider is None:
                    # First run - set active provider
                    self.active_provider = best
                    self.log(f"✅ Initial active provider: {best.name}")
                    
                elif self.active_provider.status == ProviderStatus.DOWN:
                    # Current active is down - failover
                    if self.active_provider.consecutive_failures >= self.failure_threshold:
                        self.failover_to(best)
                        
                elif best.priority < self.active_provider.priority and best.status == ProviderStatus.HEALTHY:
                    # Higher priority provider recovered - failback
                    if best.consecutive_failures == 0:
                        self.log(f"✅ Primary recovered - failing back to {best.name}")
                        self.failover_to(best)
                
                # 3. Status summary
                self.log(f"📊 Active: {self.active_provider.name if self.active_provider else 'None'}")
                
                # 4. Wait
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                self.log("\n🛑 Controller stopped by user")
                break
            except Exception as e:
                self.log(f"❌ Control loop error: {e}", "ERROR")
                time.sleep(30)
    
    def status(self) -> Dict:
        """Get current status of all providers."""
        self.check_all_providers()
        return {
            "active": self.active_provider.name if self.active_provider else None,
            "providers": [
                {
                    "name": p.name,
                    "status": p.status.value,
                    "priority": p.priority,
                    "failures": p.consecutive_failures,
                    "last_check": p.last_check.isoformat() if p.last_check else None
                }
                for p in self.providers
            ]
        }


# ============ CLI ============

def main():
    controller = MultiCloudController()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            import json
            print(json.dumps(controller.status(), indent=2))
            return
        elif sys.argv[1] == "--check":
            controller.check_all_providers()
            return
    
    controller.run_control_loop()


if __name__ == "__main__":
    main()
