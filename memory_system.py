"""
UNIFIED MEMORY SYSTEM
Memory storage and retrieval for all agents:
- Sarah (voice/SMS responder)
- Orchestrator (Antigravity)
- Brain (session memory)
"""
import os
import json
import requests
from datetime import datetime
from typing import Optional, Dict, List, Any

# Supabase config
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", 
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAfqN89E6mIoKT3OWNKKXrN4xZIqoOHHNo")

from sarah_prompts import (
    SARAH_SYSTEM_PROMPT,
    MEMORY_RETRIEVAL_TEMPLATE,
    MEMORY_EXTRACTION_SYSTEM,
    MEMORY_EXTRACTION_USER_TEMPLATE,
    SELF_IMPROVEMENT_SYSTEM,
    SELF_IMPROVEMENT_USER_TEMPLATE,
    FOLLOWUP_GENERATOR_PROMPT,
    ORCHESTRATOR_MEMORY_RETRIEVAL
)

class UnifiedMemory:
    """Unified memory system for all agents"""
    
    def __init__(self):
        self.headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
    
    # =========================================================================
    # CONTACT METHODS
    # =========================================================================
    
    def get_or_create_contact(self, phone: str = None, email: str = None) -> Dict:
        """Get existing contact or create new one"""
        if not phone and not email:
            return {}
        
        # Try to find by phone first
        if phone:
            r = requests.get(
                f"{SUPABASE_URL}/rest/v1/contacts",
                headers=self.headers,
                params={"phone": f"eq.{phone}", "limit": 1}
            )
            if r.status_code == 200 and r.json():
                return r.json()[0]
        
        # Try by email
        if email:
            r = requests.get(
                f"{SUPABASE_URL}/rest/v1/contacts",
                headers=self.headers,
                params={"email": f"eq.{email}", "limit": 1}
            )
            if r.status_code == 200 and r.json():
                return r.json()[0]
        
        # Create new contact
        new_contact = {
            "phone": phone,
            "email": email,
            "pipeline_stage": "new",
            "interaction_count": 0
        }
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/contacts",
            headers={**self.headers, "Prefer": "return=representation"},
            json=new_contact
        )
        if r.status_code in [200, 201]:
            return r.json()[0] if isinstance(r.json(), list) else r.json()
        return new_contact
    
    def update_contact(self, contact_id: str, updates: Dict) -> bool:
        """Update contact record"""
        updates["updated_at"] = datetime.utcnow().isoformat()
        r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/contacts?id=eq.{contact_id}",
            headers=self.headers,
            json=updates
        )
        return r.status_code in [200, 204]
    
    # =========================================================================
    # MEMORY RETRIEVAL (for injection before AI responds)
    # =========================================================================
    
    def get_memory_context(self, phone: str = None, email: str = None, contact_id: str = None) -> str:
        """
        Get formatted memory context for injection into AI prompt.
        Returns formatted string matching MEMORY_RETRIEVAL_TEMPLATE.
        """
        # Get contact
        contact = {}
        if contact_id:
            r = requests.get(
                f"{SUPABASE_URL}/rest/v1/contacts?id=eq.{contact_id}",
                headers=self.headers
            )
            if r.status_code == 200 and r.json():
                contact = r.json()[0]
        elif phone or email:
            contact = self.get_or_create_contact(phone, email)
        
        if not contact:
            return ""
        
        cid = contact.get("id", "")
        
        # Get high-confidence memories
        memories = self._get_memories(cid, min_confidence=0.7)
        key_memories = "\n".join([
            f"- {m['key']}: {m['value']} (confidence: {m['confidence']})"
            for m in memories
        ]) or "No prior memory"
        
        # Get recent interactions
        interactions = self._get_recent_interactions(cid, limit=3)
        recent_interactions = "\n".join([
            f"- {i['created_at'][:10]} | {i['channel']} | {i.get('intent', 'unknown')} | {i.get('outcome', 'unknown')}"
            for i in interactions
        ]) or "No prior interactions"
        
        # Get open tasks (pending follow-ups, escalations)
        open_tasks = self._get_open_tasks(cid)
        
        return MEMORY_RETRIEVAL_TEMPLATE.format(
            name=contact.get("name", "Unknown"),
            phone=contact.get("phone", "Unknown"),
            email=contact.get("email", "Unknown"),
            timezone=contact.get("timezone", "Unknown"),
            pipeline_stage=contact.get("pipeline_stage", "new"),
            tags=", ".join(contact.get("tags", [])) or "None",
            key_memories=key_memories,
            recent_interactions=recent_interactions,
            open_tasks=open_tasks
        )
    
    def _get_memories(self, contact_id: str, min_confidence: float = 0.5) -> List[Dict]:
        """Get memories for a contact above confidence threshold"""
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/memories",
            headers=self.headers,
            params={
                "contact_id": f"eq.{contact_id}",
                "confidence": f"gte.{min_confidence}",
                "order": "priority.asc,confidence.desc",
                "limit": 10
            }
        )
        return r.json() if r.status_code == 200 else []
    
    def _get_recent_interactions(self, contact_id: str, limit: int = 3) -> List[Dict]:
        """Get recent interactions for a contact"""
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/interactions",
            headers=self.headers,
            params={
                "contact_id": f"eq.{contact_id}",
                "order": "created_at.desc",
                "limit": limit
            }
        )
        return r.json() if r.status_code == 200 else []
    
    def _get_open_tasks(self, contact_id: str) -> str:
        """Get pending tasks for a contact"""
        # Check for pending follow-ups
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/interactions",
            headers=self.headers,
            params={
                "contact_id": f"eq.{contact_id}",
                "outcome": "eq.follow_up",
                "order": "created_at.desc",
                "limit": 1
            }
        )
        
        tasks = []
        if r.status_code == 200 and r.json():
            tasks.append("Pending follow-up")
        
        # Check for escalations
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/interactions",
            headers=self.headers,
            params={
                "contact_id": f"eq.{contact_id}",
                "escalated": "eq.true",
                "order": "created_at.desc",
                "limit": 1
            }
        )
        if r.status_code == 200 and r.json():
            tasks.append(f"Escalation: {r.json()[0].get('escalation_reason', 'Unknown')}")
        
        return "\n".join([f"- {t}" for t in tasks]) or "No open tasks"
    
    # =========================================================================
    # MEMORY EXTRACTION (after interaction)
    # =========================================================================
    
    def extract_and_store_memory(self, 
                                  phone: str,
                                  channel: str,
                                  transcript: str,
                                  ai_response: str = None) -> Dict:
        """
        Extract memory from interaction using AI, then store it.
        Returns the extracted data.
        """
        # Get or create contact
        contact = self.get_or_create_contact(phone=phone)
        contact_id = contact.get("id")
        
        # Get existing memories for context
        existing_memories = self._get_memories(contact_id) if contact_id else []
        existing_memory_str = "\n".join([
            f"- {m['key']}: {m['value']}"
            for m in existing_memories
        ]) or "None"
        
        # Call AI to extract memory
        extracted = self._ai_extract_memory(channel, transcript, existing_memory_str)
        
        if not extracted:
            return {}
        
        # Store interaction
        interaction_id = self._store_interaction(
            contact_id=contact_id,
            phone=phone,
            channel=channel,
            direction="inbound",
            user_message=transcript,
            ai_response=ai_response,
            intent=extracted.get("intent"),
            sentiment=extracted.get("sentiment"),
            outcome=extracted.get("next_action"),
            escalated=extracted.get("escalate", {}).get("needed", False),
            escalation_reason=extracted.get("escalate", {}).get("reason"),
            escalation_urgency=extracted.get("escalate", {}).get("urgency")
        )
        
        # Store memories
        for fact in extracted.get("key_facts", []):
            self._store_memory(contact_id, phone, "fact", fact["key"], fact["value"], 
                             fact.get("confidence", 0.8), interaction_id)
        
        for pref in extracted.get("preferences", []):
            self._store_memory(contact_id, phone, "preference", pref["key"], pref["value"],
                             pref.get("confidence", 0.8), interaction_id)
        
        for obj in extracted.get("objections", []):
            self._store_memory(contact_id, phone, "objection", obj["type"], obj.get("detail", ""),
                             0.9, interaction_id)
        
        # Update contact summary
        if contact_id:
            self.update_contact(contact_id, {
                "summary_1_sentence": extracted.get("summary_1_sentence"),
                "lead_fit": extracted.get("lead_fit", {}).get("fit"),
                "sentiment": extracted.get("sentiment"),
                "last_interaction_at": datetime.utcnow().isoformat(),
                "interaction_count": contact.get("interaction_count", 0) + 1,
                "opt_out": extracted.get("opt_out", False)
            })
        
        return extracted
    
    def _ai_extract_memory(self, channel: str, transcript: str, existing_memory: str) -> Dict:
        """Use AI to extract structured memory from transcript"""
        prompt = MEMORY_EXTRACTION_USER_TEMPLATE.format(
            channel=channel,
            transcript=transcript,
            existing_memory=existing_memory
        )
        
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={
                    "systemInstruction": {"parts": [{"text": MEMORY_EXTRACTION_SYSTEM}]},
                    "contents": [{"parts": [{"text": prompt}]}]
                },
                timeout=30
            )
            if r.status_code == 200:
                text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                # Parse JSON from response
                text = text.strip()
                if text.startswith("```"):
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
                return json.loads(text)
        except Exception as e:
            print(f"Memory extraction error: {e}")
        return {}
    
    def _store_interaction(self, **kwargs) -> Optional[str]:
        """Store interaction record"""
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/interactions",
            headers={**self.headers, "Prefer": "return=representation"},
            json=kwargs
        )
        if r.status_code in [200, 201]:
            result = r.json()
            return result[0]["id"] if isinstance(result, list) else result.get("id")
        return None
    
    def _store_memory(self, contact_id: str, phone: str, memory_type: str,
                      key: str, value: str, confidence: float, 
                      source_interaction_id: str = None) -> bool:
        """Store a memory item"""
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/memories",
            headers=self.headers,
            json={
                "contact_id": contact_id,
                "phone": phone,
                "memory_type": memory_type,
                "key": key,
                "value": value,
                "confidence": confidence,
                "source_interaction_id": source_interaction_id
            }
        )
        return r.status_code in [200, 201]
    
    # =========================================================================
    # FOLLOW-UP GENERATION
    # =========================================================================
    
    def generate_followup(self, phone: str) -> Optional[str]:
        """Generate a follow-up message for a contact"""
        contact = self.get_or_create_contact(phone=phone)
        contact_id = contact.get("id")
        
        if not contact_id:
            return None
        
        # Get last interaction
        interactions = self._get_recent_interactions(contact_id, limit=1)
        if not interactions:
            return None
        
        last = interactions[0]
        
        # Get objections from memory
        memories = self._get_memories(contact_id)
        objections = [m for m in memories if m.get("memory_type") == "objection"]
        top_objection = objections[0]["value"] if objections else "None"
        
        # Count follow-ups
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/interactions",
            headers=self.headers,
            params={
                "contact_id": f"eq.{contact_id}",
                "direction": "eq.outbound",
                "outcome": "eq.follow_up",
                "select": "count"
            }
        )
        followup_count = len(r.json()) if r.status_code == 200 else 1
        
        prompt = FOLLOWUP_GENERATOR_PROMPT.format(
            intent=last.get("intent", "unknown"),
            objection=top_objection,
            last_outbound=last.get("ai_response", "")[:100],
            followup_number=followup_count + 1
        )
        
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except:
            pass
        return None
    
    # =========================================================================
    # SELF-IMPROVEMENT (daily batch)
    # =========================================================================
    
    def run_self_improvement(self, batch_size: int = 50) -> Dict:
        """Run self-improvement analysis on recent interactions"""
        # Get recent interactions with outcomes
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/interactions",
            headers=self.headers,
            params={
                "select": "*",
                "order": "created_at.desc",
                "limit": batch_size
            }
        )
        
        if r.status_code != 200:
            return {}
        
        interactions = r.json()
        
        # Format batch data
        batch_data = json.dumps([
            {
                "outcome": i.get("outcome"),
                "intent": i.get("intent"),
                "sentiment": i.get("sentiment"),
                "escalated": i.get("escalated"),
                "user_message": i.get("user_message", "")[:200],
                "ai_response": i.get("ai_response", "")[:200]
            }
            for i in interactions
        ], indent=2)
        
        prompt = SELF_IMPROVEMENT_USER_TEMPLATE.format(
            batch_size=len(interactions),
            batch_data=batch_data
        )
        
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={
                    "systemInstruction": {"parts": [{"text": SELF_IMPROVEMENT_SYSTEM}]},
                    "contents": [{"parts": [{"text": prompt}]}]
                },
                timeout=60
            )
            if r.status_code == 200:
                text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                text = text.strip()
                if text.startswith("```"):
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
                
                improvements = json.loads(text)
                
                # Store suggestions in playbook_updates
                for suggestion in improvements.get("suggested_script_changes", []):
                    requests.post(
                        f"{SUPABASE_URL}/rest/v1/playbook_updates",
                        headers=self.headers,
                        json={
                            "update_type": "script_change",
                            "where_applies": suggestion.get("where"),
                            "change_description": suggestion.get("change"),
                            "reason": suggestion.get("reason"),
                            "risk_level": suggestion.get("risk", "med"),
                            "status": "proposed"
                        }
                    )
                
                return improvements
        except Exception as e:
            print(f"Self-improvement error: {e}")
        
        return {}


# Singleton instance
memory = UnifiedMemory()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_sarah_prompt_with_memory(phone: str) -> str:
    """Get full Sarah system prompt with memory context injected"""
    memory_context = memory.get_memory_context(phone=phone)
    return f"{SARAH_SYSTEM_PROMPT}\n\n{memory_context}"

def process_interaction(phone: str, channel: str, user_message: str, ai_response: str):
    """Process an interaction: extract and store memory"""
    transcript = f"User: {user_message}\nSarah: {ai_response}"
    return memory.extract_and_store_memory(phone, channel, transcript, ai_response)

def get_followup_message(phone: str) -> Optional[str]:
    """Generate a follow-up message for a contact"""
    return memory.generate_followup(phone)

def run_daily_improvement():
    """Run daily self-improvement analysis"""
    return memory.run_self_improvement(batch_size=50)


if __name__ == "__main__":
    print("=" * 60)
    print("UNIFIED MEMORY SYSTEM - TEST")
    print("=" * 60)
    
    # Test memory retrieval
    print("\n[TEST] Memory retrieval for phone +1234567890:")
    context = memory.get_memory_context(phone="+1234567890")
    print(context[:500] if context else "No memory found")
    
    print("\n[TEST] Full Sarah prompt with memory:")
    full_prompt = get_sarah_prompt_with_memory("+1234567890")
    print(full_prompt[:800])
