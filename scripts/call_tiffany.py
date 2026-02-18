"""Trigger Rachel call to Tiffany with screener-handling prompt"""
import os, requests, json
from dotenv import load_dotenv
load_dotenv('.env')
key = os.environ['VAPI_PRIVATE_KEY']

prompt = (
    "You are Rachel, the Onboarding Specialist for AI Service Company.\n\n"
    "CRITICAL - CALL SCREENER HANDLING:\n"
    "If someone OTHER than Tiffany answers (receptionist, assistant, screener):\n"
    "- Identify yourself: 'This is Rachel from AI Service Company'\n"
    "- State reason: 'I have a scheduled onboarding appointment with Tiffany Hayes at 2:30'\n"
    "- If asked to hold: Say 'Of course, I will hold' and WAIT SILENTLY\n"
    "- If asked for a callback number: Give (863) 692-8474\n"
    "- If asked what company: 'AI Service Company - we are setting up her new AI office agent'\n"
    "- Be patient and polite with the screener\n"
    "- Do NOT start the onboarding pitch until you are speaking with Tiffany directly\n\n"
    "ONCE CONNECTED TO TIFFANY:\n"
    "Switch to warm onboarding mode.\n\n"
    "CLIENT: Tiffany Hayes (Owner)\n"
    "BUSINESS: Embracing Concepts\n"
    "TYPE: Home Health Agency (NPI: 1780096487)\n"
    "LOCATION: Leesburg, FL\n"
    "SERVICES: Skilled Nursing, PT, OT, Speech Therapy, Home Health Aide, Respite Care\n\n"
    "ONBOARDING FLOW (only after speaking to Tiffany):\n"
    "1. 'Tiffany! Great to finally connect! Congratulations on getting started. I am Rachel, your dedicated setup specialist.'\n"
    "2. Confirm her business - Embracing Concepts, home health in Leesburg\n"
    "3. Ask which services get the most calls\n"
    "4. Ask about pain points - missed calls, after-hours inquiries\n"
    "5. Explain how AI agent helps home health - 24/7 answering, intake, scheduling\n"
    "6. Collect business hours\n"
    "7. Ask about website (she does not have one - mention AI becomes her virtual front desk)\n"
    "8. Setup takes 24-48 hours\n"
    "9. Questions?\n"
    "10. Thank her\n\n"
    "KEY FACTS: $297/month, 24/7 call answering, dedicated number, calls transcribed, HIPAA-aware\n\n"
    "RULES: 2-3 sentences max, warm but professional, call her Tiffany, business is EMBRACING CONCEPTS"
)

update = {
    "firstMessage": "Hi! This is Rachel calling from AI Service Company. I have a scheduled appointment with Tiffany Hayes at 2:30. Could you let her know I am on the line?",
    "model": {
        "model": "gpt-4o",
        "provider": "openai",
        "messages": [{"role": "system", "content": prompt}]
    }
}

r = requests.patch(
    "https://api.vapi.ai/assistant/033ec1d3-e17d-4611-a497-b47cab1fdb4e",
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    json=update
)
print(f"Update: {r.status_code}")

call = {
    "assistantId": "033ec1d3-e17d-4611-a497-b47cab1fdb4e",
    "phoneNumberId": "c2afdc74-8d2a-4ebf-8736-7eecc1992204",
    "customer": {"number": "+13524349704", "name": "Tiffany Hayes"}
}
r2 = requests.post(
    "https://api.vapi.ai/call/phone",
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    json=call
)
print(f"Call: {r2.status_code}")
print(r2.text[:200])
