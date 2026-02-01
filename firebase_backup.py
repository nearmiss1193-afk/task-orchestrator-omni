"""
Firebase Backup Module
Provides redundant storage using Firebase Firestore.
Falls back to Firebase if Supabase is unavailable.
"""
import os
import json

# Firebase Admin SDK
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("[FIREBASE] firebase-admin not installed")

# Initialize Firebase
_firebase_app = None
_firestore_db = None

def init_firebase():
    """Initialize Firebase from service account JSON"""
    global _firebase_app, _firestore_db
    
    if not FIREBASE_AVAILABLE:
        return False
    
    if _firebase_app:
        return True  # Already initialized
    
    # Check for credentials file
    cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH", "firebase-service-account.json")
    cred_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")
    
    try:
        if cred_json:
            # Credentials from environment variable (Railway)
            cred_dict = json.loads(cred_json)
            cred = credentials.Certificate(cred_dict)
        elif os.path.exists(cred_path):
            # Credentials from file (local)
            cred = credentials.Certificate(cred_path)
        else:
            print(f"[FIREBASE] No credentials found at {cred_path}")
            return False
        
        _firebase_app = firebase_admin.initialize_app(cred)
        _firestore_db = firestore.client()
        print("[FIREBASE] Initialized successfully")
        return True
        
    except Exception as e:
        print(f"[FIREBASE] Init error: {e}")
        return False


def save_lead_to_firebase(lead_data: dict) -> bool:
    """Save lead to Firebase Firestore as backup"""
    if not init_firebase():
        return False
    
    try:
        # Use company_name as document ID for deduplication
        doc_id = lead_data.get("company_name", "").replace(" ", "_").lower()[:50]
        if not doc_id:
            doc_id = None  # Auto-generate
        
        _firestore_db.collection("leads").document(doc_id).set(lead_data, merge=True)
        print(f"[FIREBASE] Saved lead: {lead_data.get('company_name')}")
        return True
        
    except Exception as e:
        print(f"[FIREBASE] Save error: {e}")
        return False


def get_leads_from_firebase(status: str = None, limit: int = 100) -> list:
    """Get leads from Firebase (fallback when Supabase is down)"""
    if not init_firebase():
        return []
    
    try:
        query = _firestore_db.collection("leads")
        
        if status:
            query = query.where("status", "==", status)
        
        query = query.limit(limit)
        docs = query.stream()
        
        leads = []
        for doc in docs:
            lead = doc.to_dict()
            lead["id"] = doc.id
            leads.append(lead)
        
        print(f"[FIREBASE] Retrieved {len(leads)} leads")
        return leads
        
    except Exception as e:
        print(f"[FIREBASE] Query error: {e}")
        return []


def update_lead_in_firebase(lead_id: str, updates: dict) -> bool:
    """Update lead in Firebase"""
    if not init_firebase():
        return False
    
    try:
        _firestore_db.collection("leads").document(lead_id).update(updates)
        return True
    except Exception as e:
        print(f"[FIREBASE] Update error: {e}")
        return False


def sync_supabase_to_firebase(leads: list) -> int:
    """Bulk sync leads from Supabase to Firebase"""
    if not init_firebase():
        return 0
    
    synced = 0
    batch = _firestore_db.batch()
    
    for lead in leads:
        doc_id = lead.get("company_name", "").replace(" ", "_").lower()[:50]
        if doc_id:
            doc_ref = _firestore_db.collection("leads").document(doc_id)
            batch.set(doc_ref, lead, merge=True)
            synced += 1
    
    try:
        batch.commit()
        print(f"[FIREBASE] Synced {synced} leads")
        return synced
    except Exception as e:
        print(f"[FIREBASE] Sync error: {e}")
        return 0


# Health check
def firebase_health() -> dict:
    """Check Firebase connection health"""
    if not init_firebase():
        return {"status": "unavailable", "reason": "not_initialized"}
    
    try:
        # Try to read one document
        _firestore_db.collection("leads").limit(1).get()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "error", "reason": str(e)}


if __name__ == "__main__":
    # Test
    print(firebase_health())
