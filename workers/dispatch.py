"""
JOB DISPATCH SYSTEM v1.0
========================
Routes service jobs to field techs via SMS coordination.

Flow:
1. Job created (from Sarah call or API)
2. System matches tech by service type + availability
3. SMS sent to tech: "New job at [address]. Reply ACCEPT or PASS"
4. ACCEPT → customer confirmation SMS + job status updated
5. PASS → auto-routes to next available tech

Tables needed:
- dispatch_jobs: job tickets with status tracking
- tech_roster: available technicians with skills and phone numbers
"""
import os
import json
import requests
from datetime import datetime, timezone


# ============================================================
#  JOB STATUS CONSTANTS
# ============================================================
STATUS_NEW = "new"
STATUS_DISPATCHED = "dispatched"
STATUS_ACCEPTED = "accepted"
STATUS_EN_ROUTE = "en_route"
STATUS_COMPLETED = "completed"
STATUS_CANCELLED = "cancelled"
STATUS_REASSIGNING = "reassigning"

URGENCY_LEVELS = {
    "emergency": "🚨 EMERGENCY",
    "urgent": "⚡ URGENT",
    "standard": "📋 Standard",
    "scheduled": "📅 Scheduled",
}


# ============================================================
#  TABLE SETUP (Run once to create tables)
# ============================================================

def ensure_tables(supabase):
    """
    Create dispatch tables if they don't exist.
    Run this once via: python -c "from workers.dispatch import setup; setup()"
    
    Tables are created via Supabase SQL editor:
    
    CREATE TABLE IF NOT EXISTS dispatch_jobs (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        service_type TEXT NOT NULL,
        address TEXT NOT NULL,
        customer_name TEXT,
        customer_phone TEXT,
        company_name TEXT,
        urgency TEXT DEFAULT 'standard',
        notes TEXT,
        assigned_tech_id TEXT,
        assigned_tech_name TEXT,
        assigned_tech_phone TEXT,
        status TEXT DEFAULT 'new',
        dispatch_attempts INT DEFAULT 0,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        accepted_at TIMESTAMPTZ,
        completed_at TIMESTAMPTZ,
        metadata JSONB DEFAULT '{}'
    );
    
    CREATE TABLE IF NOT EXISTS tech_roster (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT NOT NULL UNIQUE,
        services TEXT[] DEFAULT '{}',
        region TEXT DEFAULT 'florida',
        available BOOLEAN DEFAULT true,
        current_job_id UUID,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    print("Tables must be created via Supabase SQL editor. See docstring above.")


# ============================================================
#  CREATE JOB TICKET
# ============================================================

def create_job(service_type: str, address: str, customer_name: str,
               customer_phone: str, company_name: str, supabase,
               urgency: str = "standard", notes: str = "") -> dict:
    """
    Create a new job ticket and attempt to dispatch.
    
    Args:
        service_type: Type of service needed (e.g., "AC repair", "plumbing", "electrical")
        address: Service address
        customer_name: Customer requesting service
        customer_phone: Customer's phone for confirmation
        company_name: The business handling the job
        supabase: Supabase client
        urgency: emergency/urgent/standard/scheduled
        notes: Additional notes from the call
    
    Returns:
        dict with job_id and dispatch status
    """
    now = datetime.now(timezone.utc).isoformat()
    
    # Insert job ticket
    job_data = {
        "service_type": service_type,
        "address": address,
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "company_name": company_name,
        "urgency": urgency,
        "notes": notes,
        "status": STATUS_NEW,
        "dispatch_attempts": 0,
        "metadata": json.dumps({
            "created_by": "system",
            "created_at": now,
        }),
    }
    
    try:
        result = supabase.table("dispatch_jobs").insert(job_data).execute()
        job_id = result.data[0]["id"] if result.data else None
        
        if not job_id:
            return {"status": "failed", "error": "no_job_id"}
        
        print(f"  📋 Job created: {job_id[:8]} | {service_type} at {address}")
        
        # Auto-dispatch to first available tech
        dispatch_result = dispatch_to_tech(job_id, service_type, supabase)
        
        return {
            "status": "created",
            "job_id": job_id,
            "dispatch": dispatch_result,
        }
        
    except Exception as e:
        print(f"  ❌ Job creation error: {e}")
        return {"status": "failed", "error": str(e)}


# ============================================================
#  DISPATCH TO TECH
# ============================================================

def dispatch_to_tech(job_id: str, service_type: str, supabase,
                     exclude_techs: list = None) -> dict:
    """
    Find an available tech and send them the job via SMS.
    
    Args:
        job_id: The job to dispatch
        service_type: Service type to match against tech skills
        supabase: Supabase client
        exclude_techs: List of tech IDs that already passed on this job
    
    Returns:
        dict with dispatch result
    """
    exclude_techs = exclude_techs or []
    
    # Find available techs
    query = supabase.table("tech_roster").select("*").eq("available", True)
    result = query.execute()
    
    available_techs = []
    for tech in (result.data or []):
        if tech["id"] in exclude_techs:
            continue
        # Match by service type (if services list is populated)
        services = tech.get("services", []) or []
        if not services or service_type.lower() in [s.lower() for s in services]:
            available_techs.append(tech)
    
    if not available_techs:
        print(f"  ⚠️ No available techs for {service_type}")
        # Update job status
        supabase.table("dispatch_jobs").update({
            "status": STATUS_REASSIGNING,
        }).eq("id", job_id).execute()
        
        return {"status": "no_techs_available", "job_id": job_id}
    
    # Pick first available tech
    tech = available_techs[0]
    tech_phone = tech.get("phone", "")
    tech_name = tech.get("name", "Tech")
    
    # Get job details
    job = supabase.table("dispatch_jobs").select("*").eq("id", job_id).execute()
    if not job.data:
        return {"status": "job_not_found"}
    
    job_data = job.data[0]
    urgency_label = URGENCY_LEVELS.get(job_data.get("urgency", "standard"), "📋 Standard")
    
    # Send dispatch SMS to tech
    message = (
        f"{urgency_label}\n"
        f"New Job: {job_data['service_type']}\n"
        f"📍 {job_data['address']}\n"
        f"👤 {job_data.get('customer_name', 'Customer')}\n"
    )
    if job_data.get("notes"):
        message += f"📝 {job_data['notes']}\n"
    message += f"\nReply ACCEPT or PASS"
    
    webhook_url = os.environ.get("GHL_SMS_WEBHOOK_URL")
    if webhook_url and tech_phone:
        try:
            requests.post(webhook_url, json={
                "phone": tech_phone,
                "message": message,
            }, timeout=15)
        except:
            pass
    
    # Update job with assigned tech
    attempts = job_data.get("dispatch_attempts", 0) + 1
    supabase.table("dispatch_jobs").update({
        "assigned_tech_id": tech["id"],
        "assigned_tech_name": tech_name,
        "assigned_tech_phone": tech_phone,
        "status": STATUS_DISPATCHED,
        "dispatch_attempts": attempts,
        "metadata": json.dumps({
            **json.loads(job_data.get("metadata", "{}") or "{}"),
            f"dispatch_{attempts}": {
                "tech_id": tech["id"],
                "tech_name": tech_name,
                "sent_at": datetime.now(timezone.utc).isoformat(),
            },
        }),
    }).eq("id", job_id).execute()
    
    # Track pending response
    supabase.table("system_state").upsert({
        "key": f"dispatch_pending_{tech_phone}",
        "status": "awaiting_response",
        "last_error": json.dumps({
            "job_id": job_id,
            "tech_id": tech["id"],
            "tech_name": tech_name,
            "sent_at": datetime.now(timezone.utc).isoformat(),
        }),
    }, on_conflict="key").execute()
    
    print(f"  📱 Dispatched to {tech_name} ({tech_phone})")
    return {
        "status": "dispatched",
        "tech_name": tech_name,
        "tech_phone": tech_phone,
        "job_id": job_id,
    }


# ============================================================
#  HANDLE TECH RESPONSE (ACCEPT / PASS)
# ============================================================

def handle_tech_response(tech_phone: str, response: str, supabase) -> dict:
    """
    Process a tech's ACCEPT or PASS reply.
    
    ACCEPT: Update job, confirm to customer, mark tech as busy
    PASS: Clear assignment, dispatch to next available tech
    """
    response = response.strip().upper()
    
    # Look up the pending dispatch
    pending = supabase.table("system_state").select("*").eq(
        "key", f"dispatch_pending_{tech_phone}"
    ).execute()
    
    if not pending.data:
        print(f"  ⚠️ No pending dispatch for {tech_phone}")
        return {"status": "no_pending", "phone": tech_phone}
    
    context = {}
    try:
        context = json.loads(pending.data[0].get("last_error", "{}"))
    except:
        pass
    
    job_id = context.get("job_id", "")
    tech_id = context.get("tech_id", "")
    tech_name = context.get("tech_name", "Tech")
    
    # Get job details
    job = supabase.table("dispatch_jobs").select("*").eq("id", job_id).execute()
    if not job.data:
        return {"status": "job_not_found", "job_id": job_id}
    
    job_data = job.data[0]
    webhook_url = os.environ.get("GHL_SMS_WEBHOOK_URL")
    
    if response == "ACCEPT":
        # ===== TECH ACCEPTED =====
        now = datetime.now(timezone.utc).isoformat()
        
        # Update job status
        supabase.table("dispatch_jobs").update({
            "status": STATUS_ACCEPTED,
            "accepted_at": now,
        }).eq("id", job_id).execute()
        
        # Mark tech as busy
        supabase.table("tech_roster").update({
            "available": False,
            "current_job_id": job_id,
        }).eq("id", tech_id).execute()
        
        # Confirm to tech
        if webhook_url and tech_phone:
            try:
                requests.post(webhook_url, json={
                    "phone": tech_phone,
                    "message": (
                        f"✅ Job confirmed!\n"
                        f"📍 {job_data['address']}\n"
                        f"👤 {job_data.get('customer_name', 'Customer')}: "
                        f"{job_data.get('customer_phone', 'N/A')}\n"
                        f"Reply DONE when complete."
                    ),
                }, timeout=15)
            except:
                pass
        
        # Confirm to customer
        customer_phone = job_data.get("customer_phone", "")
        if webhook_url and customer_phone:
            try:
                requests.post(webhook_url, json={
                    "phone": customer_phone,
                    "message": (
                        f"Great news! {tech_name} has been assigned to your "
                        f"{job_data['service_type']} job and is on the way. "
                        f"— {job_data.get('company_name', 'Your service team')}"
                    ),
                }, timeout=15)
            except:
                pass
        
        # Clear pending state
        supabase.table("system_state").update({
            "status": "accepted",
        }).eq("key", f"dispatch_pending_{tech_phone}").execute()
        
        print(f"  ✅ {tech_name} ACCEPTED job {job_id[:8]}")
        return {
            "status": "accepted",
            "tech_name": tech_name,
            "job_id": job_id,
        }
    
    elif response == "PASS":
        # ===== TECH PASSED — Route to next =====
        
        # Confirm to tech
        if webhook_url and tech_phone:
            try:
                requests.post(webhook_url, json={
                    "phone": tech_phone,
                    "message": "👍 No problem. Job reassigned to another tech.",
                }, timeout=15)
            except:
                pass
        
        # Clear pending state
        supabase.table("system_state").update({
            "status": "passed",
        }).eq("key", f"dispatch_pending_{tech_phone}").execute()
        
        # Collect all techs that already passed
        meta = json.loads(job_data.get("metadata", "{}") or "{}")
        excluded = [tech_id]
        for key, val in meta.items():
            if key.startswith("dispatch_") and isinstance(val, dict):
                tid = val.get("tech_id")
                if tid:
                    excluded.append(tid)
        
        # Re-dispatch to next tech
        print(f"  ↩️ {tech_name} PASSED — routing to next tech")
        return dispatch_to_tech(job_id, job_data["service_type"], supabase,
                                exclude_techs=excluded)
    
    elif response == "DONE":
        # ===== JOB COMPLETED =====
        now = datetime.now(timezone.utc).isoformat()
        
        supabase.table("dispatch_jobs").update({
            "status": STATUS_COMPLETED,
            "completed_at": now,
        }).eq("id", job_id).execute()
        
        # Free up the tech
        supabase.table("tech_roster").update({
            "available": True,
            "current_job_id": None,
        }).eq("id", tech_id).execute()
        
        # Confirm to tech
        if webhook_url and tech_phone:
            try:
                requests.post(webhook_url, json={
                    "phone": tech_phone,
                    "message": "✅ Job marked complete. Great work!",
                }, timeout=15)
            except:
                pass
        
        # Clear pending
        supabase.table("system_state").update({
            "status": "completed",
        }).eq("key", f"dispatch_pending_{tech_phone}").execute()
        
        print(f"  🏁 Job {job_id[:8]} completed by {tech_name}")
        return {
            "status": "completed",
            "tech_name": tech_name,
            "job_id": job_id,
        }
    
    else:
        return {"status": "unknown_response", "response": response}


# ============================================================
#  DISPATCH BOARD (for Dashboard)
# ============================================================

def get_dispatch_board(supabase, limit: int = 20) -> dict:
    """Get active dispatch board for dashboard display."""
    
    # Active jobs
    active = supabase.table("dispatch_jobs").select("*").in_(
        "status", [STATUS_NEW, STATUS_DISPATCHED, STATUS_ACCEPTED, STATUS_EN_ROUTE, STATUS_REASSIGNING]
    ).order("created_at", desc=True).limit(limit).execute()
    
    # Recent completed
    completed = supabase.table("dispatch_jobs").select("*").eq(
        "status", STATUS_COMPLETED
    ).order("completed_at", desc=True).limit(5).execute()
    
    # Tech roster
    techs = supabase.table("tech_roster").select("*").execute()
    
    available_count = sum(1 for t in (techs.data or []) if t.get("available"))
    
    return {
        "active_jobs": active.data or [],
        "recent_completed": completed.data or [],
        "techs": techs.data or [],
        "available_techs": available_count,
        "total_techs": len(techs.data or []),
    }
