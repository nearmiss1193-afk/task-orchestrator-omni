
import sys
import os

# Add module path
sys.path.append(os.path.join(os.getcwd(), "modules", "expanse"))

try:
    from vapi_bridge import VapiBridge
    from descript_bridge import DescriptBridge
    
    print("✅ Classes Imported Successfully")
    
    v = VapiBridge(api_key="test")
    d = DescriptBridge(api_key="test")
    
    print(f"✅ VapiBridge Initialized: {v.base_url}")
    print(f"✅ DescriptBridge Initialized: {d.base_url}")
    
except ImportError as e:
    print(f"❌ Import Failed: {e}")
except Exception as e:
    print(f"❌ Initialization Failed: {e}")
