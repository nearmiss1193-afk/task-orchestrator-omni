#!/usr/bin/env python3
"""
Anneal Wrapper - Universal Self-Annealing Script Wrapper
=========================================================

Wraps ANY Python script with self-annealing capabilities.

Usage:
    python anneal_wrapper.py <script.py> [args...]

Example:
    python anneal_wrapper.py enrich_leads.py --input data.json

What it does:
- Captures stdout/stderr
- Logs errors with full context to orchestrator_logs/
- Triggers retry with exponential backoff
- Updates corresponding directive with learned edge case
"""

import sys
import os
import subprocess
import traceback
import json
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from annealing_engine import (
    anneal_script,
    log_annealing_event,
    classify_error,
    update_directive_learnings,
    update_error_memory,
    LOGS_DIR
)


def print_banner():
    print("=" * 60)
    print("  ANNEAL WRAPPER - Self-Annealing Execution")
    print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print("Usage: python anneal_wrapper.py <script.py> [args...]")
        print("\nExample:")
        print("  python anneal_wrapper.py enrich_leads.py")
        print("  python anneal_wrapper.py ghl_sync.py --dry-run")
        sys.exit(1)
    
    script_path = sys.argv[1]
    script_args = sys.argv[2:]
    
    # Resolve script path
    if not os.path.isabs(script_path):
        # Check in current dir, then execution dir
        if os.path.exists(script_path):
            script_path = os.path.abspath(script_path)
        else:
            execution_dir = Path(__file__).parent
            candidate = execution_dir / script_path
            if candidate.exists():
                script_path = str(candidate)
            else:
                print(f"[ANNEAL] ERROR: Script not found: {script_path}")
                sys.exit(1)
    
    print_banner()
    print(f"[ANNEAL] Script: {script_path}")
    print(f"[ANNEAL] Args: {script_args}")
    print(f"[ANNEAL] Time: {datetime.now().isoformat()}")
    print("-" * 60)
    
    # Execute with annealing
    result = anneal_script(script_path, script_args)
    
    print("-" * 60)
    
    if result.success:
        print(f"[ANNEAL] ✅ SUCCESS after {result.retries} retries")
        print(f"[ANNEAL] Output:")
        print(result.result[:2000] if result.result else "(no output)")
        sys.exit(0)
    else:
        print(f"[ANNEAL] ❌ FAILED after {result.retries} retries")
        print(f"[ANNEAL] Error: {result.error}")
        
        classification = classify_error(result.error)
        print(f"[ANNEAL] Category: {classification['category']}")
        print(f"[ANNEAL] Safe to auto-fix: {classification['safe_to_auto_fix']}")
        print(f"[ANNEAL] Suggested fix: {classification['suggested_fix']}")
        
        if result.fix_applied:
            print(f"[ANNEAL] Directive updated with learning")
        
        if not classification['safe_to_auto_fix']:
            print("\n" + "!" * 60)
            print("  REQUIRES HUMAN REVIEW")
            print("!" * 60)
            print(f"Check logs: {LOGS_DIR}")
        
        sys.exit(1)


if __name__ == "__main__":
    main()
