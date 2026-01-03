
import modal
import sys

# Modal client compatibility fix
# Usage: python test_lookup.py
try:
    f = modal.Function.lookup("ghl-omni-automation", "research_lead_logic")
    print("✅ Function found!")
    # Call with a dummy ID to see if it wakes up
    res = f.remote("test_id") 
    print(f"Response: {res}")
except AttributeError:
    print("❌ Method not found. Checking installed version...")
    import modal
    print(f"Modal Version: {modal.__version__}")
except Exception as e:
    print(f"❌ Error: {e}")
