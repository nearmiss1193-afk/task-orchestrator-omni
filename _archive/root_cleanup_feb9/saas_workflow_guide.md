# SaaS Onboarding & Payment Integration Guide

This guide details how to link the **Deployed Landing Page** payment form to your **Automated SaaS Onboarding** in GoHighLevel.

## 1. The Trigger Point

Your Landing Page now has an embedded **Payment Form** (ID: `qaJ7szEbp2TwJkAT6WxG`).

* **Location:** Funnel Step 3 ("Secure Payment")
* **Action:** Customer enters card details & submits.

## 2. GHL Workflow Setup (Required)

You must ensure the following Workflow exists in GoHighLevel to handle the "Form Submitted" event.

### **Workflow Name:** "SaaS Auto-Onboarding"

**Trigger:**

* **Type:** Form Submitted
* **Filter:** Form is `AI Service Co Payment` (`qaJ7szEbp2TwJkAT6WxG`)

**Actions:**

1. **Add Tag:** `new-saas-customer`
1. **Add Tag:** `new-saas-customer`
1. **Stripe/Payment Action:** (If not handled natively by form product) -> Grant Access to Offer.
1. **Create User (SaaS):**
    * *Note:* If using GHL SaaS Mode, this happens via the "Offer" grant.
    * If using Membership/Custom: **Grant Offer: "AI Service Platform"**.
1. **Send Email (Welcome):**
    * **Subject:** Welcome to AI Service Co - Access Your Account
    * **Body:**

        ```text
        Hi {{contact.first_name}},
        
        Welcome to your new AI Service Engine!
        
        Click here to create your password and login:
        {{membership.signup_url}} (or your custom app URL)
        
        Your Growth Partner credentials are tied to: {{contact.email}}
        ```

1. **Add to Pipeline:** "SaaS Onboarding" -> Stage: "Account Created"

## 3. How they "Set Password"

* **Standard GHL SaaS:** The "Grant Offer" action automatically sends a standard welcome email with a magic link to set a password.
* **Custom:** Use the `{{membership.magic_link}}` custom value in your "Welcome" email action.

## 4. How they "Send Email"

Once they login to their sub-account:

* SMTP/Mailgun must be configured for the sub-account.
* The "SaaS Config" in your Agency View determines if they can send email immediately or need verification.

## 5. Verification

* **Shopper Status:** ✅ The system currently successfully submits the lead to the Payment Form.
* **Next Step:** Check your GHL "Conversations" or "Contacts" tab. You should see "Shopper[Random]" with the tag and form submission.
