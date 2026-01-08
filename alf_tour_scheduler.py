"""
ALF TOUR SCHEDULER
==================
Sarah books ALF facility tours automatically.
"""
import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"

# Sample ALF facilities with tour availability
ALF_FACILITIES = {
    "sunrise_tampa": {
        "name": "Sunrise Senior Living Tampa",
        "address": "123 Care Lane, Tampa, FL",
        "phone": "(813) 555-0101",
        "tour_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "tour_times": ["10:00 AM", "2:00 PM", "4:00 PM"],
        "contact_person": "Jennifer Adams"
    },
    "brookdale_tampa": {
        "name": "Brookdale Tampa",
        "address": "456 Senior Way, Tampa, FL",
        "phone": "(813) 555-0102",
        "tour_days": ["Tuesday", "Wednesday", "Thursday", "Saturday"],
        "tour_times": ["11:00 AM", "1:00 PM", "3:00 PM"],
        "contact_person": "Michael Torres"
    },
    "atria_tampa": {
        "name": "Atria Senior Living Tampa",
        "address": "789 Golden Years Blvd, Tampa, FL",
        "phone": "(813) 555-0103",
        "tour_days": ["Monday", "Wednesday", "Friday", "Saturday"],
        "tour_times": ["9:00 AM", "11:00 AM", "2:00 PM"],
        "contact_person": "Sarah Mitchell"
    }
}


def get_available_slots(facility_id: str, week_start: datetime = None) -> list:
    """Get available tour slots for a facility"""
    
    if week_start is None:
        week_start = datetime.now()
    
    facility = ALF_FACILITIES.get(facility_id)
    if not facility:
        return []
    
    slots = []
    for i in range(7):
        date = week_start + timedelta(days=i)
        day_name = date.strftime("%A")
        
        if day_name in facility["tour_days"]:
            for time in facility["tour_times"]:
                slots.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "day": day_name,
                    "time": time,
                    "facility": facility["name"],
                    "facility_id": facility_id
                })
    
    return slots


def book_tour(family: dict, facility_id: str, slot: dict) -> dict:
    """Book a tour for a family"""
    
    facility = ALF_FACILITIES.get(facility_id)
    if not facility:
        return {"error": "Facility not found"}
    
    booking = {
        "booking_id": f"TOUR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "family": family,
        "facility": facility,
        "slot": slot,
        "status": "confirmed",
        "booked_at": datetime.now().isoformat()
    }
    
    # Send confirmation SMS
    if family.get('phone'):
        message = f"✅ Tour Confirmed!\n\n{facility['name']}\n{slot['day']}, {slot['date']} at {slot['time']}\n\nAddress: {facility['address']}\n\nAsk for {facility['contact_person']}"
        
        try:
            requests.post(GHL_SMS_WEBHOOK, json={"phone": family['phone'], "message": message})
            booking["sms_sent"] = True
        except:
            booking["sms_sent"] = False
    
    # Save booking
    save_booking(booking)
    
    return booking


def save_booking(booking: dict):
    """Save booking to file"""
    os.makedirs("tour_bookings", exist_ok=True)
    
    filename = f"tour_bookings/{booking['booking_id']}.json"
    with open(filename, "w") as f:
        json.dump(booking, f, indent=2)
    
    print(f"[BOOKING] Saved: {filename}")


def suggest_tours(family: dict, preferences: dict = None) -> list:
    """Suggest tour options based on family preferences"""
    
    suggestions = []
    
    for fac_id, facility in ALF_FACILITIES.items():
        slots = get_available_slots(fac_id)
        if slots:
            suggestions.append({
                "facility": facility["name"],
                "facility_id": fac_id,
                "address": facility["address"],
                "next_available": slots[0],
                "all_slots": slots[:6]  # Next 6 slots
            })
    
    return suggestions


def format_tour_options_for_sarah(suggestions: list) -> str:
    """Format tour options for Sarah to read to caller"""
    
    if not suggestions:
        return "I apologize, but I don't have any tours available right now. Let me get your info and have someone call you back."
    
    script = "I have some tour options for you:\n\n"
    
    for i, sug in enumerate(suggestions[:3], 1):
        script += f"Option {i}: {sug['facility']}\n"
        script += f"  Next available: {sug['next_available']['day']} at {sug['next_available']['time']}\n"
        script += f"  Located at: {sug['address']}\n\n"
    
    script += "Which one would you like to schedule, or would you prefer a different day?"
    
    return script


if __name__ == "__main__":
    # Test family
    test_family = {
        "name": "Johnson Family",
        "contact": "Mary Johnson",
        "phone": "+13529368152",
        "senior_name": "Robert Johnson",
        "care_level": "assisted_living"
    }
    
    # Get suggestions
    suggestions = suggest_tours(test_family)
    print("Tour Suggestions:")
    print(json.dumps(suggestions, indent=2))
    
    # Print Sarah script
    print("\nSarah's Script:")
    print(format_tour_options_for_sarah(suggestions))
    
    # Book a tour
    if suggestions:
        booking = book_tour(test_family, suggestions[0]["facility_id"], suggestions[0]["next_available"])
        print(f"\nBooking: {booking['booking_id']}")
