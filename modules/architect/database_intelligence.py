import os
import json
from supabase import create_client

class DatabaseArchitect:
    """
    MISSION: SUPABASE INTELLIGENCE (The "Architect")
    Handles schema migrations, table validation, and query optimization.
    Eliminates manual SQL execution for routine updates.
    """
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        self.client = create_client(self.url, self.key) if self.url and self.key else None

    def execute_migration(self, sql_command):
        """
        Executes raw SQL via RPC (Remote Procedure Call) if 'exec_sql' function exists,
        or logs instructions if direct execution is blocked.
        """
        if not self.client:
            return {"status": "error", "message": "Missing Credentials"}

        try:
            # Try calling a helper RPC function 'exec_sql' if you installed it
            # Otherwise, use the client to perform equivalent operations if possible
            # For DDL (CREATE/ALTER), we strictly need RPC or Dashboard.
            
            # NOTE: To enable this fully, the User must create this ONE function manually once:
            # create or replace function exec_sql(query text) returns void as $$ begin execute query; end; $$ language plpgsql security definer;
            
            response = self.client.rpc("exec_sql", {"query": sql_command}).execute()
            return {"status": "success", "data": response.data}
        except Exception as e:
            # Fallback: Check if it's a known error (missing function)
            if "function exec_sql" in str(e).lower():
                return {"status": "blocked", "message": "RPC 'exec_sql' missing. Please create it in Dashboard."}
            return {"status": "error", "message": str(e)}

    def validate_schema(self, required_tables):
        """
        Checks if tables exist.
        """
        missing = []
        for table in required_tables:
            try:
                self.client.table(table).select("id").limit(1).execute()
            except:
                missing.append(table)
        return {"status": "checked", "missing": missing}

    def heal_schema(self):
        """
        Auto-fixes known missing columns.
        """
        # Example: Add 'level' to brain_logs
        sql = "ALTER TABLE brain_logs ADD COLUMN IF NOT EXISTS level text DEFAULT 'INFO';"
        return self.execute_migration(sql)
