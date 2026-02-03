
import os

def check_env():
    with open('.env', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if 'SUPABASE_SERVICE_ROLE_KEY' in line:
                key = line.split('=')[1].strip()
                print(f"Key Length: {len(key)}")
                print(f"Key Start: {key[:10]}...")
                print(f"Key End: ...{key[-10:]}")
                return key
    return None

if __name__ == "__main__":
    check_env()
