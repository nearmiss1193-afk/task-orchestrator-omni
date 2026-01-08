"""
INVOICE GENERATOR
=================
Auto-create invoices from Sarah call transcripts.
"""
import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

GROK_API_KEY = os.getenv('GROK_API_KEY')

INVOICE_TEMPLATE = """
================================================================================
                                INVOICE
================================================================================

Invoice #: {invoice_number}
Date: {date}
Due: {due_date}

BILL TO:
{customer_name}
{customer_phone}
{customer_email}

--------------------------------------------------------------------------------
DESCRIPTION                                                           AMOUNT
--------------------------------------------------------------------------------
{line_items}
--------------------------------------------------------------------------------
                                                      SUBTOTAL:     ${subtotal:.2f}
                                                      TAX (7%):     ${tax:.2f}
                                                      TOTAL:        ${total:.2f}
================================================================================

Payment Terms: Due within 30 days
Pay by: Check, Credit Card, or Cash

Thank you for your business!
AI Service Co | (863) 213-2505 | aiserviceco.com
"""


def extract_invoice_data(transcript: str, customer: dict) -> dict:
    """Extract invoice details from call transcript using Grok"""
    
    prompt = f"""Extract invoice details from this service call transcript:

Transcript:
{transcript}

Customer Info:
{json.dumps(customer)}

Return JSON with:
{{
    "service_description": "Service performed",
    "parts_used": [{{"name": "part", "cost": 0}}],
    "labor_hours": 0,
    "labor_rate": 85,
    "notes": "any special notes"
}}"""

    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "grok-3-mini",
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return json.loads(response.json()['choices'][0]['message']['content'])
    except Exception as e:
        print(f"[ERROR] Extraction failed: {e}")
    
    return {"service_description": "Service call", "labor_hours": 1, "labor_rate": 85, "parts_used": []}


def generate_invoice(call_data: dict) -> dict:
    """Generate invoice from call data"""
    
    invoice_data = extract_invoice_data(
        call_data.get('transcript', ''),
        call_data.get('customer', {})
    )
    
    # Calculate totals
    parts_total = sum(p.get('cost', 0) for p in invoice_data.get('parts_used', []))
    labor_total = invoice_data.get('labor_hours', 1) * invoice_data.get('labor_rate', 85)
    subtotal = parts_total + labor_total
    tax = subtotal * 0.07
    total = subtotal + tax
    
    # Generate line items
    line_items = []
    for part in invoice_data.get('parts_used', []):
        line_items.append(f"{part['name']:<60} ${part['cost']:>10.2f}")
    line_items.append(f"{'Labor (' + str(invoice_data.get('labor_hours', 1)) + ' hrs @ $' + str(invoice_data.get('labor_rate', 85)) + '/hr)':<60} ${labor_total:>10.2f}")
    
    customer = call_data.get('customer', {})
    invoice = {
        "invoice_number": f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "date": datetime.now().strftime('%Y-%m-%d'),
        "due_date": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        "customer": customer,
        "line_items": invoice_data,
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "formatted": INVOICE_TEMPLATE.format(
            invoice_number=f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            date=datetime.now().strftime('%Y-%m-%d'),
            due_date=(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            customer_name=customer.get('name', 'Customer'),
            customer_phone=customer.get('phone', ''),
            customer_email=customer.get('email', ''),
            line_items='\n'.join(line_items),
            subtotal=subtotal,
            tax=tax,
            total=total
        )
    }
    
    return invoice


def save_invoice(invoice: dict, filename: str = None):
    """Save invoice to file"""
    if not filename:
        filename = f"invoices/{invoice['invoice_number']}.json"
    
    os.makedirs("invoices", exist_ok=True)
    
    with open(filename, "w") as f:
        json.dump(invoice, f, indent=2)
    
    # Also save text version
    with open(filename.replace('.json', '.txt'), "w") as f:
        f.write(invoice['formatted'])
    
    print(f"[INVOICE] Saved: {filename}")
    return filename


if __name__ == "__main__":
    test_call = {
        "transcript": "Replaced capacitor on outdoor unit, cleaned condenser coils. Took about 2 hours.",
        "customer": {
            "name": "John Smith",
            "phone": "(555) 123-4567",
            "email": "john@example.com"
        }
    }
    
    invoice = generate_invoice(test_call)
    print(invoice['formatted'])
    save_invoice(invoice)
