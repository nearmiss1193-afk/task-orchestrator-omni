---
description: How to send SMS via GHL webhook workflow
---

# GHL SMS Workflow Setup

## Webhook URL

```text
https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd
```

## CRITICAL: Workflow Order

**Create Contact MUST come BEFORE SMS action!**

Correct order:

1. Inbound Webhook (Trigger)
2. Create/Update Contact (maps phone from webhook)
3. Send SMS (now has contact context)

## Sending SMS from Python

```python
import requests

requests.post(
    'https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd',
    json={'phone': '+1XXXXXXXXXX', 'message': 'Your message here'}
)
```

## Common Issues

| Issue             | Cause                  | Fix                        |
| ----------------- | ---------------------- | -------------------------- |
| SMS skipped       | Contact not created    | Reorder workflow           |
| 401 Unauthorized  | API token expired      | Use webhooks instead       |
| No message sent   | Wrong webhook URL      | Verify workflow published  |

## Lesson Learned (Jan 7, 2026)

GHL workflows execute actions in parallel if not properly ordered. Always ensure contact exists before any messaging action.
