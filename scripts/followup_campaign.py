"""
Follow-up SMS + Email campaign for voice drop leads.
Sends via GHL webhook with rate limiting to avoid spam blocks.
"""
import csv, re, time, requests, json, os
from datetime import datetime

GHL_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"

SMS_MESSAGE = """Hey! This is Dan from AI Service Company. We left you a voicemail recently about our AI phone system for local businesses. Did you get a chance to listen?

We're offering a FREE 2-week trial - no commitment. Here's what it does:
- Answers every call 24/7 so you never miss a customer
- Books appointments automatically
- Sends you reviews on Google & Facebook on autopilot
- Runs automated advertising for your business

Interested? Just reply YES or call us at (863) 692-8474. We'll have you set up in 24 hours!"""

EMAIL_SUBJECT = "Did you get our voicemail? Free 2-week AI trial for your business"

EMAIL_BODY = """Hi {name},

I wanted to follow up on the voicemail we left for {business}. We're offering a completely FREE 2-week trial of our AI office system - no strings attached.

Here's what it does for your business:
- Answers every phone call 24/7 (even when you're busy or closed)
- Books appointments automatically onto your calendar  
- Gets you more Google & Facebook reviews on autopilot
- Runs targeted advertising for your business

You never miss a call or customer again. After the trial, it's just $297/month - but there's zero commitment to try it.

Want to see it in action? Just reply to this email or call us at (863) 692-8474. We can have your AI agent live within 24 hours.

Best,
Dan
AI Service Company
(863) 692-8474"""

def normalize_phone(p):
    d = re.sub(r'\D', '', p or '')
    if len(d) == 11 and d.startswith('1'):
        d = d[1:]
    return d if len(d) == 10 else None

def send_sms(phone, msg):
    try:
        r = requests.post(GHL_WEBHOOK, json={"phone": f"+1{phone}", "message": msg}, timeout=10)
        return r.status_code == 200
    except:
        return False

def send_email(email, name, business):
    try:
        body = EMAIL_BODY.format(name=name or "there", business=business or "your business")
        r = requests.post(GHL_WEBHOOK, json={
            "email": email,
            "subject": EMAIL_SUBJECT,
            "message": body
        }, timeout=10)
        return r.status_code == 200
    except:
        return False

def main():
    # Build phone-to-business lookup from enriched CSV
    phone_lookup = {}
    with open("scripts/lakeland_businesses_enriched.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            phone = normalize_phone(row.get("phone", ""))
            if phone:
                phone_lookup[phone] = {
                    "name": row.get("name", ""),
                    "email": row.get("email", ""),
                    "category": row.get("category", "")
                }

    # Also from expansion CSVs
    for csvf in ["scripts/lakeland_expansion.csv", "scripts/lakeland_expansion_r2.csv"]:
        try:
            with open(csvf, "r", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    phone = normalize_phone(row.get("phone", ""))
                    if phone and phone not in phone_lookup:
                        phone_lookup[phone] = {
                            "name": row.get("name", ""),
                            "email": row.get("email", ""),
                            "category": row.get("category", "")
                        }
        except:
            pass

    print(f"Phone lookup built: {len(phone_lookup)} businesses")
    print(f"With emails: {sum(1 for v in phone_lookup.values() if v.get('email'))}")

    # Collect all target phones from voice drop CSVs
    target_phones = set()
    for csvf in ["scripts/sly_voicedrop_batch2_500.csv",
                  r"C:\Users\nearm\Desktop\voicedrop_1000.csv"]:
        try:
            with open(csvf, "r", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    phone = normalize_phone(row.get("Phone", ""))
                    if phone:
                        target_phones.add(phone)
        except Exception as e:
            print(f"Skipping {csvf}: {e}")

    # Add already-contacted phones
    ac_raw = ['3212976079','8132671289','8132792727','4079304455','4077195944','4078847555','8138554461','4073833659','8139716100','4078860204','4073093165','8132819079','3212561234','8134129333','4078802886','4075189355','8135087791','4076052888','4075180880','8135022755','8138753083','4076775400','4072787858','4079606254','4077959250','8131107483','8139490424','4076477777','4078788383','3216098870','7873101338','8132543206','4073356777','3523943318','8131067067','8137272159','8132659702','4074294364','8137984717','4074364414','8134960407','8135039020','4074316795','4079576290','4074831182','8136817183','4076729662','8132036001','4078870104','4078550388','8132072040','4075745177','8134329111','8136509393','8139467711','8134521570','4078787387','3213402590','7275156077','4072176969','8134905211','3527492459','8134942411','8133139253','8131354904','4075202322','8133777321','4072971077','8135938128','8138180600','8137601060','4076969626','4076760076','4073486042','4074103200','4078634856','4073833301','4076368178','6892991931','4072884813','3219262997','4073611860','4079791033','8132653033','4079039444','4074238164','4079681801','8138159280','8138452391','4072726040','4076283450','8137788206','4077100526','4079307309','3213607663','8136548686','4078926617','4075749009','3213214520','4072037037','4075664646','4078463912','3219392168','4076717974','4079102255','8139325511','8139621121','4072884672','8138910400','8883427314','8139973140','4073073076','7276773373','4075390639','8137496863','8138862506','4078035230','8132394685','4078770333','4077018733','8138358900','8139492995','7867639677','8135473226','4072098114','3108097109','8137752276','3214309621','3216243034','4078977050','4076542316','8132704794','8134867285','4073601806','6898887911','4073198985','8132326261','8132031764','4072035138','5719829312','8138867000','6893146219','8136722500','4076630490','4073485607','4073618016','4076720001','4078513437','8638040000','8338990310','8635333838','8635148077','8638607633','8636471515','8639400874','8638756817','8636983766','8636872287','8632209316','8636482958','8632251950','8632585820','8133249311','8638590335','8636602185','8638081799','8632943360','8632254519','8636868151','8632327626','8636658231','4077772071','8636836511','8636074222','8635376408','8634100041','7278230540','8132211154','8634220247','8636042357','8635331220','8135163121','8632594743','8636668392','8638370530','8636566672','8632876388','8633375013','8632131608','8639409950','8635294082','8632988026','8636837500','8636143819','8636659597','8636888834','8636763556','8635336698','8637974400','8638592837','8632686552']
    for p in ac_raw:
        target_phones.add(p[-10:])

    print(f"\nTotal target phones: {len(target_phones)}")

    # Send follow-ups
    sms_sent = 0
    sms_fail = 0
    email_sent = 0
    total = len(target_phones)

    log = open("scripts/followup_log.txt", "w")
    log.write(f"Follow-up Campaign Started: {datetime.now()}\n")
    log.write(f"Total targets: {total}\n\n")

    for i, phone in enumerate(target_phones):
        biz = phone_lookup.get(phone, {})
        name = biz.get("name", "")
        email = biz.get("email", "")

        # Send SMS
        if send_sms(phone, SMS_MESSAGE):
            sms_sent += 1
        else:
            sms_fail += 1

        # Send email if available
        if email:
            if send_email(email, name, name):
                email_sent += 1

        # Progress
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i+1}/{total} | SMS: {sms_sent} | Email: {email_sent}")

        # Rate limit: 2 per second to avoid spam blocks
        time.sleep(0.5)

    summary = f"""
FOLLOW-UP CAMPAIGN COMPLETE
============================
Total targets: {total}
SMS sent: {sms_sent}
SMS failed: {sms_fail}
Emails sent: {email_sent}
Finished: {datetime.now()}
"""
    print(summary)
    log.write(summary)
    log.close()

    # Save summary
    with open("scripts/followup_result.txt", "w") as f:
        f.write(summary)

if __name__ == "__main__":
    main()
