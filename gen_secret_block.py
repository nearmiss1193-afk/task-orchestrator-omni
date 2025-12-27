
import os

def gen():
    try:
        sb_url = ""
        sb_key = ""
        with open("modules/orchestrator/dashboard/.env.local", "r", encoding="utf-8-sig") as f:
            for line in f:
                parts = line.strip().split("=", 1)
                if len(parts) == 2:
                    k, v = parts
                    if k == "NEXT_PUBLIC_SUPABASE_URL": sb_url = v.strip('"')
                    if k == "SUPABASE_SERVICE_ROLE_KEY": sb_key = v.strip('"')
        
        # New Key from User
        gemini_key = "AIzaSyB_WzpN1ASQssu_9ccfweWFPfoRknVUlHU"

        with open("secret_block.txt", "w") as out:
            out.write(f'VAULT = modal.Secret.from_dict({{\n')
            out.write(f'    "GEMINI_API_KEY": "{gemini_key}",\n')
            out.write(f'    "SUPABASE_URL": "{sb_url}",\n')
            out.write(f'    "SUPABASE_SERVICE_ROLE_KEY": "{sb_key}"\n')
            out.write(f'}})\n')
        
    except Exception as e:
        print(e)

if __name__ == "__main__":
    gen()
