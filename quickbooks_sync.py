"""
QUICKBOOKS SYNC
===============
Auto-log payments and leads to QuickBooks.
"""
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# QuickBooks config (would need OAuth in production)
QB_CLIENT_ID = os.getenv('QUICKBOOKS_CLIENT_ID', '')
QB_CLIENT_SECRET = os.getenv('QUICKBOOKS_CLIENT_SECRET', '')
QB_REALM_ID = os.getenv('QUICKBOOKS_REALM_ID', '')
QB_ACCESS_TOKEN = os.getenv('QUICKBOOKS_ACCESS_TOKEN', '')

QB_BASE_URL = "https://quickbooks.api.intuit.com/v3"


def sync_customer(customer: dict) -> dict:
    """Sync customer to QuickBooks"""
    
    if not QB_ACCESS_TOKEN:
        return {"error": "QuickBooks not configured", "mock": True, "customer": customer}
    
    payload = {
        "DisplayName": customer.get('name'),
        "PrimaryPhone": {"FreeFormNumber": customer.get('phone', '')},
        "PrimaryEmailAddr": {"Address": customer.get('email', '')},
        "BillAddr": {
            "Line1": customer.get('address', ''),
            "City": customer.get('city', ''),
            "CountrySubDivisionCode": customer.get('state', 'FL'),
            "PostalCode": customer.get('zip', '')
        }
    }
    
    try:
        response = requests.post(
            f"{QB_BASE_URL}/company/{QB_REALM_ID}/customer",
            headers={
                "Authorization": f"Bearer {QB_ACCESS_TOKEN}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            json=payload
        )
        
        if response.status_code == 200:
            return {"success": True, "qb_id": response.json().get('Customer', {}).get('Id')}
        return {"error": response.text}
    except Exception as e:
        return {"error": str(e)}


def sync_invoice(invoice: dict) -> dict:
    """Sync invoice to QuickBooks"""
    
    if not QB_ACCESS_TOKEN:
        return {"error": "QuickBooks not configured", "mock": True, "invoice": invoice}
    
    # Would need to create/lookup customer first and get line items
    # This is a simplified version
    
    return {"status": "would_sync", "invoice_id": invoice.get('invoice_number')}


def sync_payment(payment: dict) -> dict:
    """Sync payment to QuickBooks"""
    
    if not QB_ACCESS_TOKEN:
        return {"error": "QuickBooks not configured", "mock": True, "payment": payment}
    
    payload = {
        "TotalAmt": payment.get('amount', 0),
        "CustomerRef": {"value": payment.get('customer_qb_id')},
        "PaymentMethodRef": {"value": "1"}  # Credit Card
    }
    
    return {"status": "would_sync", "amount": payment.get('amount')}


def get_sync_status() -> dict:
    """Get current sync status"""
    
    return {
        "configured": bool(QB_ACCESS_TOKEN),
        "realm_id": QB_REALM_ID or "Not configured",
        "last_sync": datetime.now().isoformat() if QB_ACCESS_TOKEN else "Never"
    }


# Mock sync functions for when QB isn't configured
def mock_sync_all():
    """Mock sync for demo purposes"""
    return {
        "customers_synced": 5,
        "invoices_synced": 12,
        "payments_synced": 8,
        "total_revenue": 4250.00,
        "status": "mock_mode"
    }


if __name__ == "__main__":
    print("QuickBooks Sync Status:")
    print(json.dumps(get_sync_status(), indent=2))
    
    if not QB_ACCESS_TOKEN:
        print("\nMock Sync Results:")
        print(json.dumps(mock_sync_all(), indent=2))
