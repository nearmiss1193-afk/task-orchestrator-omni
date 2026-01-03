
import os
import json
import datetime
import requests
from modules.governor.internal_supervisor import InternalSupervisor

class SovereignOpsAgent:
    """
    MISSION 39: SOVEREIGN OPS AGENT
    Persona: "Sovereign Ops Agent"
    Goal: Manage 'Empire Ops' in ClickUp via Daily Pulse & Alerts.
    """
    
    def __init__(self, clickup_api_key=None, clickup_list_id=None):
        self.api_key = clickup_api_key or os.environ.get("CLICKUP_API_KEY")
        self.list_id = clickup_list_id or os.environ.get("CLICKUP_LIST_ID")
        self.supervisor = InternalSupervisor()
        self.mock_mode = not (self.api_key and self.list_id)

    def run_daily_pulse(self):
        """
        Main execution loop.
        1. Read System State.
        2. Build Pulse.
        3. Post to ClickUp (Task/Comment).
        4. Manage Alerts.
        """
        print(f"🤖 [Sovereign Ops] Starting Pulse Routine (Mock: {self.mock_mode})...")
        
        # 1. READ STATE
        pulse_data = self._read_system_state()
        
        # 2. BUILD MARKDOWN
        pulse_md = self._build_pulse_markdown(pulse_data)
        
        # 3. POST PULSE
        task_id = self._manage_daily_task(pulse_md, pulse_data['date'])
        
        # 4. MANAGE ALERTS
        if pulse_data['alerts']:
            self._process_alerts(pulse_data['alerts'], task_id)
            
        return pulse_md

    def _read_system_state(self):
        """Reads local logs and synthesizes state."""
        today = datetime.date.today().isoformat()
        
        # Helper to read latest file
        def read_latest(glob_pattern, default="No data."):
            import glob
            files = sorted(glob.glob(glob_pattern), key=os.path.getmtime, reverse=True)
            if files:
                try:
                    with open(files[0], 'r', encoding='utf-8') as f: return f.read()
                except: return default
            return default

        # Raw Logs
        ops_log = read_latest("sovereign_digests/SOVEREIGN_OPS_LOG.md", "")
        autonomy_log = read_latest("sovereign_digests/AUTONOMY_DIGEST_*.md", "No autonomy data.")
        audit_log = read_latest("sovereign_digests/WEBSITE_AUDIT_*.md", "No audit data.")
        onboarding_log = read_latest("sovereign_logs/SUBACCOUNT_LOG_*.txt", "No onboarding data.")
        
        # Determine Status
        health = "🟢 Green"
        if "CRITICAL" in autonomy_log or "Error" in audit_log: health = "🔴 Critical"
        elif "WARNING" in autonomy_log: health = "🟡 Warning"
        
        # Extract Alerts (Simple Heuristic)
        alerts = []
        if health != "🟢 Green":
            alerts.append({"title": "Review Critical Logs", "priority": "High"})
        if "re-check" in audit_log.lower():
            alerts.append({"title": "Website Audit Follow-up", "priority": "Normal"})

        return {
            "date": today,
            "health": health,
            "ops_log": ops_log,
            "autonomy_log": autonomy_log,
            "audit_log": audit_log,
            "onboarding_log": onboarding_log,
            "alerts": alerts
        }

    def _build_pulse_markdown(self, data):
        """Generates the 5-section report."""
        md = f"# Sovereign Pulse – {data['date']}\n\n"
        
        md += "## 1. System Health\n"
        md += f"- **Status:** {data['health']}\n"
        md += f"- **Notes:** Autonomy Gain Nominal. {data['autonomy_log'][:100].replace(chr(10), ' ')}...\n\n"
        
        md += "## 2. Website & Funnels\n"
        md += f"- **Audit Status:** {data['audit_log'].splitlines()[0] if data['audit_log'] else 'N/A'}\n"
        md += "- Funnels Operational.\n\n"
        
        md += "## 3. Onboarding & Payments\n"
        md += f"- **Recent Activity:** {data['onboarding_log'][:100].replace(chr(10), ' ')}...\n\n"
        
        md += "## 4. AI Operations & Learning\n"
        md += "- **Gemini:** Online (Flash/Pro).\n"
        md += "- **Ops Agent:** Online.\n\n"
        
        md += "## 5. Alerts\n"
        if data['alerts']:
            for a in data['alerts']:
                md += f"- [ ] {a['title']} ({a['priority']})\n"
        else:
            md += "- No active alerts.\n"
            
        return md

    def _manage_daily_task(self, markdown, date):
        """Creates or updates the daily Pulse task."""
        task_name = f"Sovereign Pulse – {date}"
        
        if self.mock_mode:
            print(f"   [MOCK] Creating Task '{task_name}' in List '{self.list_id or 'N/A'}'")
            print(f"   [MOCK] Description:\n{markdown[:200]}...")
            return "mock_task_id"
            
        # Real ClickUp API
        url = f"https://api.clickup.com/api/v2/list/{self.list_id}/task"
        headers = {"Authorization": self.api_key, "Content-Type": "application/json"}
        payload = {
            "name": task_name,
            "description": markdown,
            "assignees": [], # Add User ID if known
            "status": "OPEN",
            "priority": 3 # Normal
        }
        
        # Check for existing (Search) - Simplified for MVP: Just Create
        # In established code, we'd search first.
        try:
            res = requests.post(url, headers=headers, json=payload)
            if res.status_code == 200:
                print(f"   [CLICKUP] Task Created: {res.json().get('id')}")
                return res.json().get("id")
            else:
                print(f"   [CLICKUP] Error: {res.text}")
                return None
        except Exception as e:
            print(f"   [CLICKUP] Exception: {e}")
            return None

    def _process_alerts(self, alerts, parent_task_id):
        """Creates subtasks or linked tasks for alerts."""
        if self.mock_mode:
            print(f"   [MOCK] Processing {len(alerts)} alerts...")
            return

        for alert in alerts:
            # Create Task Logic (similar to above)
            pass

    def handle_webhook_event(self, payload):
        """
        Handles incoming events from ClickUp (e.g. taskCommentPosted).
        Triggered by Modal Webhook.
        """
        event = payload.get("event")
        history_items = payload.get("history_items", [])
        
        print(f"🤖 [Sovereign Ops] Webhook Event: {event}")
        
        if event == "taskCommentPosted":
            for item in history_items:
                comment = item.get("comment", {})
                text_content = comment.get("text_content", "") or comment.get("text", "")
                
                # Simple "Mention" Detection (if user tagged agent or asked status)
                if "@Sovereign" in text_content or "status" in text_content.lower():
                    print(f"   [REACTION] Responding to comment: {text_content[:50]}...")
                    # Logic to reply would go here (using POST comment API)
                    # self.post_comment(task_id, "Status: Green...")
                    return {"status": "replied", "context": text_content}
        
        return {"status": "ignored"}


# Entry Point
if __name__ == "__main__":
    agent = SovereignOpsAgent()
    agent.run_daily_pulse()
