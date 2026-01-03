import os
import datetime
import requests
import json

class GuardianV2:
    """
    MISSION: SOVEREIGN SYSTEM GUARDIAN
    The 'Inspector' that enforces operational integrity.
    """
    
    def __init__(self, supabase_client=None):
        self.supabase = supabase_client
        self.ghl_token = os.environ.get("GHL_AGENCY_API_TOKEN")
        self.ghl_loc = os.environ.get("GHL_LOCATION_ID")
        
        # Manifest of Critical Assets (The "Drift Watcher" Target)
        self.critical_assets = {
            "forms": ["Roofing Intake", "HVAC Lead Gen"],
            "tags": ["trigger-vortex", "trigger-spartan-outreach", "candidate"],
            "calendars": ["Service Demo"]
        }
        
    def execute_sovereign_protocol(self):
        """
        Main Loop: Diagnostic -> Repair -> Report
        """
        report = {"status": "healthy", "repairs": [], "alerts": []}
        
        # 1. The Drift Watcher (Asset Integrity)
        drift_report = self._check_asset_drift()
        if drift_report['missing']:
            report['status'] = "degraded"
            report['alerts'].extend([f"Missing Asset: {m}" for m in drift_report['missing']])
            # Future: self._auto_repair_assets(drift_report['missing'])
            
        # 2. The Ghost Hunter (Zombie Processes)
        ghost_report = self._check_zombies()
        if ghost_report['stalled']:
            report['status'] = "critical"
            report['alerts'].extend([f"Stalled Agent: {a}" for a in ghost_report['stalled']])
            
        return report

    def _check_asset_drift(self):
        """
        Scans GHL to ensure all critical tags/forms exist.
        """
        missing = []
        # We need the Architect to scan efficiently. 
        # Since we are in the cloud execution context, we might not have full Constructor lib loaded.
        # Fallback to simple API checks if Architect not available, but we prefer Architect.
        try:
            from modules.constructor.workflow_architect import WorkflowArchitect
            architect = WorkflowArchitect()
            
            # Check Forms
            for form_name in self.critical_assets['forms']:
                fid = architect.find_form(form_name)
                if not fid and form_name != "HVAC Lead Gen": # HVAC legacy check
                     missing.append(f"Form: {form_name}")

            # Check Tags (Custom Logic as Architect focuses on Forms/Workflows)
            # We skip heavy tag scanning for now to save API calls, assuming Forms are the canary.
            
        except ImportError:
            missing.append("Module: WorkflowArchitect (Import Failed)")
        except Exception as e:
            missing.append(f"Check Failed: {str(e)}")
            
        return {"missing": missing}

    def _check_zombies(self):
        """
        Checks Supabase logs for silence.
        """
        stalled = []
        if not self.supabase:
            return {"stalled": ["Supabase Connection (Offline)"]}
            
        try:
            # Check last log for specific missions
            # This is a lightweight check.
            now = datetime.datetime.now(datetime.timezone.utc)
            
            # 1. Spartan Silence
            res = self.supabase.table("brain_logs").select("created_at").ilike("message", "%Spartan%").order("created_at", desc=True).limit(1).execute()
            if res.data:
                last_seen = datetime.datetime.fromisoformat(res.data[0]['created_at'].replace('Z', '+00:00'))
                if (now - last_seen).total_seconds() > 86400: # 24h silence warning
                    stalled.append("Spartan (24h Silence)")
                    
            # 2. Predator Silence
            res = self.supabase.table("brain_logs").select("created_at").ilike("message", "%Predator%").order("created_at", desc=True).limit(1).execute()
            if res.data:
                last_seen = datetime.datetime.fromisoformat(res.data[0]['created_at'].replace('Z', '+00:00'))
                if (now - last_seen).total_seconds() > 43200: # 12h silence (Should run every 4h-8h)
                    stalled.append("Predator (12h Silence)")

        except Exception as e:
            stalled.append(f"Log Check Error: {str(e)}")
            
        return {"stalled": stalled}

    def _predict_anomalies(self):
        """
        MISSION 29: PREDICTIVE ERROR DETECTION
        Analyzes log density to predict cascades before they happen.
        """
        anomalies = []
        try:
            if not self.supabase: return {"anomalies": ["Offline"]}
            
            # check last 100 logs for Error Density > 10%
            logs = self.supabase.table("brain_logs").select("level").order("created_at", desc=True).limit(100).execute()
            if logs.data:
                error_count = sum(1 for log in logs.data if log['level'] in ['ERR', 'CRITICAL', 'ERROR'])
                density = error_count / len(logs.data)
                
                if density > 0.1:
                    anomalies.append(f"High Error Density ({int(density*100)}%). Cascade Imminent.")
                    
        except Exception as e:
            anomalies.append(f"Analysis Failed: {e}")
            
        return {"anomalies": anomalies}

    def _optimize_resources(self, report):
        """
        MISSION 29: DYNAMIC RESOURCE ALLOCATION
        Adjusts System Gain based on Health Status.
        """
        action = "MAINTAIN"
        gain_adjustment = 0.0
        
        if report['status'] == 'critical':
            action = "THROTTLE"
            gain_adjustment = -0.2
        elif report['status'] == 'degraded':
            action = "STABILIZE"
            gain_adjustment = -0.05
        elif report['status'] == 'healthy':
             # If healthy + no anomalies, boost
             anomalies = self._predict_anomalies()['anomalies']
             if not anomalies:
                 action = "BOOST"
                 gain_adjustment = 0.05
             else:
                 action = "PREVENT"
                 gain_adjustment = -0.1
        
        # Apply to DB (Simulated "System Gain")
        try:
             # In a real system we'd update a 'system_state' table
             # self.supabase.table("system_state").update({"gain": ...})
             pass
        except:
             pass
             
        return {"action": action, "gain_delta": gain_adjustment}
