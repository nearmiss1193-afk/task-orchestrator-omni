"""
SQL to create event_log table - Run in Supabase SQL Editor
"""

SQL = """
CREATE TABLE IF NOT EXISTS event_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    event_type VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    context JSONB
);

CREATE INDEX IF NOT EXISTS idx_event_log_phone ON event_log(phone);
CREATE INDEX IF NOT EXISTS idx_event_log_type ON event_log(event_type);
"""

import requests

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}


def supabase_upsert_event_log(
    event_type: str,
    phone: str = None,
    success: bool = True,
    error_message: str = None,
    retry_count: int = 0,
    context: dict = None
) -> bool:
    """Log an event (success or failure) to event_log table"""
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/event_log",
            headers=HEADERS,
            json={
                "event_type": event_type,
                "phone": phone,
                "success": success,
                "error_message": error_message,
                "retry_count": retry_count,
                "context": context or {}
            },
            timeout=10
        )
        return r.status_code in [200, 201]
    except Exception as e:
        print(f"Event log failed: {e}")
        return False


def test_event_log():
    """Test if event_log table exists"""
    r = requests.get(f"{SUPABASE_URL}/rest/v1/event_log?limit=1", headers=HEADERS)
    print(f"event_log table status: {r.status_code}")
    if r.status_code == 404:
        print("\\nTable doesn't exist. Run this SQL in Supabase SQL Editor:")
        print(SQL)
    return r.status_code == 200


if __name__ == "__main__":
    test_event_log()
