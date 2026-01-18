# Variant Attribution - Verification Commands

## Pre-requisites

### 1. Run SQL Migration in Supabase

Open Supabase SQL Editor and run:

```sql
-- See full migration in: sql/attribution_migration.sql

CREATE TABLE IF NOT EXISTS outbound_touches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ts TIMESTAMPTZ DEFAULT NOW(),
    phone TEXT NOT NULL,
    channel TEXT NOT NULL,
    variant_id TEXT,
    variant_name TEXT,
    run_id TEXT,
    vertical TEXT DEFAULT 'hvac',
    company TEXT,
    status TEXT DEFAULT 'sent',
    correlation_id TEXT,
    payload JSONB
);

CREATE TABLE IF NOT EXISTS outreach_attribution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    appointment_id TEXT NOT NULL,
    phone TEXT,
    attributed_variant_id TEXT,
    attributed_variant_name TEXT,
    attributed_run_id TEXT,
    attributed_touch_id UUID,
    attributed_touch_ts TIMESTAMPTZ,
    attributed_channel TEXT,
    attribution_confidence FLOAT DEFAULT 0.0,
    payload JSONB
);
```

---

## Verification Steps

### Step 1: Record a test touch with variant_id

```powershell
Invoke-RestMethod -Uri "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/test/record-touch" `
  -Method Post -ContentType "application/json" `
  -Body '{"phone":"+13529368152","channel":"sms","variant_id":"variant_a","variant_name":"Direct CTA","run_id":"jan18_test"}'
```

**Expected Output:**

```json
{"success": true, "correlation_id": "test_touch_xxx", "phone_normalized": "+13529368152"}
```

### Step 2: Simulate appointment booking for same phone

```powershell
Invoke-RestMethod -Uri "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/webhook/ghl/appointment" `
  -Method Post -ContentType "application/json" `
  -Body '{"type":"AppointmentCreated","appointmentId":"test_appt_002","contact":{"phone":"+13529368152","name":"Test User"}}'
```

**Expected Output:**

```json
{
  "status": "ok",
  "event_type": "appointment.created",
  "attribution": {
    "attributed": true,
    "confidence": 1.0,
    "variant_id": "variant_a",
    "variant_name": "Direct CTA"
  }
}
```

### Step 3: Verify in Supabase

#### Check outbound_touches

```sql
SELECT id, ts, phone, channel, variant_id, variant_name, run_id
FROM outbound_touches
ORDER BY ts DESC
LIMIT 5;
```

#### Check outreach_attribution

```sql
SELECT appointment_id, phone, attributed_variant_id, attributed_variant_name, attribution_confidence
FROM outreach_attribution
ORDER BY created_at DESC
LIMIT 5;
```

#### Check sms.sent has variant_id

```sql
SELECT type, ts, payload->>'variant_id' as variant_id, payload->>'variant_name' as variant_name
FROM event_log_v2
WHERE type = 'sms.sent' AND payload->>'variant_id' IS NOT NULL
ORDER BY ts DESC
LIMIT 10;
```

#### Check appointment.attributed events

```sql
SELECT type, ts, payload
FROM event_log_v2
WHERE type = 'appointment.attributed'
ORDER BY ts DESC
LIMIT 5;
```

---

## What Each Table Stores

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `outbound_touches` | Every SMS/email sent with variant | phone, channel, variant_id, run_id |
| `outreach_attribution` | Links appointments → touches | appointment_id, variant_id, confidence |
| `event_log_v2` | All events (sms.sent, appointment.attributed) | type, payload |

---

## Confidence Scoring

| Time Since Touch | Confidence |
|------------------|------------|
| ≤ 24 hours | 1.0 |
| ≤ 72 hours | 0.7 |
| ≤ 7 days | 0.4 |
| > 7 days | 0.0 (no attribution) |

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `success: false` on record-touch | Table doesn't exist | Run SQL migration |
| Attribution shows 0.0 confidence | No touch for that phone | Check phone normalization |
| appointment.attributed not logged | Phone not in touches | Record touch first |
