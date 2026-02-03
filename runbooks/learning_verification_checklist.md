# Learning Verification Checklist - Jan 18, 2026

## Current State (from event_log_v2)

### ✅ PASSING

| Check | Status | Details |
|-------|--------|---------|
| event_log_v2 Active | ✅ PASS | 50+ events logged |
| kpi.snapshot events | ✅ PASS | 6 in last period |
| sms.sent events | ✅ PASS | 7 SMS events logged |
| Email events | ✅ PASS | 3 email.sent, 4 batch events |
| Truth Strip polling | ✅ PASS | dashboard.truth_checked: 2 |

### ❌ FAILING / MISSING

| Check | Status | What to Fix |
|-------|--------|-------------|
| appointment.created | ❌ MISSING | Need GHL webhook |
| appointment.updated | ❌ MISSING | Need GHL webhook |
| variant_id tracking | ❌ MISSING | Not in payload |
| variant_name tracking | ❌ MISSING | Not in payload |
| ab_variant tracking | ❌ MISSING | Not in payload |

---

## FIX 1: GHL Appointment Webhook

### Step-by-Step Setup in GHL

1. **Go to GHL → Automation → Workflows**
2. **Create new workflow** "Appointment → Modal"
3. **Trigger**: "Appointment Status Changed" (covers created/updated/cancelled)
4. **Action**: Webhook (Custom)
5. **Webhook URL**:

   ```
   https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/webhook/ghl/appointment
   ```

6. **Method**: POST
7. **Headers**:

   ```
   Content-Type: application/json
   X-GHL-Source: appointment-workflow
   ```

8. **Body**: Send all appointment fields (or use Custom Fields mapping)

### Expected Payload Fields from GHL

```json
{
  "type": "AppointmentCreated",
  "locationId": "RnK4OjX0oDcqtWw0VyLr",
  "appointmentId": "abc123",
  "contactId": "contact456",
  "calendarId": "cal789",
  "startTime": "2026-01-18T14:00:00Z",
  "endTime": "2026-01-18T14:30:00Z",
  "status": "confirmed",
  "title": "Strategy Call",
  "contact": {
    "id": "contact456",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+13521234567"
  }
}
```

---

## FIX 2: Add Webhook Endpoint to Modal

Add this to `modal_orchestrator_v3.py`:

```python
@api.post("/webhook/ghl/appointment")
async def ghl_appointment_webhook(request: Request):
    """Handle GHL appointment webhooks"""
    import uuid
    body = await request.json()
    
    event_type = body.get("type", "appointment.unknown")
    # Map GHL types to our types
    type_map = {
        "AppointmentCreated": "appointment.created",
        "AppointmentUpdated": "appointment.updated",
        "AppointmentDeleted": "appointment.cancelled",
        "AppointmentStatusChanged": "appointment.status_changed"
    }
    
    mapped_type = type_map.get(event_type, f"appointment.{event_type.lower()}")
    
    log_event(
        mapped_type,
        "ghl",
        "info",
        correlation_id=f"appt_{uuid.uuid4().hex[:8]}",
        entity_id=body.get("contactId") or body.get("contact", {}).get("id"),
        payload={
            "appointment_id": body.get("appointmentId"),
            "contact_id": body.get("contactId"),
            "start_time": body.get("startTime"),
            "status": body.get("status"),
            "title": body.get("title"),
            "contact_name": body.get("contact", {}).get("name"),
            "contact_phone": body.get("contact", {}).get("phone"),
            "raw": body
        }
    )
    
    return {"status": "ok", "event_type": mapped_type}
```

---

## FIX 3: Add Variant Tracking to SMS/Email

Update `send_sms_campaign.py` to include variant:

```python
# When sending SMS, include variant in GHL payload
payload = {
    "phone": contact_phone,
    "message": message,
    "variant_id": "control_v1",  # or "variant_b"
    "variant_name": "Direct CTA",
    "campaign_id": campaign_id
}
```

Update `log_event` calls to include variant:

```python
log_event("sms.sent", "modal", "info", correlation_id, contact_phone, {
    "variant_id": "control_v1",
    "variant_name": "Direct CTA",
    "campaign_id": "jan18_hvac"
})
```

---

## Test Curl Commands

### Test 1: Simulate Appointment Created

```bash
curl -X POST "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/webhook/ghl/appointment" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "AppointmentCreated",
    "appointmentId": "test_appt_001",
    "contactId": "test_contact_001",
    "startTime": "2026-01-18T14:00:00Z",
    "status": "confirmed",
    "title": "Strategy Call",
    "contact": {
      "name": "Test User",
      "phone": "+13529368152"
    }
  }'
```

### Test 2: Verify Event Logged

```bash
curl "https://rzcpfwkygdvoshtwxncs.supabase.co/rest/v1/event_log_v2?type=eq.appointment.created&order=ts.desc&limit=1" \
  -H "apikey: YOUR_SUPABASE_KEY" \
  -H "Authorization: Bearer YOUR_SUPABASE_KEY"
```

---

## Priority Fix Order

1. **IMMEDIATE**: Add `/webhook/ghl/appointment` endpoint to Modal v3
2. **TODAY**: Set up GHL workflow to send appointments to webhook
3. **TODAY**: Add variant_id to all SMS sends
4. **TOMORROW**: Add variant_id to email sends
5. **VERIFY**: Run curl test to confirm end-to-end

---

## SQL to Verify After Fixes

```sql
-- Check appointment events
SELECT type, ts, payload->>'appointment_id', payload->>'contact_name'
FROM event_log_v2 
WHERE type LIKE 'appointment.%'
ORDER BY ts DESC
LIMIT 10;

-- Check variant tracking
SELECT type, ts, payload->>'variant_id', payload->>'variant_name'
FROM event_log_v2 
WHERE payload->>'variant_id' IS NOT NULL
ORDER BY ts DESC
LIMIT 20;
```
