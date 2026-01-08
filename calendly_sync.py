"""
CALENDLY INTEGRATION
====================
Sync bookings to GHL and manage calendar availability.
"""
import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

CALENDLY_API_KEY = os.getenv('CALENDLY_API_KEY', '')
CALENDLY_BASE_URL = "https://api.calendly.com"
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"


def get_headers() -> dict:
    return {
        "Authorization": f"Bearer {CALENDLY_API_KEY}",
        "Content-Type": "application/json"
    }


def get_current_user() -> dict:
    """Get current Calendly user info"""
    
    if not CALENDLY_API_KEY:
        return mock_user()
    
    try:
        response = requests.get(
            f"{CALENDLY_BASE_URL}/users/me",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            return response.json().get('resource', {})
        return {"error": response.text}
    except Exception as e:
        return {"error": str(e)}


def get_event_types() -> list:
    """Get all event types for the user"""
    
    if not CALENDLY_API_KEY:
        return mock_event_types()
    
    user = get_current_user()
    user_uri = user.get('uri')
    
    if not user_uri:
        return []
    
    try:
        response = requests.get(
            f"{CALENDLY_BASE_URL}/event_types",
            headers=get_headers(),
            params={"user": user_uri}
        )
        
        if response.status_code == 200:
            return response.json().get('collection', [])
        return []
    except Exception as e:
        print(f"[ERROR] {e}")
        return []


def get_scheduled_events(days: int = 7) -> list:
    """Get scheduled events for the next X days"""
    
    if not CALENDLY_API_KEY:
        return mock_events()
    
    user = get_current_user()
    user_uri = user.get('uri')
    
    if not user_uri:
        return []
    
    min_time = datetime.now().isoformat() + "Z"
    max_time = (datetime.now() + timedelta(days=days)).isoformat() + "Z"
    
    try:
        response = requests.get(
            f"{CALENDLY_BASE_URL}/scheduled_events",
            headers=get_headers(),
            params={
                "user": user_uri,
                "min_start_time": min_time,
                "max_start_time": max_time,
                "status": "active"
            }
        )
        
        if response.status_code == 200:
            return response.json().get('collection', [])
        return []
    except Exception as e:
        print(f"[ERROR] {e}")
        return []


def sync_booking_to_ghl(event: dict) -> dict:
    """Sync a Calendly booking to GHL"""
    
    invitee = event.get('invitee', {})
    
    # Create/update contact in GHL via webhook
    payload = {
        "phone": invitee.get('phone', ''),
        "email": invitee.get('email', ''),
        "name": invitee.get('name', 'Calendly Booking'),
        "message": f"📅 Booking confirmed for {event.get('name', 'Meeting')} on {event.get('start_time', 'TBD')}",
        "source": "calendly"
    }
    
    try:
        response = requests.post(GHL_SMS_WEBHOOK, json=payload)
        return {"synced": True, "ghl_response": response.status_code}
    except Exception as e:
        return {"synced": False, "error": str(e)}


def handle_webhook(payload: dict) -> dict:
    """Handle Calendly webhook events"""
    
    event_type = payload.get('event')
    event_data = payload.get('payload', {})
    
    if event_type == 'invitee.created':
        # New booking
        print(f"[CALENDLY] New booking: {event_data.get('name')}")
        return sync_booking_to_ghl(event_data)
    
    elif event_type == 'invitee.canceled':
        # Booking cancelled
        print(f"[CALENDLY] Cancelled: {event_data.get('name')}")
        notify_cancellation(event_data)
        return {"handled": True, "action": "cancelled"}
    
    return {"handled": False, "event": event_type}


def notify_cancellation(event: dict):
    """Notify about booking cancellation"""
    invitee = event.get('invitee', {})
    
    message = f"❌ Booking cancelled: {invitee.get('name', 'Customer')} - {event.get('name', 'Meeting')}"
    
    try:
        requests.post(GHL_SMS_WEBHOOK, json={
            "phone": os.getenv('TEST_PHONE', '+13529368152'),
            "message": message
        })
    except:
        pass


def get_booking_link(event_type_name: str = "demo") -> str:
    """Get booking link for an event type"""
    
    event_types = get_event_types()
    
    for et in event_types:
        if event_type_name.lower() in et.get('name', '').lower():
            return et.get('scheduling_url', '')
    
    return ""


# Mock functions
def mock_user() -> dict:
    return {
        "uri": "mock_user_uri",
        "name": "AI Service Co",
        "email": "owner@aiserviceco.com",
        "mock": True,
        "message": "Calendly not configured - add CALENDLY_API_KEY to .env"
    }


def mock_event_types() -> list:
    return [
        {"name": "15 Minute Demo", "duration": 15, "scheduling_url": "https://calendly.com/aiserviceco/demo"},
        {"name": "30 Minute Consultation", "duration": 30, "scheduling_url": "https://calendly.com/aiserviceco/consult"},
    ]


def mock_events() -> list:
    return [
        {"name": "Demo Call", "start_time": "2026-01-08T10:00:00Z", "invitee": {"name": "John Smith", "email": "john@example.com"}},
        {"name": "Consultation", "start_time": "2026-01-08T14:00:00Z", "invitee": {"name": "Jane Doe", "email": "jane@example.com"}},
    ]


def get_api_status() -> dict:
    return {
        "configured": bool(CALENDLY_API_KEY),
        "api_key_set": bool(CALENDLY_API_KEY)
    }


if __name__ == "__main__":
    print("Calendly Status:")
    print(json.dumps(get_api_status(), indent=2))
    
    print("\nEvent Types:")
    for et in get_event_types():
        print(f"  - {et.get('name')}: {et.get('scheduling_url', 'N/A')}")
    
    print("\nUpcoming Events:")
    for event in get_scheduled_events():
        print(f"  - {event.get('name')}: {event.get('start_time')}")
