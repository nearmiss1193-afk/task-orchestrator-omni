
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("VAPI_PRIVATE_KEY")
print(f"VAPI_PRIVATE_KEY: {'[FOUND]' if key else '[MISSING]'}")
