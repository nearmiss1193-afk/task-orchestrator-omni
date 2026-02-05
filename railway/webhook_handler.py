"""
Webhook Handler - Receives GHL events (email opens, clicks, replies)
Always-on Flask service
"""
import os
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

# Import shared clients
from supabase_client import get_client, update_lead_status

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "webhook_handler",
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route("/ghl/webhook", methods=["POST"])
def ghl_webhook():
    """
    Handle incoming GHL webhooks for engagement tracking
    Events: email_opened, email_clicked, email_replied, sms_replied
    """
    try:
        data = request.json or {}
        event_type = data.get("type", data.get("event", "unknown"))
        contact_id = data.get("contactId", data.get("contact_id"))
        
        print(f"📥 GHL Webhook: {event_type} for contact {contact_id}")
        
        if not contact_id:
            return jsonify({"error": "No contact ID"}), 400
        
        # Match GHL contact to our lead
        lead = find_lead_by_ghl_contact(contact_id)
        
        if not lead:
            print(f"   ⚠️ Lead not found for GHL contact {contact_id}")
            return jsonify({"status": "contact_not_found"}), 200
        
        # Process based on event type
        if event_type in ["email_opened", "EmailOpened", "opened"]:
            handle_email_open(lead)
        elif event_type in ["email_clicked", "EmailClicked", "clicked"]:
            handle_email_click(lead)
        elif event_type in ["email_replied", "EmailReplied", "replied", "reply"]:
            handle_reply(lead)
        elif event_type in ["sms_replied", "SMSReplied"]:
            handle_reply(lead)
        elif event_type in ["appointment_booked", "AppointmentBooked"]:
            handle_booking(lead)
        else:
            print(f"   ℹ️ Unhandled event type: {event_type}")
        
        return jsonify({"status": "processed"}), 200
        
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return jsonify({"error": str(e)}), 500


def find_lead_by_ghl_contact(ghl_contact_id: str) -> dict:
    """Find our lead by GHL contact ID (stored in outbound_touches)"""
    client = get_client()
    
    # Look in outbound_touches for the GHL contact ID
    result = client.table("outbound_touches") \
        .select("contact_id") \
        .eq("report_data->>ghl_contact_id", ghl_contact_id) \
        .limit(1) \
        .execute()
    
    if result.data:
        our_contact_id = result.data[0]["contact_id"]
        # Get the actual lead
        lead_result = client.table("contacts_master") \
            .select("*") \
            .eq("id", our_contact_id) \
            .limit(1) \
            .execute()
        if lead_result.data:
            return lead_result.data[0]
    
    return None


def calculate_engagement_score(lead: dict, action: str) -> int:
    """Calculate new engagement score based on action"""
    current = lead.get("engagement_score", 0) or 0
    
    if action == "open":
        return min(current + 10, 100)
    elif action == "click":
        return min(current + 20, 100)
    elif action == "reply":
        return min(current + 50, 100)
    elif action == "book":
        return 100  # Max engagement
    
    return current


def handle_email_open(lead: dict):
    """Handle email open event"""
    new_score = calculate_engagement_score(lead, "open")
    update_lead_status(lead["id"], lead.get("status", "outreached"), {
        "engagement_score": new_score,
        "last_engagement": datetime.utcnow().isoformat(),
        "last_engagement_type": "email_open"
    })
    print(f"   📧 Email opened - Score: {new_score}")
    
    # Log the touch update
    client = get_client()
    client.table("outbound_touches") \
        .update({"touch_status": "opened"}) \
        .eq("contact_id", lead["id"]) \
        .eq("touch_status", "sent") \
        .execute()


def handle_email_click(lead: dict):
    """Handle email click event"""
    new_score = calculate_engagement_score(lead, "click")
    update_lead_status(lead["id"], lead.get("status", "outreached"), {
        "engagement_score": new_score,
        "last_engagement": datetime.utcnow().isoformat(),
        "last_engagement_type": "email_click"
    })
    print(f"   🖱️ Email clicked - Score: {new_score}")
    
    # Log the touch update
    client = get_client()
    client.table("outbound_touches") \
        .update({"touch_status": "clicked"}) \
        .eq("contact_id", lead["id"]) \
        .execute()


def handle_reply(lead: dict):
    """Handle reply event - HOT LEAD!"""
    new_score = calculate_engagement_score(lead, "reply")
    update_lead_status(lead["id"], "replied", {
        "engagement_score": new_score,
        "last_engagement": datetime.utcnow().isoformat(),
        "last_engagement_type": "reply"
    })
    print(f"   🔥 REPLY received - Score: {new_score} - HOT LEAD!")
    
    # Log the touch update
    client = get_client()
    client.table("outbound_touches") \
        .update({"touch_status": "replied"}) \
        .eq("contact_id", lead["id"]) \
        .execute()
    
    # TODO: Trigger notification or Vapi call


def handle_booking(lead: dict):
    """Handle appointment booking - QUALIFIED!"""
    update_lead_status(lead["id"], "qualified", {
        "engagement_score": 100,
        "last_engagement": datetime.utcnow().isoformat(),
        "last_engagement_type": "booking"
    })
    print(f"   🎯 BOOKING made - Lead is QUALIFIED!")


@app.route("/test", methods=["GET", "POST"])
def test_endpoint():
    """Test endpoint for debugging"""
    return jsonify({
        "message": "Webhook handler is working",
        "method": request.method,
        "data": request.json if request.method == "POST" else None
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Webhook Handler starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
