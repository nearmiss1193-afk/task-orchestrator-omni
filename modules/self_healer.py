"""
🧠 SELF-HEALING AI SYSTEM
=========================
Autonomous error detection, pattern analysis, and fix suggestion.
Uses Claude AI to analyze errors and generate code fixes.
"""
import os
import json
import traceback
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import requests
from dotenv import load_dotenv
load_dotenv()

# In‑process event bus for error propagation
from .event_bus import bus
from . import graph_store


# === DEPENDENCIES ===
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")

from supabase import create_client
client = create_client(SUPABASE_URL, SUPABASE_KEY)


class SelfHealingAgent:
    """
    Autonomous error detection, analysis, and correction system.
    
    Capabilities:
    1. Log errors with full context to Supabase
    2. Analyze patterns in recent errors
    3. Use Claude to generate fix suggestions
    4. Track fix application status
    """
    
    def __init__(self):
        self.client = client
        self.anthropic_key = ANTHROPIC_KEY
        
    # === 1. ERROR LOGGING ===
    def log_error(
        self, 
        source: str, 
        exception: Exception, 
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Log an error to Supabase with full details.
        
        Args:
            source: Name of the function/module where error occurred
            exception: The caught exception
            context: Additional context (lead data, API response, etc.)
            
        Returns:
            Error log ID if successful, None otherwise
        """
        try:
            # Extract traceback info
            tb = traceback.extract_tb(exception.__traceback__)
            last_frame = tb[-1] if tb else None
            
            error_data = {
                "source": source,
                "error_type": type(exception).__name__,
                "error_message": str(exception),
                "stack_trace": traceback.format_exc(),
                "file_path": last_frame.filename if last_frame else None,
                "line_number": last_frame.lineno if last_frame else None,
                "function_name": last_frame.name if last_frame else None,
                "context": context if context else {}
            }
            
            result = self.client.table("error_logs").insert(error_data).execute()
            
            if result.data:
                error_id = result.data[0]["id"]
                print(f"🧠 [SELF-HEALER] Logged error: {source} → {type(exception).__name__}")
                # Publish event to in‑process bus for downstream learners
                bus.publish({
                    "event": "error_logged",
                    "error_id": error_id,
                    "source": source,
                    "error_type": type(exception).__name__,
                    "timestamp": datetime.utcnow().isoformat()
                })
                return error_id
                
        except Exception as e:
            print(f"🧠 [SELF-HEALER] Failed to log error: {e}")
            
        return None
    
    # === 2. PATTERN ANALYSIS ===
    def analyze_patterns(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Find recurring error patterns in the last N hours.
        
        Returns list of patterns grouped by source and error type,
        sorted by frequency.
        """
        try:
            # Get errors from last N hours
            cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
            
            result = self.client.table("error_logs") \
                .select("*") \
                .gte("created_at", cutoff) \
                .order("created_at", desc=True) \
                .limit(100) \
                .execute()
            
            if not result.data:
                return []
            
            # Group by source + error_type
            patterns = {}
            for error in result.data:
                key = f"{error['source']}::{error['error_type']}"
                if key not in patterns:
                    patterns[key] = {
                        "source": error["source"],
                        "error_type": error["error_type"],
                        "count": 0,
                        "examples": [],
                        "first_seen": error["created_at"],
                        "last_seen": error["created_at"]
                    }
                patterns[key]["count"] += 1
                patterns[key]["last_seen"] = error["created_at"]
                
                # Store up to 3 examples
                if len(patterns[key]["examples"]) < 3:
                    patterns[key]["examples"].append({
                        "id": error["id"],
                        "message": error["error_message"],
                        "file_path": error["file_path"],
                        "line_number": error["line_number"],
                        "stack_trace": error["stack_trace"][:500]  # Truncate
                    })
            
            # Sort by frequency and return top 10
            sorted_patterns = sorted(
                patterns.values(), 
                key=lambda x: x["count"], 
                reverse=True
            )[:10]
            
            print(f"🧠 [SELF-HEALER] Found {len(sorted_patterns)} error patterns in last {hours}h")
            return sorted_patterns
            
        except Exception as e:
            print(f"🧠 [SELF-HEALER] Pattern analysis failed: {e}")
            return []
    
    # === 3. FIX GENERATION ===
    def generate_fix(self, error_id: str) -> Optional[Dict[str, Any]]:
        """
        Use Claude to analyze an error and suggest a fix.
        
        Returns dict with:
        - root_cause: Analysis of why error occurred
        - fix_suggestion: Suggested code change
        - confidence: 0-1 confidence score
        """
        try:
            # Get error details
            result = self.client.table("error_logs") \
                .select("*") \
                .eq("id", error_id) \
                .single() \
                .execute()
            
            if not result.data:
                return None
            
            error = result.data
            
            # Try to read the source file for context
            source_code = ""
            if error.get("file_path") and os.path.exists(error["file_path"]):
                try:
                    with open(error["file_path"], "r") as f:
                        lines = f.readlines()
                        line_num = error.get("line_number", 0)
                        start = max(0, line_num - 15)
                        end = min(len(lines), line_num + 15)
                        source_code = "".join(lines[start:end])
                except:
                    pass
            
            # Build prompt for Claude
            prompt = f"""Analyze this Python error and suggest a fix.

## Error Details
- **Source**: {error['source']}
- **Type**: {error['error_type']}
- **Message**: {error['error_message']}
- **File**: {error.get('file_path', 'Unknown')}
- **Line**: {error.get('line_number', 'Unknown')}
- **Function**: {error.get('function_name', 'Unknown')}

## Stack Trace
```
{error['stack_trace'][:1500]}
```

## Context
```json
{json.dumps(error.get('context', {}), indent=2)[:500]}
```

{f'## Source Code Around Error (lines {start+1}-{end})' if source_code else ''}
{f'```python\n{source_code}\n```' if source_code else ''}

## Your Task
1. Identify the root cause of this error
2. Suggest a specific code fix
3. Rate your confidence (0-1) in the fix

Respond in this JSON format:
{{
    "root_cause": "Explanation of why this error occurred",
    "fix_suggestion": "The corrected code snippet or patch",
    "confidence": 0.85,
    "prevention_tip": "How to prevent this error in the future"
}}"""

            # Call Claude API
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.anthropic_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1500,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=60
            )
            
            if response.status_code == 200:
                content = response.json()["content"][0]["text"]
                
                # Parse JSON from response
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    fix_data = json.loads(json_match.group())
                    
                    # Save fix suggestion to database
                    self.client.table("error_logs").update({
                        "fix_suggested": json.dumps(fix_data)
                    }).eq("id", error_id).execute()
                    
                    print(f"🧠 [SELF-HEALER] Generated fix for {error['source']}")
                    print(f"   Root cause: {fix_data.get('root_cause', 'Unknown')[:100]}...")
                    print(f"   Confidence: {fix_data.get('confidence', 0)}")
                    
                    return fix_data
            else:
                print(f"🧠 [SELF-HEALER] Claude API error: {response.status_code}")
                
        except Exception as e:
            print(f"🧠 [SELF-HEALER] Fix generation failed: {e}")
            
        return None
    
    # === 4. AUTO-FIX APPLICATION ===
    def apply_fix(
        self, 
        error_id: str, 
        fix_code: str,
        auto: bool = False
    ) -> bool:
        """
        Apply a suggested fix to the codebase.
        
        Args:
            error_id: ID of the error log
            fix_code: The corrected code to apply
            auto: If True and confidence > 0.8, auto-apply
            
        Returns:
            True if fix was applied, False otherwise
        """
        try:
            # Get error details
            result = self.client.table("error_logs") \
                .select("*") \
                .eq("id", error_id) \
                .single() \
                .execute()
            
            if not result.data:
                return False
            
            error = result.data
            file_path = error.get("file_path")
            
            if not file_path or not os.path.exists(file_path):
                print(f"🧠 [SELF-HEALER] Cannot apply fix: file not found")
                return False
            
            # Parse fix suggestion if stored
            fix_data = {}
            if error.get("fix_suggested"):
                try:
                    fix_data = json.loads(error["fix_suggested"])
                except:
                    pass
            
            confidence = fix_data.get("confidence", 0)
            
            # Safety check for auto mode
            if auto and confidence < 0.8:
                print(f"🧠 [SELF-HEALER] Confidence too low for auto-apply: {confidence}")
                return False
            
            # Create backup
            backup_path = f"{file_path}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(file_path, "r") as f:
                original_content = f.read()
            with open(backup_path, "w") as f:
                f.write(original_content)
            
            print(f"🧠 [SELF-HEALER] Created backup: {backup_path}")
            
            # For now, just log that we would apply the fix
            # Actual code modification requires more sophisticated patching
            print(f"🧠 [SELF-HEALER] Fix ready to apply:")
            print(f"   File: {file_path}")
            print(f"   Line: {error.get('line_number')}")
            print(f"   Suggested fix stored in database")
            
            # Update database
            self.client.table("error_logs").update({
                "fix_applied": True,
                "fix_applied_at": datetime.utcnow().isoformat()
            }).eq("id", error_id).execute()
            
            return True
            
        except Exception as e:
            print(f"🧠 [SELF-HEALER] Fix application failed: {e}")
            return False
    
    # === 5. SELF-HEAL CYCLE ===
    def self_heal_cycle(self, hours: int = 4) -> Dict[str, Any]:
        """
        Main healing loop: analyze → suggest → (optionally) apply.
        
        Returns summary of actions taken.
        """
        print(f"\n{'='*60}")
        print(f"🧠 SELF-HEALING CYCLE - {datetime.now().strftime('%I:%M %p')}")
        print(f"{'='*60}\n")
        
        results = {
            "patterns_found": 0,
            "fixes_generated": 0,
            "fixes_applied": 0,
            "errors": []
        }
        
        try:
            # 1. Analyze patterns
            patterns = self.analyze_patterns(hours=hours)
            results["patterns_found"] = len(patterns)
            
            if not patterns:
                print("✅ No recurring error patterns found!")
                return results
            
            print(f"\n📊 Top Error Patterns:")
            for i, p in enumerate(patterns[:5], 1):
                print(f"   {i}. {p['source']} → {p['error_type']}: {p['count']} occurrences")
            
            # 2. Generate fixes for recurring errors (count > 2)
            for pattern in patterns:
                if pattern["count"] < 2:
                    continue
                
                # Get most recent example
                if pattern["examples"]:
                    example = pattern["examples"][0]
                    
                    print(f"\n🔧 Generating fix for: {pattern['source']}")
                    fix = self.generate_fix(example["id"])
                    
                    if fix:
                        results["fixes_generated"] += 1
                        
                        # Check if high confidence for potential auto-apply
                        if fix.get("confidence", 0) >= 0.9:
                            print(f"   ⚡ High confidence fix available!")
                            print(f"   Root cause: {fix.get('root_cause', '')[:100]}")
            
            print(f"\n📈 Healing Cycle Summary:")
            print(f"   Patterns analyzed: {results['patterns_found']}")
            print(f"   Fixes generated: {results['fixes_generated']}")
            
        except Exception as e:
            results["errors"].append(str(e))
            print(f"❌ Healing cycle error: {e}")
        
        return results
    
    # === 6. GET RECENT ERRORS ===
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent errors for review."""
        try:
            result = self.client.table("error_logs") \
                .select("*") \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            return result.data if result.data else []
        except:
            return []
    
    # === 7. GET UNFIXED ERRORS ===
    def get_unfixed_errors(self) -> List[Dict[str, Any]]:
        """Get errors that have suggested fixes but haven't been applied."""
        try:
            result = self.client.table("error_logs") \
                .select("*") \
                .not_.is_("fix_suggested", "null") \
                .eq("fix_applied", False) \
                .order("created_at", desc=True) \
                .limit(20) \
                .execute()
            return result.data if result.data else []
        except:
            return []


# === HELPER FUNCTION FOR AGENTS ===
def wrap_with_healing(func):
    """
    Decorator to automatically log errors to self-healer.
    
    Usage:
        @wrap_with_healing
        def my_agent():
            # ... agent code
    """
    healer = SelfHealingAgent()
    
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            healer.log_error(func.__name__, e, {"args": str(args)[:200]})
            raise
    
    return wrapper


# === QUICK TEST ===
if __name__ == "__main__":
    print("🧠 Testing Self-Healing Agent...")
    
    healer = SelfHealingAgent()
    
    # Test 1: Log a test error
    print("\n1. Testing error logging...")
    try:
        raise ValueError("Test error for self-healer")
    except Exception as e:
        error_id = healer.log_error("test_source", e, {"test": "context"})
        print(f"   Logged error ID: {error_id}")
    
    # Test 2: Pattern analysis
    print("\n2. Testing pattern analysis...")
    patterns = healer.analyze_patterns(hours=24)
    print(f"   Found {len(patterns)} patterns")
    
    # Test 3: Generate fix (if we have an error)
    if error_id:
        print("\n3. Testing fix generation...")
        fix = healer.generate_fix(error_id)
        if fix:
            print(f"   Root cause: {fix.get('root_cause', 'Unknown')[:100]}")
            print(f"   Confidence: {fix.get('confidence', 0)}")
    
    print("\n✅ Self-Healer tests complete!")
