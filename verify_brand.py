#!/usr/bin/env python3
"""
verify_brand.py - Brand Governor for phone number enforcement

Scans public/ directory for phone numbers that don't match canonical values.
Can auto-fix violations with --fix flag.

Usage:
  python verify_brand.py --dir public           # Check only
  python verify_brand.py --dir public --fix     # Auto-fix violations
  python verify_brand.py --dir public --strict  # Fail on any warning
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Load brand config
SCRIPT_DIR = Path(__file__).parent
CONFIG_PATH = SCRIPT_DIR / "brand_config.json"

def load_config():
    if CONFIG_PATH.exists():
        return json.load(open(CONFIG_PATH))
    return {
        "canonical_numbers": {
            "voice": {"e164": "+18632132505", "display": "(863) 213-2505"},
            "sms": {"e164": "+13527585336", "display": "(352) 758-5336"}
        }
    }

CONFIG = load_config()

# Canonical patterns that ARE allowed
CANONICAL_VOICE = CONFIG["canonical_numbers"]["voice"]["display"]
CANONICAL_SMS = CONFIG["canonical_numbers"]["sms"]["display"]
CANONICAL_VOICE_E164 = CONFIG["canonical_numbers"]["voice"]["e164"]
CANONICAL_SMS_E164 = CONFIG["canonical_numbers"]["sms"]["e164"]

# Patterns to find any phone number
PHONE_PATTERN = re.compile(
    r'(\+?1?[\s\-\.]?\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4})',
    re.IGNORECASE
)

# Allowed number patterns (normalized)
ALLOWED_NUMBERS = {
    "8632132505",  # Voice
    "3527585336",  # SMS
    "3529368152",  # Escalation
}

def normalize_phone(phone):
    """Extract just digits from phone number."""
    return ''.join(c for c in phone if c.isdigit())[-10:]

def is_canonical(phone):
    """Check if phone matches a canonical number."""
    normalized = normalize_phone(phone)
    return normalized in ALLOWED_NUMBERS

def scan_file(filepath, fix=False):
    """Scan a single file for phone number violations."""
    violations = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return [f"ERROR reading {filepath}: {e}"]
    
    original_content = content
    matches = PHONE_PATTERN.findall(content)
    
    for match in matches:
        if not is_canonical(match):
            # Determine correct replacement
            normalized = normalize_phone(match)
            
            # Check if it looks like a voice number (863 area) but wrong
            if normalized.startswith("863") and normalized != "8632132505":
                replacement = CANONICAL_VOICE
                violations.append(f"VIOLATION in {filepath}: {match} → should be {replacement}")
            # Check if it looks like SMS number (352 area) but wrong  
            elif normalized.startswith("352") and normalized != "3527585336" and normalized != "3529368152":
                replacement = CANONICAL_SMS
                violations.append(f"VIOLATION in {filepath}: {match} → should be {replacement}")
            # Unknown number - flag but don't auto-fix
            elif len(normalized) == 10:
                violations.append(f"WARNING in {filepath}: Unknown phone {match} - manual review needed")
                replacement = None
            else:
                continue
            
            if fix and replacement:
                content = content.replace(match, replacement)
    
    # Write fixed content
    if fix and content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        violations.append(f"FIXED: {filepath}")
    
    return violations

def scan_directory(directory, fix=False, extensions=None):
    """Scan directory for phone number violations."""
    if extensions is None:
        extensions = ['.html', '.js', '.css', '.md', '.json']
    
    all_violations = []
    scanned = 0
    
    for root, dirs, files in os.walk(directory):
        # Skip node_modules, .git, etc.
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                filepath = os.path.join(root, file)
                violations = scan_file(filepath, fix)
                all_violations.extend(violations)
                scanned += 1
    
    return all_violations, scanned

def main():
    parser = argparse.ArgumentParser(description="Brand Governor - Phone Number Enforcement")
    parser.add_argument("--dir", required=True, help="Directory to scan")
    parser.add_argument("--fix", action="store_true", help="Auto-fix violations")
    parser.add_argument("--strict", action="store_true", help="Fail on any warning")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.dir):
        print(f"ERROR: {args.dir} is not a valid directory")
        sys.exit(1)
    
    violations, scanned = scan_directory(args.dir, args.fix)
    
    errors = [v for v in violations if v.startswith("VIOLATION") or v.startswith("ERROR")]
    warnings = [v for v in violations if v.startswith("WARNING")]
    fixes = [v for v in violations if v.startswith("FIXED")]
    
    if args.json:
        result = {
            "scanned": scanned,
            "errors": len(errors),
            "warnings": len(warnings),
            "fixes": len(fixes),
            "violations": violations,
            "passed": len(errors) == 0 and (not args.strict or len(warnings) == 0)
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"BRAND GOVERNOR SCAN RESULTS")
        print(f"{'='*60}")
        print(f"Directory: {args.dir}")
        print(f"Files scanned: {scanned}")
        print(f"Errors: {len(errors)}")
        print(f"Warnings: {len(warnings)}")
        if args.fix:
            print(f"Fixed: {len(fixes)}")
        print()
        
        for v in violations:
            print(v)
        
        print()
        if len(errors) == 0 and (not args.strict or len(warnings) == 0):
            print("✅ PASSED - All phone numbers are canonical")
            sys.exit(0)
        else:
            print("❌ FAILED - Phone number violations detected")
            sys.exit(1)

if __name__ == "__main__":
    main()
