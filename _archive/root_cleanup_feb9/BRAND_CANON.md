# BRAND_CANON.md - Single Source of Truth

> ⚠️ **LOCKED CONSTANTS** - These values must NEVER be changed without explicit approval.

## Phone Numbers

| Label | E164 | Display | Provider |
|-------|------|---------|----------|
| **VOICE** | +18632132505 | (863) 213-2505 | Vapi |
| **TEXT** | +13527585336 | (352) 758-5336 | GHL |

## Canonical Values

```
canonical_voice_e164 = "+18632132505"
canonical_voice_display = "(863) 213-2505"
canonical_sms_e164 = "+13527585336"  
canonical_sms_display = "(352) 758-5336"
```

## Business Info

| Field | Value |
|-------|-------|
| Business Name | AI Service Co |
| Website | <https://www.aiserviceco.com> |
| Booking Link | <https://link.aiserviceco.com/discovery> |
| Owner Email | <nearmiss1193@gmail.com> |
| Hours | Mon-Fri 8am-6pm EST |

## Pricing (Locked)

| Tier | Price |
|------|-------|
| Starter | $297/mo |
| Growth | $497/mo |
| Dominance | $997/mo |
| Enterprise | Custom |

## Escalation

- Emergency: +1 (352) 936-8152
- Email: <owner@aiserviceco.com>

## Forbidden Patterns

These numbers should NEVER appear on public pages:

- `863-337-3705` (old number)
- `352-758-5336` labelled as "Call" (wrong - this is TEXT only)
- `863-213-2505` labelled as "Text" (wrong - this is VOICE only)
- Any `XXX-XXX-XXXX` placeholder
- Any 10-digit number not matching canonical voice/sms

## Label Rules

- "(863) 213-2505" must ALWAYS have label: Call, Voice, Phone
- "(352) 758-5336" must ALWAYS have label: Text, SMS, Message
