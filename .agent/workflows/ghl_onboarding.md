---
description: GHL onboarding workflow for new client after Stripe checkout
---

# GHL Client Onboarding Workflow

## Trigger

New client completes Stripe checkout for AI Service Co

## Steps

### 1. Create GHL Sub-Account

```python
# Use GHL API to create sub-account
POST https://services.leadconnectorhq.com/locations/
{
    "name": "{{client_business_name}}",
    "email": "{{client_email}}",
    "phone": "{{client_phone}}"
}
```

### 2. Send Welcome Email

```python
python ghl_sms_sender.py "{{client_phone}}" "Welcome to AI Service Co! Sarah will call you shortly to complete setup."
```

### 3. Trigger Sarah Welcome Call

```python
python call_sara_prospect.py --phone "{{client_phone}}" --type "onboarding"
```

### 4. Create GHL Workflow for Client

- Inbound call handling
- SMS autoresponder
- Lead capture

### 5. Configure Phone Number

- Purchase or port number
- Connect to Vapi
- Assign to sub-account

## Webhook Endpoints

### Stripe Webhook

```text
POST /api/stripe-webhook
Handles: checkout.session.completed
```

### GHL Webhook  

```text
https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/...
```

## Verification

- [ ] Sub-account created
- [ ] Welcome SMS sent
- [ ] Sarah call made
- [ ] Client workflow active
