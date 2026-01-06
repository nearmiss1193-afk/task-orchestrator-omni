import os
import json
import datetime
import sqlite3
import requests
from dotenv import load_dotenv

load_dotenv()

class PDRAgent:
    """
    MISSION: PERSONAL DEVELOPMENT & RESEARCH (The "Coach")
    Audits logs, identifies skill gaps, and researches improvements.
    """
    def __init__(self, db_path="empire.db"):
        self.db_path = db_path
        self.brain_logs_limit = 50
        self.vapi_assistant_id = os.getenv("VAPI_ASSISTANT_ID", "1a797f12-e2dd-4f7f-b2c5-08c38c74859a")
        self._init_local_db()

    def _init_local_db(self):
        """Initializes SQLite tables for local testing if they don't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS brain_logs (id INTEGER PRIMARY KEY, message TEXT, level TEXT, timestamp TEXT)")
            c.execute("CREATE TABLE IF NOT EXISTS leads (id INTEGER PRIMARY KEY, status TEXT, created_at TEXT)")
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Local DB Init Warning: {e}")

    def get_supabase(self):
        url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if url and key:
            from supabase import create_client
            return create_client(url, key)
        return None

    def run_audit(self):
        """
        Scans logs for failure patterns or inefficiencies.
        """
        print("🔍 PDRAgent: Commencing System Audit...")
        findings = []
        
        supabase = self.get_supabase()
        if supabase:
            try:
                # 1. Check for recent errors in brain_logs
                res = supabase.table("brain_logs").select("message").in_("level", ["CRITICAL", "ERROR", "ERR"]).order("timestamp", desc=True).limit(self.brain_logs_limit).execute()
                if res.data:
                    findings.append({"type": "LOG_ERRORS", "data": [e['message'] for e in res.data]})
                
                # 2. Check for lead conversion staleness
                stale_threshold = (datetime.datetime.now() - datetime.timedelta(hours=24)).isoformat()
                res = supabase.table("contacts_master").select("id", count="exact").eq("status", "new").lt("created_at", stale_threshold).execute()
                if res.count > 0:
                    findings.append({"type": "STALE_LEADS", "count": res.count})
                
                return findings
            except Exception as e:
                print(f"⚠️ Supabase Audit Warning: {e}. Falling back to SQLite.")

        # Fallback to SQLite
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # 1. Check for recent errors in brain_logs
            c.execute("SELECT message FROM brain_logs WHERE level IN ('CRITICAL', 'ERROR', 'ERR') ORDER BY timestamp DESC LIMIT ?", (self.brain_logs_limit,))
            errors = c.fetchall()
            if errors:
                findings.append({"type": "LOG_ERRORS", "data": [e[0] for e in errors]})
            
            # 2. Check for lead conversion staleness
            c.execute("SELECT COUNT(*) FROM leads WHERE status = 'new' AND created_at < datetime('now', '-24 hours')")
            stale_leads = c.fetchone()[0]
            if stale_leads > 0:
                findings.append({"type": "STALE_LEADS", "count": stale_leads})
                
            conn.close()
        except Exception as e:
            print(f"❌ SQLite Audit Error: {e}")
            
        return findings

    def research_improvement(self, finding):
        """
        Generates a development directive based on findings.
        In a full version, this would use a Search tool or LLM.
        """
        print(f"🧠 PDRAgent: Researching improvement for {finding['type']}...")
        
        if finding['type'] == "LOG_ERRORS":
            return {
                "agent": "Orchestrator",
                "directive": "Investigate recurring patterns in critical logs and implement retry logic for transient API failures.",
                "priority": "HIGH"
            }
        elif finding['type'] == "STALE_LEADS":
            return {
                "agent": "Sarah",
                "directive": "Review outreach schedule. Leads older than 24h detected without follow-up. Consider a 'Re-engagement' nudge prompt.",
                "priority": "MEDIUM"
            }
        
        return None

    def dispatch_evolution(self, directive):
        """
        Sends the directive to the InternalSupervisor (Governor).
        """
        if not directive: return
        
        print(f"🚀 PDRAgent: Dispatching Evolution Directive to {directive['agent']}...")
        
        timestamp = datetime.datetime.now().isoformat()
        message = f"[SIGNAL_EVOLUTION] {json.dumps(directive)}"
        
        supabase = self.get_supabase()
        if supabase:
            try:
                supabase.table("brain_logs").insert({"message": message, "level": "INFO", "timestamp": timestamp}).execute()
                print("✅ Evolution Signal Logged to Supabase.")
                return
            except Exception as e:
                print(f"⚠️ Supabase Dispatch Warning: {e}")

        # Fallback/Local
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("INSERT INTO brain_logs (message, level, timestamp) VALUES (?, ?, ?)", 
                      (message, "INFO", timestamp))
            conn.commit()
            conn.close()
            print("✅ Evolution Signal Logged to SQLite.")
        except Exception as e:
            print(f"❌ SQLite Dispatch Error: {e}")

    def execute_loop(self):
        """
        The main background execution cycle.
        """
        findings = self.run_audit()
        for f in findings:
            directive = self.research_improvement(f)
            self.dispatch_evolution(directive)

if __name__ == "__main__":
    agent = PDRAgent()
    agent.execute_loop()
