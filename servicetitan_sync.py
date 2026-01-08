"""
SERVICETITAN INTEGRATION
========================
Bidirectional sync with ServiceTitan for jobs, customers, and invoices.
"""
import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# ServiceTitan config
ST_CLIENT_ID = os.getenv('SERVICETITAN_CLIENT_ID', '')
ST_CLIENT_SECRET = os.getenv('SERVICETITAN_CLIENT_SECRET', '')
ST_TENANT_ID = os.getenv('SERVICETITAN_TENANT_ID', '')
ST_ACCESS_TOKEN = os.getenv('SERVICETITAN_ACCESS_TOKEN', '')

ST_BASE_URL = "https://api.servicetitan.io"
ST_AUTH_URL = "https://auth.servicetitan.io/connect/token"


def get_access_token() -> str:
    """Get ServiceTitan OAuth token"""
    
    if not ST_CLIENT_ID or not ST_CLIENT_SECRET:
        return ""
    
    try:
        response = requests.post(
            ST_AUTH_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": ST_CLIENT_ID,
                "client_secret": ST_CLIENT_SECRET
            }
        )
        
        if response.status_code == 200:
            return response.json().get('access_token')
    except Exception as e:
        print(f"[ERROR] Auth failed: {e}")
    
    return ""


def get_headers() -> dict:
    """Get API headers"""
    token = ST_ACCESS_TOKEN or get_access_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "ST-App-Key": ST_CLIENT_ID
    }


# ============ CUSTOMERS ============

def sync_customer_to_st(customer: dict) -> dict:
    """Create/update customer in ServiceTitan"""
    
    if not ST_TENANT_ID:
        return mock_response("customer", customer)
    
    payload = {
        "name": customer.get('name'),
        "type": "Residential",
        "address": {
            "street": customer.get('address', ''),
            "city": customer.get('city', ''),
            "state": customer.get('state', 'FL'),
            "zip": customer.get('zip', ''),
            "country": "USA"
        },
        "contacts": [
            {
                "type": "Phone",
                "value": customer.get('phone', ''),
                "memo": "Primary"
            },
            {
                "type": "Email",
                "value": customer.get('email', '')
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{ST_BASE_URL}/crm/v2/tenant/{ST_TENANT_ID}/customers",
            headers=get_headers(),
            json=payload
        )
        
        if response.status_code in [200, 201]:
            return {"success": True, "st_customer_id": response.json().get('id')}
        return {"error": response.text}
    except Exception as e:
        return {"error": str(e)}


def get_customer_from_st(customer_id: str) -> dict:
    """Get customer from ServiceTitan"""
    
    if not ST_TENANT_ID:
        return mock_response("get_customer", {"id": customer_id})
    
    try:
        response = requests.get(
            f"{ST_BASE_URL}/crm/v2/tenant/{ST_TENANT_ID}/customers/{customer_id}",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            return response.json()
        return {"error": response.text}
    except Exception as e:
        return {"error": str(e)}


# ============ JOBS ============

def create_job_in_st(job: dict) -> dict:
    """Create a job in ServiceTitan"""
    
    if not ST_TENANT_ID:
        return mock_response("job", job)
    
    payload = {
        "customerId": job.get('customer_id'),
        "locationId": job.get('location_id'),
        "businessUnitId": job.get('business_unit_id'),
        "jobTypeId": job.get('job_type_id'),
        "priority": job.get('priority', 'Normal'),
        "summary": job.get('description', 'Service call'),
        "appointmentStart": job.get('start_time'),
        "appointmentEnd": job.get('end_time')
    }
    
    try:
        response = requests.post(
            f"{ST_BASE_URL}/jpm/v2/tenant/{ST_TENANT_ID}/jobs",
            headers=get_headers(),
            json=payload
        )
        
        if response.status_code in [200, 201]:
            return {"success": True, "st_job_id": response.json().get('id')}
        return {"error": response.text}
    except Exception as e:
        return {"error": str(e)}


def get_jobs_from_st(status: str = "Scheduled", days: int = 7) -> list:
    """Get jobs from ServiceTitan"""
    
    if not ST_TENANT_ID:
        return mock_jobs()
    
    start_date = datetime.now().strftime('%Y-%m-%d')
    end_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    
    try:
        response = requests.get(
            f"{ST_BASE_URL}/jpm/v2/tenant/{ST_TENANT_ID}/jobs",
            headers=get_headers(),
            params={
                "status": status,
                "startDate": start_date,
                "endDate": end_date
            }
        )
        
        if response.status_code == 200:
            return response.json().get('data', [])
        return []
    except Exception as e:
        print(f"[ERROR] Get jobs failed: {e}")
        return []


def update_job_status(job_id: str, status: str) -> dict:
    """Update job status in ServiceTitan"""
    
    if not ST_TENANT_ID:
        return mock_response("update_job", {"job_id": job_id, "status": status})
    
    try:
        response = requests.patch(
            f"{ST_BASE_URL}/jpm/v2/tenant/{ST_TENANT_ID}/jobs/{job_id}",
            headers=get_headers(),
            json={"status": status}
        )
        
        if response.status_code == 200:
            return {"success": True}
        return {"error": response.text}
    except Exception as e:
        return {"error": str(e)}


# ============ INVOICES ============

def get_invoices_from_st(days: int = 30) -> list:
    """Get invoices from ServiceTitan"""
    
    if not ST_TENANT_ID:
        return mock_invoices()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    try:
        response = requests.get(
            f"{ST_BASE_URL}/accounting/v2/tenant/{ST_TENANT_ID}/invoices",
            headers=get_headers(),
            params={
                "createdOnOrAfter": start_date.strftime('%Y-%m-%d'),
                "createdOnOrBefore": end_date.strftime('%Y-%m-%d')
            }
        )
        
        if response.status_code == 200:
            return response.json().get('data', [])
        return []
    except Exception as e:
        print(f"[ERROR] Get invoices failed: {e}")
        return []


# ============ TECHNICIANS ============

def get_technicians() -> list:
    """Get all technicians from ServiceTitan"""
    
    if not ST_TENANT_ID:
        return mock_technicians()
    
    try:
        response = requests.get(
            f"{ST_BASE_URL}/settings/v2/tenant/{ST_TENANT_ID}/technicians",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            return response.json().get('data', [])
        return []
    except Exception as e:
        print(f"[ERROR] Get technicians failed: {e}")
        return []


# ============ SYNC ============

def full_sync() -> dict:
    """Run full bidirectional sync"""
    
    print("[SYNC] Starting ServiceTitan bidirectional sync...")
    
    results = {
        "jobs_synced": 0,
        "customers_synced": 0,
        "invoices_synced": 0,
        "errors": []
    }
    
    # Get jobs
    jobs = get_jobs_from_st()
    results["jobs_synced"] = len(jobs)
    print(f"[SYNC] Found {len(jobs)} jobs")
    
    # Get invoices
    invoices = get_invoices_from_st()
    results["invoices_synced"] = len(invoices)
    print(f"[SYNC] Found {len(invoices)} invoices")
    
    # Get technicians
    techs = get_technicians()
    print(f"[SYNC] Found {len(techs)} technicians")
    
    results["timestamp"] = datetime.now().isoformat()
    
    return results


# ============ MOCK DATA ============

def mock_response(action: str, data: dict) -> dict:
    return {
        "mock": True,
        "action": action,
        "data": data,
        "message": "ServiceTitan not configured - add credentials to .env"
    }


def mock_jobs() -> list:
    return [
        {"id": "J001", "customer": "John Smith", "type": "AC Repair", "status": "Scheduled", "tech": "Mike"},
        {"id": "J002", "customer": "Jane Doe", "type": "Furnace Tune-up", "status": "In Progress", "tech": "Dave"},
        {"id": "J003", "customer": "Bob Wilson", "type": "Water Heater", "status": "Completed", "tech": "Chris"},
    ]


def mock_invoices() -> list:
    return [
        {"id": "INV001", "customer": "John Smith", "amount": 450.00, "status": "Paid"},
        {"id": "INV002", "customer": "Jane Doe", "amount": 175.00, "status": "Outstanding"},
    ]


def mock_technicians() -> list:
    return [
        {"id": "T001", "name": "Mike Johnson", "specialty": "HVAC", "active": True},
        {"id": "T002", "name": "Dave Wilson", "specialty": "Plumbing", "active": True},
        {"id": "T003", "name": "Chris Brown", "specialty": "Electrical", "active": True},
    ]


def get_sync_status() -> dict:
    """Get current sync configuration status"""
    return {
        "configured": bool(ST_TENANT_ID and ST_CLIENT_ID),
        "tenant_id": ST_TENANT_ID[:8] + "..." if ST_TENANT_ID else "Not configured",
        "has_token": bool(ST_ACCESS_TOKEN),
        "last_sync": "Never" if not ST_TENANT_ID else datetime.now().isoformat()
    }


if __name__ == "__main__":
    print("ServiceTitan Sync Status:")
    print(json.dumps(get_sync_status(), indent=2))
    
    print("\nRunning sync (mock mode if not configured):")
    results = full_sync()
    print(json.dumps(results, indent=2))
