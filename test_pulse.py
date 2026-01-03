
import os
import sys
from unittest.mock import MagicMock

# Mock Supabase
class MockSupabase:
    def table(self, name): return self
    def select(self, *args, **kwargs): return self
    def limit(self, *args): return self
    def execute(self): 
        mock_res = MagicMock()
        mock_res.data = []
        mock_res.count = 42
        return mock_res
    def upsert(self, *args, **kwargs): return self

# Setup environment to allow imports
sys.path.append(os.getcwd())

from modules.governor.internal_supervisor import InternalSupervisor

def test_pulse():
    print("🧪 Testing Sovereign Pulse...")
    supervisor = InternalSupervisor()
    
    # Run Digest
    mock_db = MockSupabase()
    output = supervisor.generate_sovereign_digest(mock_db)
    
    print("\n[RESULT PREVIEW]")
    print(output)
    
if __name__ == "__main__":
    test_pulse()
