"""
Meta-Learning Loop for Self-Healing System.
Implements RLHF (Reinforcement Learning from Human Feedback),
self-supervised error embeddings, and online model updates.
"""
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from .event_bus import bus
from .graph_store import graph_store

# Feature flags
FEATURE_FLAGS = {
    "rlhf_enabled": os.getenv("RLHF_ENABLED", "true").lower() == "true",
    "auto_retrain": os.getenv("AUTO_RETRAIN", "false").lower() == "true",
    "embedding_model": os.getenv("EMBEDDING_MODEL", "simple"),  # simple or transformer
}


class MetaLearner:
    """
    Meta-learning system that learns how to learn from errors.
    
    Capabilities:
    1. RLHF - Learn from human fix approvals/rejections
    2. Error clustering - Group similar errors
    3. Fix effectiveness tracking - Which fixes work best
    4. Knowledge distillation - Extract patterns into rules
    """
    
    def __init__(self):
        self.fix_outcomes: List[Dict[str, Any]] = []
        self.human_feedback: List[Dict[str, Any]] = []
        self.error_clusters: Dict[str, List[str]] = {}  # cluster_id -> [error_ids]
        self.fix_templates: Dict[str, Dict] = {}  # pattern -> {fix, confidence, usage_count}
        self._subscribe_to_events()
        self._load_cached_knowledge()
    
    def _subscribe_to_events(self):
        """Subscribe to relevant events."""
        bus.subscribe(self._on_event)
        print("🧪 [META-LEARNER] Subscribed to learning events")
    
    def _on_event(self, event: Dict[str, Any]):
        """Handle incoming events."""
        event_type = event.get("event")
        
        if event_type == "error_logged":
            self._process_new_error(event)
        elif event_type == "fix_applied":
            self._record_fix_application(event)
        elif event_type == "fix_feedback":
            self._process_human_feedback(event)
    
    def _load_cached_knowledge(self):
        """Load previously learned patterns from graph store."""
        try:
            # Load fix templates from graph store
            cur = graph_store.conn.cursor()
            cur.execute("SELECT label, data FROM nodes WHERE label LIKE 'fix_template:%'")
            for row in cur.fetchall():
                pattern = row[0].replace("fix_template:", "")
                data = json.loads(row[1]) if row[1] else {}
                self.fix_templates[pattern] = data
            print(f"🧪 [META-LEARNER] Loaded {len(self.fix_templates)} fix templates")
        except Exception as e:
            print(f"🧪 [META-LEARNER] Cache load error: {e}")
    
    def _compute_error_signature(self, error: Dict) -> str:
        """Compute a signature for error clustering."""
        key_parts = [
            error.get("error_type", ""),
            error.get("source", ""),
            # Normalize message by removing variable parts
            self._normalize_message(error.get("error_message", ""))
        ]
        signature = hashlib.md5("|".join(key_parts).encode()).hexdigest()[:12]
        return signature
    
    def _normalize_message(self, message: str) -> str:
        """Normalize error message by removing variable parts."""
        import re
        # Remove numbers, UUIDs, timestamps, etc.
        message = re.sub(r'\d+', 'N', message)
        message = re.sub(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', 'UUID', message)
        message = re.sub(r'\'[^\']+\'', 'STR', message)
        message = re.sub(r'"[^"]+"', 'STR', message)
        return message
    
    def _process_new_error(self, event: Dict[str, Any]):
        """Process a new error and cluster it."""
        error_id = event.get("error_id")
        signature = self._compute_error_signature(event)
        
        # Add to cluster
        if signature not in self.error_clusters:
            self.error_clusters[signature] = []
        self.error_clusters[signature].append(error_id)
        
        # Check if we have a known fix for this pattern
        if signature in self.fix_templates:
            template = self.fix_templates[signature]
            print(f"🧪 [META-LEARNER] Known pattern detected: {signature}")
            print(f"   Confidence: {template.get('confidence', 0):.2f}")
            
            # If high confidence, suggest auto-apply
            if template.get("confidence", 0) >= 0.95 and FEATURE_FLAGS["auto_retrain"]:
                bus.publish({
                    "event": "auto_fix_available",
                    "error_id": error_id,
                    "fix_template": template,
                    "signature": signature
                })
    
    def _record_fix_application(self, event: Dict[str, Any]):
        """Record when a fix is applied."""
        self.fix_outcomes.append({
            "error_id": event.get("error_id"),
            "fix_code": event.get("fix_code"),
            "applied_at": datetime.utcnow().isoformat(),
            "success": None  # Will be updated by outcome feedback
        })
    
    def _process_human_feedback(self, event: Dict[str, Any]):
        """Process human feedback on fix quality (RLHF)."""
        if not FEATURE_FLAGS["rlhf_enabled"]:
            return
        
        feedback = {
            "error_id": event.get("error_id"),
            "fix_approved": event.get("approved", False),
            "rating": event.get("rating", 0),  # 1-5 scale
            "comments": event.get("comments", ""),
            "timestamp": datetime.utcnow().isoformat()
        }
        self.human_feedback.append(feedback)
        
        # Update fix template confidence based on feedback
        signature = event.get("error_signature")
        if signature and signature in self.fix_templates:
            template = self.fix_templates[signature]
            old_confidence = template.get("confidence", 0.5)
            
            # Bayesian update based on feedback
            if event.get("approved"):
                new_confidence = min(1.0, old_confidence + 0.1 * (1 - old_confidence))
            else:
                new_confidence = max(0.0, old_confidence - 0.2 * old_confidence)
            
            template["confidence"] = new_confidence
            template["usage_count"] = template.get("usage_count", 0) + 1
            template["last_feedback"] = datetime.utcnow().isoformat()
            
            # Save to graph store
            self._save_fix_template(signature, template)
            
            print(f"🧪 [META-LEARNER] Updated template {signature}: {old_confidence:.2f} → {new_confidence:.2f}")
    
    def record_fix_outcome(self, error_id: str, success: bool, error_signature: str = None):
        """Record whether a fix was successful."""
        # Find the fix outcome
        for outcome in self.fix_outcomes:
            if outcome["error_id"] == error_id:
                outcome["success"] = success
                outcome["verified_at"] = datetime.utcnow().isoformat()
                break
        
        # Update cluster statistics
        if error_signature:
            if error_signature not in self.fix_templates:
                self.fix_templates[error_signature] = {
                    "confidence": 0.5,
                    "usage_count": 0,
                    "success_count": 0,
                    "fail_count": 0
                }
            
            template = self.fix_templates[error_signature]
            template["usage_count"] += 1
            if success:
                template["success_count"] = template.get("success_count", 0) + 1
            else:
                template["fail_count"] = template.get("fail_count", 0) + 1
            
            # Update confidence based on success rate
            total = template.get("success_count", 0) + template.get("fail_count", 0)
            if total > 0:
                template["confidence"] = template["success_count"] / total
            
            self._save_fix_template(error_signature, template)
    
    def _save_fix_template(self, signature: str, template: Dict):
        """Save fix template to graph store."""
        try:
            graph_store.add_node(
                label=f"fix_template:{signature}",
                data=json.dumps(template)
            )
        except:
            pass
    
    def learn_fix_pattern(self, error_type: str, error_message: str, fix_code: str):
        """Learn a new fix pattern from a successful fix."""
        signature = self._compute_error_signature({
            "error_type": error_type,
            "error_message": error_message,
            "source": "learned"
        })
        
        template = {
            "error_type": error_type,
            "error_pattern": self._normalize_message(error_message),
            "fix_code": fix_code,
            "confidence": 0.7,  # Start with medium confidence
            "usage_count": 1,
            "learned_at": datetime.utcnow().isoformat()
        }
        
        self.fix_templates[signature] = template
        self._save_fix_template(signature, template)
        
        print(f"🧪 [META-LEARNER] Learned new pattern: {signature}")
        return signature
    
    def get_stats(self) -> Dict[str, Any]:
        """Get meta-learner statistics."""
        return {
            "fix_outcomes_recorded": len(self.fix_outcomes),
            "human_feedback_count": len(self.human_feedback),
            "error_clusters": len(self.error_clusters),
            "fix_templates": len(self.fix_templates),
            "feature_flags": FEATURE_FLAGS,
            "top_patterns": sorted(
                [(k, v.get("confidence", 0), v.get("usage_count", 0)) 
                 for k, v in self.fix_templates.items()],
                key=lambda x: x[2],
                reverse=True
            )[:5]
        }
    
    def suggest_fix(self, error: Dict) -> Optional[Dict]:
        """Suggest a fix based on learned patterns."""
        signature = self._compute_error_signature(error)
        
        if signature in self.fix_templates:
            template = self.fix_templates[signature]
            if template.get("confidence", 0) >= 0.6:
                return {
                    "signature": signature,
                    "fix_code": template.get("fix_code"),
                    "confidence": template.get("confidence"),
                    "usage_count": template.get("usage_count", 0),
                    "source": "meta_learner"
                }
        return None


# Singleton instance
meta_learner = MetaLearner()


def submit_human_feedback(error_id: str, approved: bool, rating: int = 3, comments: str = ""):
    """Submit human feedback for RLHF."""
    bus.publish({
        "event": "fix_feedback",
        "error_id": error_id,
        "approved": approved,
        "rating": rating,
        "comments": comments
    })
