"""
WEATHER OUTREACH
================
Weather-triggered proactive outreach.
"""
import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
RESEND_API_KEY = os.getenv('RESEND_API_KEY')

# Weather triggers and messages
WEATHER_TRIGGERS = {
    "heat_wave": {
        "condition": lambda temp: temp >= 95,
        "service": "hvac",
        "sms": "🌡️ Heat wave coming to {city}! Make sure your AC is ready. Need a tune-up? Reply YES for a free inspection.",
        "email_subject": "Is Your AC Ready for the Heat Wave?",
        "urgency": "high"
    },
    "cold_snap": {
        "condition": lambda temp: temp <= 35,
        "service": "hvac",
        "sms": "❄️ Freezing temps headed to {city}! Protect your pipes and furnace. Need a check? Reply YES.",
        "email_subject": "Protect Your Home from the Cold Snap",
        "urgency": "high"
    },
    "storm_warning": {
        "condition": lambda data: data.get('wind', 0) >= 40,
        "service": "roofing",
        "sms": "🌩️ Storm warning for {city}! Free roof inspection before the storm. Reply YES to schedule.",
        "email_subject": "Free Roof Inspection Before the Storm",
        "urgency": "urgent"
    },
    "heavy_rain": {
        "condition": lambda data: data.get('rain', 0) >= 2,
        "service": "plumbing",
        "sms": "🌧️ Heavy rain expected! Check your drains and gutters. Need help? Reply YES.",
        "email_subject": "Prepare Your Plumbing for Heavy Rain",
        "urgency": "medium"
    }
}


def check_weather(city: str = "Tampa", state: str = "FL") -> dict:
    """Check weather for a location (mock - would use real API)"""
    # In production, use OpenWeatherMap, WeatherAPI, etc.
    # This is a mock response
    return {
        "city": city,
        "state": state,
        "temp_high": 97,
        "temp_low": 78,
        "wind": 15,
        "rain": 0.5,
        "conditions": "Partly Cloudy",
        "forecast_date": (datetime.now() + timedelta(days=1)).isoformat()
    }


def detect_triggers(weather: dict) -> list:
    """Detect which weather triggers are active"""
    
    active = []
    
    for trigger_name, trigger in WEATHER_TRIGGERS.items():
        condition = trigger["condition"]
        
        if trigger_name == "heat_wave" and condition(weather.get('temp_high', 0)):
            active.append(trigger_name)
        elif trigger_name == "cold_snap" and condition(weather.get('temp_low', 100)):
            active.append(trigger_name)
        elif trigger_name in ["storm_warning", "heavy_rain"] and condition(weather):
            active.append(trigger_name)
    
    return active


def send_weather_outreach(contacts: list, trigger: str, weather: dict):
    """Send outreach to contacts based on weather trigger"""
    
    trigger_data = WEATHER_TRIGGERS.get(trigger)
    if not trigger_data:
        return {"error": "Unknown trigger"}
    
    city = weather.get('city', 'your area')
    results = []
    
    for contact in contacts:
        # Check if contact matches service type
        if contact.get('interested_services') and trigger_data['service'] not in contact.get('interested_services', []):
            continue
        
        # Send SMS
        if contact.get('phone'):
            message = trigger_data['sms'].format(city=city)
            try:
                requests.post(GHL_SMS_WEBHOOK, json={"phone": contact['phone'], "message": message})
                results.append({"contact": contact['name'], "channel": "sms", "sent": True})
            except:
                results.append({"contact": contact['name'], "channel": "sms", "sent": False})
    
    return {
        "trigger": trigger,
        "weather": weather,
        "contacts_reached": len(results),
        "results": results
    }


def run_weather_check(contacts: list):
    """Run weather check and trigger appropriate outreach"""
    
    weather = check_weather("Tampa", "FL")
    triggers = detect_triggers(weather)
    
    print(f"[WEATHER] {weather['city']}: {weather['temp_high']}°F high, {weather['conditions']}")
    print(f"[TRIGGERS] Active: {triggers or 'None'}")
    
    all_results = []
    for trigger in triggers:
        result = send_weather_outreach(contacts, trigger, weather)
        all_results.append(result)
        print(f"[OUTREACH] {trigger}: {result.get('contacts_reached', 0)} reached")
    
    return all_results


if __name__ == "__main__":
    test_contacts = [
        {"name": "John Smith", "phone": "+13529368152", "interested_services": ["hvac"]},
        {"name": "Jane Doe", "phone": "+13529368152", "interested_services": ["roofing"]},
    ]
    
    results = run_weather_check(test_contacts)
    print(json.dumps(results, indent=2))
