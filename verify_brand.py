#!/usr/bin/env python3
"""
verify_brand.py - Brand Governor for phone number enforcement

Scans public/ directory for phone numbers that don't match canonical values.
Outputs brand_audit_report.json with issues and line numbers.
Supports --fix to auto-fix violations.

Usage:
  python verify_brand.py --dir public                    # Check only
  python verify_brand.py --dir public --fix              # Auto-fix violations
  python verify_brand.py --dir public --strict           # Fail on any warning
  python verify_brand.py --dir public --report           # Output JSON report
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

# Load brand config
SCRIPT_DIR = Path(__file__).parent
CONFIG_PATH = SCRIPT_DIR / "brand_config.json"
REPORT_PATH = SCRIPT_DIR / "brand_audit_report.json"

def load_config():
    if CONFIG_PATH.exists():
        return json.load(open(CONFIG_PATH))
    # Fallback defaults
    return {
        "canonical_numbers": {
            "voice": {"e164": "+18632132505", "display": "(863) 213-2505"},
            "sms": {"e164": "+13527585336", "display": "(352) 758-5336"}
        },
        "forbidden_patterns": ["863-337-3705", "8633373705"],
        "allowed_numbers_e164": ["+18632132505", "+13527585336", "+13529368152"]
    }

CONFIG = load_config()

# Extract canonical info
VOICE_DISPLAY = CONFIG["canonical_numbers"]["voice"]["display"]
VOICE_E164 = CONFIG["canonical_numbers"]["voice"]["e164"]
SMS_DISPLAY = CONFIG["canonical_numbers"]["sms"]["display"]
SMS_E164 = CONFIG["canonical_numbers"]["sms"]["e164"]

# Build allowed digits set
ALLOWED_DIGITS = set()
for num in CONFIG.get("allowed_numbers_e164", []):
    digits = ''.join(c for c in num if c.isdigit())[-10:]
    ALLOWED_DIGITS.add(digits)

# Forbidden patterns
FORBIDDEN = set(CONFIG.get("forbidden_patterns", []))

# Regex to find phone-like strings
PHONE_PATTERN = re.compile(
    r'(\+?1?[\s\-\.]?\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4})',
    re.IGNORECASE
)

def normalize_phone(phone):
    """Extract just digits from phone number, return last 10."""
    return ''.join(c for c in phone if c.isdigit())[-10:]

def is_allowed(phone):
    """Check if phone matches an allowed number."""
    normalized = normalize_phone(phone)
    if normalized in ALLOWED_DIGITS:
        return True
    # Also check if it's a forbidden pattern
    for forbidden in FORBIDDEN:
        if normalize_phone(forbidden) == normalized:
            return False
    return len(normalized) < 10  # Ignore short numbers

def get_replacement(phone):
    """Determine correct replacement for a wrong number."""
    normalized = normalize_phone(phone)
    
    # If starts with 863, replace with voice
    if normalized.startswith("863"):
        return VOICE_DISPLAY
    # If starts with 352, replace with SMS
    if normalized.startswith("352"):
        return SMS_DISPLAY
    return None

def scan_file(filepath, fix=False):
    """Scan a single file for phone number violations."""
    issues = []
    fixed_count = 0
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        return [{"file": str(filepath), "line": 0, "type": "error", "message": str(e)}], 0
    
    original_content = ''.join(lines)
    new_lines = []
    
    for line_num, line in enumerate(lines, 1):
        matches = PHONE_PATTERN.findall(line)
        new_line = line
        
        for match in matches:
            normalized = normalize_phone(match)
            
            # Skip if allowed
            if normalized in ALLOWED_DIGITS:
                continue
            
            # Skip short numbers
            if len(normalized) < 10:
                continue
            
            # Check forbidden
            is_forbidden = any(normalize_phone(f) == normalized for f in FORBIDDEN)
            
            replacement = get_replacement(match)
            
            if is_forbidden or not is_allowed(match):
                issue = {
                    "file": str(filepath),
                    "line": line_num,
                    "found": match,
                    "type": "violation" if is_forbidden else "unknown",
                    "replacement": replacement,
                    "context": line.strip()[:80]
                }
                issues.append(issue)
                
                if fix and replacement:
                    new_line = new_line.replace(match, replacement)
                    fixed_count += 1
        
        new_lines.append(new_line)
    
    # Write fixed content
    if fix and fixed_count > 0:
        new_content = ''.join(new_lines)
        if new_content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
    
    return issues, fixed_count

def scan_directory(directory, fix=False, extensions=None):
    """Scan directory for phone number violations."""
    if extensions is None:
        extensions = ['.html', '.htm', '.js', '.css', '.md', '.json', '.txt']
    
    all_issues = []
    total_fixed = 0
    scanned = 0
    
    # Specific paths to scan
    scan_paths = [
        os.path.join(directory, "*.html"),
        os.path.join(directory, "audits", "*.html"),
        os.path.join(directory, "assets", "*.html"),
    ]
    
    for root, dirs, files in os.walk(directory):
        # Skip non-public dirs
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                filepath = os.path.join(root, file)
                issues, fixed = scan_file(filepath, fix)
                all_issues.extend(issues)
                total_fixed += fixed
                scanned += 1
    
    return all_issues, scanned, total_fixed

def main():
    parser = argparse.ArgumentParser(description="Brand Governor - Phone Number Enforcement")
    parser.add_argument("--dir", required=True, help="Directory to scan")
    parser.add_argument("--fix", action="store_true", help="Auto-fix violations")
    parser.add_argument("--strict", action="store_true", help="Fail on any issue")
    parser.add_argument("--report", action="store_true", help="Output JSON report")
    parser.add_argument("--json", action="store_true", help="JSON output to stdout")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.dir):
        print(f"ERROR: {args.dir} is not a valid directory")
        sys.exit(1)
    
    issues, scanned, fixed = scan_directory(args.dir, args.fix)
    
    violations = [i for i in issues if i.get("type") == "violation"]
    unknowns = [i for i in issues if i.get("type") == "unknown"]
    errors = [i for i in issues if i.get("type") == "error"]
    
    passed = len(violations) == 0 and len(errors) == 0
    if args.strict:
        passed = passed and len(unknowns) == 0
    
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "directory": args.dir,
        "files_scanned": scanned,
        "violations": len(violations),
        "unknowns": len(unknowns),
        "errors": len(errors),
        "fixed": fixed,
        "passed": passed,
        "issues": issues,
        "canonical": {
            "voice": {"display": VOICE_DISPLAY, "e164": VOICE_E164},
            "sms": {"display": SMS_DISPLAY, "e164": SMS_E164}
        }
    }
    
    # Save report
    if args.report or args.json:
        with open(REPORT_PATH, 'w') as f:
            json.dump(report, f, indent=2)
    
    # Output
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"BRAND GOVERNOR AUDIT REPORT")
        print(f"{'='*60}")
        print(f"Directory: {args.dir}")
        print(f"Files scanned: {scanned}")
        print(f"Violations: {len(violations)}")
        print(f"Unknowns: {len(unknowns)}")
        print(f"Errors: {len(errors)}")
        if args.fix:
            print(f"Fixed: {fixed}")
        print()
        
        for issue in issues:
            severity = "❌" if issue.get("type") == "violation" else "⚠️" if issue.get("type") == "unknown" else "🔴"
            print(f"{severity} {issue['file']}:{issue.get('line', '?')} - {issue.get('found', issue.get('message', 'unknown'))}")
            if issue.get('replacement'):
                print(f"   → Replace with: {issue['replacement']}")
        
        print()
        if passed:
            print("✅ PASSED - All phone numbers are canonical")
        else:
            print("❌ FAILED - Phone number violations detected")
    
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
