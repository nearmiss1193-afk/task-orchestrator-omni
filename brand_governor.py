#!/usr/bin/env python3
"""
BRAND GOVERNOR - Public Web Truth Scanner
Scans ONLY publicly served files for brand drift and phone number violations.
"""

import json
import os
import re
import sys
import glob
import fnmatch
from pathlib import Path
from datetime import datetime, timezone

# Load brand config
CONFIG_PATH = Path(__file__).parent / "brand_config.json"
with open(CONFIG_PATH) as f:
    BRAND_CONFIG = json.load(f)

# Default scan patterns
DEFAULT_INCLUDES = ["public/*.html", "public/audits/*.html"]
DEFAULT_EXCLUDES = [
    "node_modules", ".git", "backups", "manifests", "runbooks",
    "sql", "directives", "execution", "old", "backup"
]

# Severity values
SEVERITY_VALUES = {"critical": 10, "high": 7, "medium": 5, "low": 3, "info": 1}


def normalize_phone(phone: str) -> str:
    """Normalize phone to digits only for comparison."""
    return re.sub(r'\D', '', phone)


def find_phones_with_lines(content: str) -> list:
    """Find all phone-like patterns with line numbers."""
    patterns = [
        r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',      # (123) 456-7890
        r'\d{3}[-.\s]\d{3}[-.\s]\d{4}',      # 123-456-7890
        r'\+1\s*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # +1 (123) 456-7890
        r'\+1\d{10}',                         # +11234567890
        r'(?<!\d)\d{10}(?!\d)',               # 1234567890
    ]
    
    results = []
    lines = content.split('\n')
    for line_num, line in enumerate(lines, 1):
        for pattern in patterns:
            for match in re.finditer(pattern, line):
                results.append({
                    "line": line_num,
                    "match": match.group(),
                    "normalized": normalize_phone(match.group())
                })
    return results


def should_exclude(filepath: str, excludes: list) -> bool:
    """Check if filepath should be excluded."""
    filepath_normalized = filepath.replace("\\", "/").lower()
    for excl in excludes:
        if excl.lower() in filepath_normalized:
            return True
    return False


def scan_file(filepath: str, config: dict) -> list:
    """Scan a single file for brand issues."""
    issues = []
    
    # Skip binary files
    if any(filepath.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.ico', '.webp', '.svg', '.woff', '.woff2', '.ttf', '.eot']):
        return []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return [{
            "type": "read_error",
            "severity": 2,
            "file": filepath,
            "line": 0,
            "match": str(e)
        }]
    
    # Get canonical phones
    contact = config.get("contact", {})
    canonical_e164 = contact.get("canonical_phone_e164", "")
    canonical_display = contact.get("canonical_phone_display", "")
    canonical_normalized = normalize_phone(canonical_e164)
    forbidden_patterns = contact.get("forbidden_phone_patterns", [])
    
    # Check for forbidden phone patterns
    lines = content.split('\n')
    for line_num, line in enumerate(lines, 1):
        for forbidden in forbidden_patterns:
            if forbidden in line:
                issues.append({
                    "type": "wrong_phone",
                    "severity": 10,
                    "file": filepath,
                    "line": line_num,
                    "match": forbidden
                })
    
    # Find all phone-like patterns and check if canonical
    phones = find_phones_with_lines(content)
    for phone in phones:
        # Skip if it matches canonical
        if phone["normalized"] == canonical_normalized:
            continue
        if phone["match"] == canonical_display:
            continue
        # Skip if already flagged as forbidden
        if any(phone["match"] in f for f in forbidden_patterns):
            continue
        # Skip test/toll-free numbers
        normalized = phone["normalized"]
        # Get area code (handle both 10-digit and 11-digit with country code)
        if len(normalized) == 11 and normalized.startswith('1'):
            area_code = normalized[1:4]
        elif len(normalized) >= 10:
            area_code = normalized[:3]
        else:
            area_code = ""
        if area_code in ['555', '123', '000', '800', '888', '877', '866', '855', '844']:
            continue
        # Skip escalation number
        escalation = normalize_phone(contact.get("phones", {}).get("escalation", ""))
        if phone["normalized"] == escalation or phone["normalized"] == escalation[1:]:
            continue
        
        issues.append({
            "type": "unknown_phone",
            "severity": 1 if "/audits/" in filepath.replace("\\", "/") else 10,  # Low severity for audit pages (business data)
            "file": filepath,
            "line": phone["line"],
            "match": phone["match"]
        })
    
    # Offer Governance Checks (only for main public HTML, not audits)
    if filepath.endswith('.html') and "/audits/" not in filepath.replace("\\", "/"):
        issues.extend(check_offer_governance(filepath, content, config))
    
    return issues


def check_offer_governance(filepath: str, content: str, config: dict) -> list:
    """Check for offer/CTA/pricing drift."""
    issues = []
    offer_gov = config.get("offer_governance", {})
    
    if not offer_gov:
        return issues
    
    lines = content.split('\n')
    
    # 1. Check for forbidden offer phrases
    forbidden_phrases = offer_gov.get("forbidden_offer_phrases", [])
    for line_num, line in enumerate(lines, 1):
        line_lower = line.lower()
        for phrase in forbidden_phrases:
            if phrase.lower() in line_lower:
                issues.append({
                    "type": "forbidden_phrase",
                    "severity": 10,
                    "file": filepath,
                    "line": line_num,
                    "match": phrase,
                    "auto_fix": False
                })
    
    # 2. Check CTA button text (look for common button patterns)
    allowed_cta_texts = offer_gov.get("allowed_cta_texts", [])
    # Find button/a elements with text
    import re
    button_pattern = re.compile(r'<(?:button|a)[^>]*>([^<]+)</(?:button|a)>', re.IGNORECASE)
    for line_num, line in enumerate(lines, 1):
        for match in button_pattern.finditer(line):
            button_text = match.group(1).strip()
            # Skip very short or obviously non-CTA text
            if len(button_text) < 3 or button_text in ['X', '×', '←', '→', '↻']:
                continue
            # Check if it's an allowed CTA
            if button_text not in allowed_cta_texts and not any(allowed in button_text for allowed in allowed_cta_texts):
                # Only flag if it looks like a CTA (has action words)
                action_words = ['get', 'book', 'start', 'call', 'schedule', 'sign', 'join', 'try', 'free', 'demo']
                if any(word in button_text.lower() for word in action_words):
                    issues.append({
                        "type": "cta_text_drift",
                        "severity": 6,
                        "file": filepath,
                        "line": line_num,
                        "match": button_text,
                        "auto_fix": button_text in offer_gov.get("old_cta_replacements", {})
                    })
    
    # 3. Check CTA hrefs
    allowed_prefixes = offer_gov.get("allowed_cta_href_prefixes", [])
    href_pattern = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)
    for line_num, line in enumerate(lines, 1):
        for match in href_pattern.finditer(line):
            href = match.group(1)
            # Skip internal links, anchors, javascript
            if href.startswith('#') or href.startswith('javascript:') or href.startswith('/'):
                continue
            # Check if it matches allowed prefixes
            if not any(href.startswith(prefix) for prefix in allowed_prefixes):
                # Check if it's a booking/CTA link (not just any external link)
                if 'calendly' in href.lower() or 'booking' in href.lower() or 'schedule' in href.lower():
                    issues.append({
                        "type": "cta_link_drift",
                        "severity": 8,
                        "file": filepath,
                        "line": line_num,
                        "match": href,
                        "auto_fix": any(old in href for old in offer_gov.get("old_href_replacements", {}).keys())
                    })
    
    return issues


def scan_all(base_dir: str, includes: list, excludes: list, config: dict) -> dict:
    """Scan all matching files."""
    base_path = Path(base_dir)
    all_issues = []
    scanned_files = set()
    
    for pattern in includes:
        # Handle glob
        for filepath in glob.glob(str(base_path / pattern), recursive=True):
            if should_exclude(filepath, excludes):
                continue
            if filepath in scanned_files:
                continue
            scanned_files.add(filepath)
            issues = scan_file(filepath, config)
            all_issues.extend(issues)
    
    # Calculate severity score
    severity_score = sum(i.get("severity", 1) for i in all_issues)
    
    # Count by type
    type_counts = {}
    for i in all_issues:
        t = i.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
    
    # Top files by severity
    file_severity = {}
    for i in all_issues:
        f = i.get("file", "")
        file_severity[f] = file_severity.get(f, 0) + i.get("severity", 1)
    top_files = sorted(file_severity.items(), key=lambda x: -x[1])[:10]
    
    return {
        "scan_time": datetime.now(timezone.utc).isoformat(),
        "scanned": len(scanned_files),
        "severity_score": severity_score,
        "total_issues": len(all_issues),
        "top_issue_types": sorted(type_counts.items(), key=lambda x: -x[1])[:5],
        "top_files_by_severity": top_files,
        "issues": all_issues
    }


def print_summary(result: dict):
    """Print human-readable summary."""
    print(f"\n{'='*60}")
    print("BRAND GOVERNOR - PUBLIC WEB TRUTH SCAN")
    print(f"{'='*60}")
    print(f"Scanned: {result['scanned']} files")
    print(f"Total Issues: {result['total_issues']}")
    print(f"Severity Score: {result['severity_score']}")
    print(f"\nTop Issue Types:")
    for t, c in result.get('top_issue_types', []):
        print(f"  • {t}: {c}")
    print(f"\nTop Files by Severity:")
    for f, s in result.get('top_files_by_severity', []):
        fname = Path(f).name
        print(f"  • {fname}: {s}")
    print(f"{'='*60}")
    
    # Budget check
    budget = BRAND_CONFIG.get("brand_lint", {}).get("severity_budget", {})
    max_score = budget.get("max_public_score", 50)
    if result['severity_score'] > max_score:
        print(f"⚠️  FAIL: Severity {result['severity_score']} > budget {max_score}")
    else:
        print(f"✅ PASS: Severity {result['severity_score']} <= budget {max_score}")
    print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Brand Governor - Public Web Truth Scanner")
    parser.add_argument("--dir", default=".", help="Base directory to scan")
    parser.add_argument("--include", default=None, help="Comma-separated include patterns")
    parser.add_argument("--exclude", default=None, help="Comma-separated exclude patterns")
    parser.add_argument("--json", action="store_true", help="Output JSON to stdout")
    args = parser.parse_args()
    
    # Parse patterns
    includes = args.include.split(",") if args.include else DEFAULT_INCLUDES
    excludes = args.exclude.split(",") if args.exclude else DEFAULT_EXCLUDES
    
    # Run scan
    result = scan_all(args.dir, includes, excludes, BRAND_CONFIG)
    
    # Always write JSON report
    report_path = Path(args.dir) / "brand_audit_report.json"
    with open(report_path, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print_summary(result)
        print(f"Report written to: {report_path}")
    
    # Exit code based on severity budget
    budget = BRAND_CONFIG.get("brand_lint", {}).get("severity_budget", {})
    max_score = budget.get("max_public_score", 50)
    if result['severity_score'] > max_score:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
