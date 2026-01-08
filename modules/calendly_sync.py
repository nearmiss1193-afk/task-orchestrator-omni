import os
import requests
from dotenv import load_dotenv

load_dotenv()

CALENDLY_API_KEY = os.getenv("CALENDLY_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

def sync_calendly_bookings(supabase_client):
    """
    Fetches recent bookings from Calendly and updates Lead status in Supabase.
    """
    if not CALENDLY_API_KEY:
        print("[CALENDLY] Key missing, skipping sync.")
        return

    headers = {
        "Authorization": f"Bearer {CALENDLY_API_KEY}",
        "Content-Type": "application/json"
    }

    # 1. Get Current User URI
    user_resp = requests.get("https://api.calendly.com/users/me", headers=headers)
    if user_resp.status_code != 200:
        print(f"[CALENDLY] User Fetch Error: {user_resp.text}")
        return
    user_uri = user_resp.json()['resource']['uri']

    # 2. Get Events for User
    params = {
        "user": user_uri,
        "status": "active",
        "min_start_time": "2024-01-01T00:00:00Z" # Simplification for v1
    }
    
    events_resp = requests.get("https://api.calendly.com/scheduled_events", headers=headers, params=params)
    if events_resp.status_code != 200:
        print(f"[CALENDLY] Events Fetch Error: {events_resp.text}")
        return

    events = events_resp.json().get('collection', [])
    print(f"[CALENDLY] Found {len(events)} active events.")

    for event in events:
        # Get invitee email
        event_uuid = event['uri'].split('/')[-1]
        invitees_resp = requests.get(f"https://api.calendly.com/scheduled_events/{event_uuid}/invitees", headers=headers)
        if invitees_resp.status_code == 200:
            invitees = invitees_resp.json().get('collection', [])
            for invitee in invitees:
                email = invitee['email']
                print(f"[CALENDLY] Booking found: {email} at {event['start_time']}")
                
                # Update Supabase
                try:
                    data = supabase_client.table('leads').update({
                        'status': 'converted', 
                        'metadata': {'calendly_event': event_uuid, 'booking_time': event['start_time']}
                    }).eq('email', email).execute()
                    if data.data:
                        print(f"[SUPABASE] Updated lead status for {email}")
                except Exception as e:
                    print(f"[SUPABASE] Error updating lead: {e}")
