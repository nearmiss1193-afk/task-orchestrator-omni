"""TURBO - Direct contact execution - skip all checks"""
import requests
import json
import psycopg2
import re
import time

# Direct creds
VAPI_KEY = "c23c884d-0008-4b14-ad5d-530e98d0c9da"
VAPI_PHONE_ID = "8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e"
SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
GHL_SMS = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"

def validate_phone(phone_str):
    if not phone_str: return False, None
    cleaned = re.sub(r'\D', '', str(phone_str))
    if len(cleaned) < 10: return False, None
    # Get last 10 digits
    digits = cleaned[-10:]
    area_code = digits[:3]
    # Reject fake patterns
    if digits == "9999999999" or digits == "0000000000":
        return False, None
    if "555" in digits[3:6]:  # 555 exchange is fake
        return False, None
    # Reject Canadian area codes
    canadian = ["204","226","236","249","250","289","306","343","365","367","403","416","418","431","437","438","450","506","514","519","548","579","581","587","604","613","639","647","705","709","778","780","782","807","819","825","867","873","902","905"]
    if area_code in canadian:
        return False, None
    return True, f"+1{digits}"

def main():
    print("=== TURBO CONTACTOR ===")
    
    conn = psycopg2.connect(
        host="db.rzcpfwkygdvoshtwxncs.supabase.co",
        port=5432, database="postgres", user="postgres", password="Inez11752990@"
    )
    cur = conn.cursor()
    
    # Get ALL leads with phones - we'll filter inline
    cur.execute("""
        SELECT id, company_name, phone, email 
        FROM leads 
        WHERE phone IS NOT NULL 
        AND phone NOT LIKE '%9999%' 
        AND phone NOT LIKE '%0000%'
        LIMIT 20
    """)
    all_leads = cur.fetchall()
    print(f"Checking {len(all_leads)} leads with phones")
    
    for lead_id, company, phone, email in all_leads:
        valid, clean = validate_phone(phone)
        if not valid:
            print(f"  {company}: Invalid phone {phone}")
            continue
        
        print(f"\n🚀 Contacting {company} at {clean}")
        
        # CALL
        try:
            resp = requests.post(
                "https://api.vapi.ai/call",
                headers={"Authorization": f"Bearer {VAPI_KEY}", "Content-Type": "application/json"},
                json={
                    "type": "outboundPhoneCall",
                    "phoneNumberId": VAPI_PHONE_ID,
                    "assistantId": SARAH_ID,
                    "customer": {"number": clean, "name": company}
                },
                timeout=30
            )
            if resp.status_code in [200, 201]:
                print(f"   ✅ CALL INITIATED")
                
                # SMS
                msg = f"Hi! Sarah here from AI Service Co. Just tried calling about automating your phones. Chat soon? (352) 758-5336"
                sms = requests.post(GHL_SMS, json={"phone": clean, "message": msg}, timeout=15)
                if sms.status_code in [200, 201]:
                    print(f"   ✅ SMS SENT")
                
                # Update status
                cur.execute("UPDATE leads SET status = 'contacted' WHERE id = %s", (lead_id,))
                conn.commit()
            else:
                print(f"   ❌ Call failed: {resp.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(3)
    
    print("\n=== DONE ===")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
