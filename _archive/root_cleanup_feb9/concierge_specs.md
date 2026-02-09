# Support Concierge & Upsell Agent Specifications

**Role:** The "Concierge" inside the user's app.
**Goal:** Solve problems instantly + Upsell Enterprise features contextually.

## 1. Interaction Flow

1. **User:** "I need someone to answer my phones." or "How do I change my password?"
2. **Concierge:**
    * *Step 1 (Identify):* Who is this? (e.g., "John from HVAC Co", Plan: "Growth Partner").
    * *Step 2 (Classify):* Is this **Support** (fix it) or **Growth** (buy it)?
    * *Step 3 (Act):*
        * **Support:** Search KB -> "Here is how you change your password..."
        * **Growth:** "For phone answering, our Enterprise Office Manager is perfect. It handles calls and inventory."
    * *Step 4 (Quote):* "Since you're on Growth, I can add this for +$X/mo. Should I prepare a quote?"

## 2. Dynamic Pricing Logic (The "Quote Generator")

The agent needs a tool to calculate add-on prices based on "Scopes".

| Feature Scope | Base Price | Setup Fee | Recurring |
| :--- | :--- | :--- | :--- |
| **Office Manager (Voice)** | $997/mo | $2,500 | Yes |
| **Reputation Guard** | $297/mo | $500 | Yes |
| **Social Siege (Content)** | $497/mo | $1,000 | Yes |
| **Custom Integration** | Varies | $150/hr | No |

**Tool:** `calculate_quote(scopes=[])`

* Input: `['office_manager', 'social_siege']`
* Output: `Total Setup: $3,500, Monthly: $1,494`

## 3. The API (App Integration)

**Endpoint:** `POST /concierge_chat`
**Payload:**

```json
{
  "user_id": "ghl_contact_id",
  "message": "I want the office AI thing",
  "context": {"current_plan": "growth", "location_id": "..."}
}
```

**Response:**

```json
{
  "reply": "I've drafted a quote for the Enterprise Office Manager...",
  "action": "show_quote",
  "quote_details": {
    "items": [{"name": "Office Manager", "price": 997}],
    "total_monthly": 997,
    "checkout_link": "https://stripe/..."
  }
}
```

## 4. Implementation Steps

1. **Knowledge Base:** Minimal hardcoded FAQ for now ("How to login", "Reset password").
2. **Quote Tool:** Python function in `deploy.py` implementing the pricing table.
3. **Agent Logic:** System Prompt enabling "Sales Engineer" persona.
4. **Endpoint:** `concierge_chat` in `deploy.py`.
