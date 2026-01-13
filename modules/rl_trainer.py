"""
Reinforcement Learning Trainer for Self-Healing System.
Subscribes to error events from the bus and learns from fix outcomes.
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List
from .event_bus import bus
from .graph_store import graph_store

# Feature flags for safety
FEATURE_FLAGS = {
    "rl_training_enabled": os.getenv("RL_TRAINING_ENABLED", "false").lower() == "true",
    "auto_apply_fixes": os.getenv("AUTO_APPLY_FIXES", "false").lower() == "true",
    "min_confidence_threshold": float(os.getenv("MIN_CONFIDENCE_THRESHOLD", "0.85")),
}


class RLTrainer:
    """Reinforcement Learning trainer that learns from error/fix outcomes."""
    
    def __init__(self):
        self.experiences: List[Dict[str, Any]] = []
        self.model_version = "0.1.0"
        self._subscribe_to_events()
    
    def _subscribe_to_events(self):
        """Subscribe to error_logged events from the bus."""
        bus.subscribe(self._on_error_event)
        print("🤖 [RL-TRAINER] Subscribed to error events")
    
    def _on_error_event(self, event: Dict[str, Any]):
        """Handle incoming error events."""
        if event.get("event") != "error_logged":
            return
        
        # Store experience for later training
        experience = {
            "error_id": event.get("error_id"),
            "source": event.get("source"),
            "error_type": event.get("error_type"),
            "timestamp": event.get("timestamp"),
            "fix_applied": False,
            "fix_successful": None,
            "reward": 0.0,
        }
        self.experiences.append(experience)
        
        # Add node to knowledge graph
        node_id = graph_store.add_node(
            label=f"error:{event.get('error_type')}",
            data=json.dumps(experience)
        )
        
        print(f"🤖 [RL-TRAINER] Recorded experience: {event.get('source')} → {event.get('error_type')}")
        
        # Check if we should trigger training
        if len(self.experiences) >= 10 and FEATURE_FLAGS["rl_training_enabled"]:
            self._train_batch()
    
    def record_fix_outcome(self, error_id: str, success: bool):
        """Record whether a fix was successful (reward signal)."""
        for exp in self.experiences:
            if exp["error_id"] == error_id:
                exp["fix_applied"] = True
                exp["fix_successful"] = success
                exp["reward"] = 1.0 if success else -0.5
                print(f"🤖 [RL-TRAINER] Recorded outcome for {error_id}: {'✓' if success else '✗'}")
                break
    
    def _train_batch(self):
        """Train on accumulated experiences."""
        if not FEATURE_FLAGS["rl_training_enabled"]:
            print("🤖 [RL-TRAINER] Training disabled by feature flag")
            return
        
        labeled_experiences = [e for e in self.experiences if e["fix_applied"]]
        if len(labeled_experiences) < 5:
            print("🤖 [RL-TRAINER] Not enough labeled experiences for training")
            return
        
        # Placeholder: actual RL training would happen here
        # For now, just log that we would train
        print(f"🤖 [RL-TRAINER] Would train on {len(labeled_experiences)} experiences")
        
        # Clear processed experiences
        self.experiences = [e for e in self.experiences if not e["fix_applied"]]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get trainer statistics."""
        return {
            "model_version": self.model_version,
            "pending_experiences": len(self.experiences),
            "labeled_count": sum(1 for e in self.experiences if e["fix_applied"]),
            "feature_flags": FEATURE_FLAGS,
        }


# Auto-instantiate trainer when module is imported
rl_trainer = RLTrainer()
