#!/usr/bin/env python3
"""
BRAND GOVERNOR - Automated Brand Lint + Fix Pipeline
Scans pages, templates, and configs for brand drift and consistency issues.
"""

import json
import os
import re
import glob
from datetime import datetime
from pathlib import Path

# Load brand config
CONFIG_PATH = Path(__file__).parent / "brand_config.json"
with open(CONFIG_PATH) as f:
    BRAND_CONFIG = json.load(f)

# Severity levels
SEVERITY = {
    "critical": 10,
    "high": 7,
    "medium": 5,
    "low": 3,
    "info": 1
}

class BrandGovernor:
    def __init__(self):
        self.config = BRAND_CONFIG
        self.issues = []
        self.patches = []
        self.approval_required = []
        
    def scan_file(self, filepath: str) -> list:
        """Scan a single file for brand drift issues."""
        issues = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            return [{"type": "file_error", "file": filepath, "error": str(e), "severity": "info"}]
        
        # Check for wrong URLs
        issues.extend(self._check_urls(filepath, content))
        
        # Check for wrong phone numbers
        issues.extend(self._check_phones(filepath, content))
        
        # Check for forbidden phrases
        issues.extend(self._check_forbidden_phrases(filepath, content))
        
        # Check for pricing mismatches (HTML files only)
        if filepath.endswith('.html'):
            issues.extend(self._check_pricing(filepath, content))
            issues.extend(self._check_cta(filepath, content))
        
        # Check for missing legal lines (SMS templates)
        if 'prompt_variants' in filepath or 'template' in filepath.lower():
            issues.extend(self._check_legal_lines(filepath, content))
        
        return issues
    
    def _check_urls(self, filepath: str, content: str) -> list:
        """Check for outdated or incorrect URLs."""
        issues = []
        
        # Check for old v1/v2 API URLs
        old_patterns = [
            (r'empire-api-v1-orchestration', 'Old v1 API URL - should be v3'),
            (r'empire-api-v2-orchestration', 'Old v2 API URL - should be v3'),
        ]
        
        for pattern, desc in old_patterns:
            matches = re.findall(pattern, content)
            if matches:
                issues.append({
                    "type": "wrong_url",
                    "file": filepath,
                    "pattern": pattern,
                    "description": desc,
                    "severity": "critical",
                    "auto_fix": True,
                    "fix": {
                        "search": pattern.replace(r'-v1-', '-vX-').replace(r'-v2-', '-vX-'),
                        "replace": "empire-api-v3-orchestration"
                    }
                })
        
        # Check for wrong booking link
        canonical_booking = self.config["urls"]["booking_link"]
        wrong_booking_patterns = [
            r'calendly\.com',
            r'cal\.com',
            r'hubspot\.com.*meetings',
        ]
        for pattern in wrong_booking_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append({
                    "type": "wrong_url",
                    "file": filepath,
                    "pattern": pattern,
                    "description": f"Non-canonical booking URL - should be {canonical_booking}",
                    "severity": "high",
                    "auto_fix": False
                })
        
        return issues
    
    def _check_phones(self, filepath: str, content: str) -> list:
        """Check for incorrect phone numbers including forbidden patterns."""
        issues = []
        
        # Get canonical and approved phones
        canonical_e164 = self.config["contact"].get("canonical_phone_e164", "")
        canonical_display = self.config["contact"].get("canonical_phone_display", "")
        approved_phones = [
            canonical_e164,
            canonical_display,
            self.config["contact"]["phones"].get("sarah_ai", ""),
            self.config["contact"]["phones"].get("rachel_ai", ""),
            self.config["contact"]["phones"].get("christina_outbound", ""),
            self.config["contact"]["phones"].get("escalation", "")
        ]
        
        # Check for FORBIDDEN phone patterns (highest priority)
        forbidden = self.config["contact"].get("forbidden_phone_patterns", [])
        for pattern in forbidden:
            if pattern in content:
                issues.append({
                    "type": "wrong_phone",
                    "file": filepath,
                    "found": pattern,
                    "description": f"FORBIDDEN phone pattern detected - must remove",
                    "severity": "critical",
                    "auto_fix": True,
                    "fix_from": pattern,
                    "fix_to": canonical_display
                })
        
        # Find all phone-like patterns
        phone_patterns = re.findall(r'\+?1?[\s.-]?\(?([0-9]{3})\)?[\s.-]?([0-9]{3})[\s.-]?([0-9]{4})', content)
        
        for match in phone_patterns:
            found_phone = f"+1{match[0]}{match[1]}{match[2]}"
            if found_phone not in approved_phones and found_phone.replace('+1', '') not in [p.replace('+1', '') for p in approved_phones]:
                # Check if it's a test/placeholder
                if match[0] not in ['555', '123', '000', '800', '888', '877']:
                    issues.append({
                        "type": "unknown_phone",
                        "file": filepath,
                        "found": found_phone,
                        "description": f"Unknown phone number - verify if correct",
                        "severity": "high",
                        "auto_fix": False
                    })
        
        return issues
    
    def _check_forbidden_phrases(self, filepath: str, content: str) -> list:
        """Check for forbidden/discouraged phrases."""
        issues = []
        
        for phrase in self.config["voice"]["forbidden_phrases"]:
            if phrase.lower() in content.lower():
                issues.append({
                    "type": "forbidden_phrase",
                    "file": filepath,
                    "phrase": phrase,
                    "description": f"Forbidden phrase detected: '{phrase}'",
                    "severity": "medium",
                    "auto_fix": False
                })
        
        return issues
    
    def _check_pricing(self, filepath: str, content: str) -> list:
        """Check for pricing inconsistencies in HTML."""
        issues = []
        
        # Expected prices from config
        expected_prices = {tier["monthly_price"] for tier in self.config["pricing"]["tiers"] if isinstance(tier["monthly_price"], int)}
        
        # Find all dollar amounts in content
        price_matches = re.findall(r'\$(\d{2,4})(?:/mo|/month)?', content, re.IGNORECASE)
        
        for price_str in price_matches:
            price = int(price_str)
            # Skip common non-pricing numbers
            if price in [100, 500, 1000]:  # Common round numbers
                continue
            # Flag if price looks like a tier price but doesn't match
            if 200 <= price <= 1500 and price not in expected_prices:
                issues.append({
                    "type": "price_mismatch",
                    "file": filepath,
                    "found": f"${price}",
                    "expected": list(expected_prices),
                    "description": f"Price ${price} doesn't match standard tiers",
                    "severity": "high",
                    "auto_fix": False,
                    "approval_required": True
                })
        
        return issues
    
    def _check_cta(self, filepath: str, content: str) -> list:
        """Check for CTA consistency."""
        issues = []
        
        canonical_cta = self.config["offer"]["primary_cta_text"]
        canonical_url = self.config["offer"]["primary_cta_url"]
        
        # Look for CTA buttons
        cta_patterns = [
            r'<a[^>]*class="[^"]*btn[^"]*"[^>]*>([^<]+)</a>',
            r'<button[^>]*>([^<]+)</button>',
        ]
        
        for pattern in cta_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Check if CTA text is a variant but not the canonical one
                if 'diagnostic' in match.lower() or 'report' in match.lower():
                    if match.strip() != canonical_cta:
                        issues.append({
                            "type": "cta_variant",
                            "file": filepath,
                            "found": match.strip(),
                            "canonical": canonical_cta,
                            "description": "CTA text differs from canonical",
                            "severity": "low",
                            "auto_fix": False
                        })
        
        return issues
    
    def _check_legal_lines(self, filepath: str, content: str) -> list:
        """Check for required legal lines in templates."""
        issues = []
        
        required_lines = self.config["compliance"]["required_legal_lines"]
        
        for line in required_lines:
            # Search for key part of the legal line
            key_phrase = line.split()[0:3]  # First 3 words
            key_pattern = ' '.join(key_phrase)
            
            if key_pattern.lower() not in content.lower():
                issues.append({
                    "type": "missing_legal",
                    "file": filepath,
                    "required": line,
                    "description": f"Missing required legal line",
                    "severity": "high",
                    "auto_fix": False
                })
        
        return issues
    
    def scan_all(self, base_dir: str = None) -> dict:
        """Scan all target files (PUBLIC scope only)."""
        if base_dir is None:
            base_dir = Path(__file__).parent
        
        base_dir = Path(base_dir)
        all_issues = []
        files_scanned = 0
        scanned_files = set()
        
        # Get scope from config
        scan_scope = self.config.get("brand_lint", {}).get("scan_scope", {})
        include_patterns = scan_scope.get("include", ["public/*.html", "public/audits/*.html"])
        exclude_patterns = scan_scope.get("exclude", ["backups/**", "node_modules/**", ".git/**"])
        
        # Helper to check if file should be excluded
        def should_exclude(fpath):
            fpath_str = str(fpath).replace("\\", "/")
            for excl in exclude_patterns:
                # Simple pattern matching
                if excl.startswith("*") and fpath_str.endswith(excl[1:]):
                    return True
                if excl.endswith("**") and excl[:-2].replace("*", "") in fpath_str:
                    return True
                if excl in fpath_str:
                    return True
            return False
        
        # Scan ONLY the include patterns (no extra patterns)
        for pattern in include_patterns:
            for filepath in glob.glob(str(base_dir / pattern), recursive=True):
                if should_exclude(filepath):
                    continue
                if filepath in scanned_files:
                    continue
                scanned_files.add(filepath)
                files_scanned += 1
                issues = self.scan_file(filepath)
                all_issues.extend(issues)
        
        # Categorize issues
        auto_fix = [i for i in all_issues if i.get("auto_fix")]
        needs_approval = [i for i in all_issues if i.get("approval_required")]
        informational = [i for i in all_issues if not i.get("auto_fix") and not i.get("approval_required")]
        
        # Calculate severity score
        severity_score = sum(SEVERITY.get(i.get("severity", "info"), 1) for i in all_issues)
        
        return {
            "scan_time": datetime.utcnow().isoformat(),
            "files_scanned": files_scanned,
            "total_issues": len(all_issues),
            "severity_score": severity_score,
            "auto_fixable": len(auto_fix),
            "needs_approval": len(needs_approval),
            "informational": len(informational),
            "issues": all_issues,
            "summary": self._generate_summary(all_issues)
        }
    
    def _generate_summary(self, issues: list) -> str:
        """Generate a human-readable summary."""
        if not issues:
            return "✅ No brand drift detected. All files are consistent."
        
        summary_lines = [
            f"⚠️ Found {len(issues)} brand consistency issues:",
            ""
        ]
        
        by_type = {}
        for issue in issues:
            t = issue.get("type", "other")
            by_type[t] = by_type.get(t, 0) + 1
        
        for issue_type, count in sorted(by_type.items(), key=lambda x: -x[1]):
            summary_lines.append(f"  • {issue_type}: {count}")
        
        return '\n'.join(summary_lines)
    
    def apply_auto_fixes(self, scan_result: dict, dry_run: bool = True) -> dict:
        """Apply auto-fixable patches."""
        fixes_applied = []
        
        for issue in scan_result.get("issues", []):
            if not issue.get("auto_fix"):
                continue
            
            fix = issue.get("fix", {})
            if not fix:
                continue
            
            filepath = issue["file"]
            search = fix.get("search")
            replace = fix.get("replace")
            
            if not search or not replace:
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = re.sub(search, replace, content)
                
                if new_content != content:
                    if not dry_run:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                    
                    fixes_applied.append({
                        "file": filepath,
                        "search": search,
                        "replace": replace,
                        "applied": not dry_run
                    })
            except Exception as e:
                fixes_applied.append({
                    "file": filepath,
                    "error": str(e),
                    "applied": False
                })
        
        return {
            "dry_run": dry_run,
            "fixes_proposed": len(fixes_applied),
            "fixes": fixes_applied
        }


def main():
    """Run brand governor scan."""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Brand Governor - Lint & Fix")
    parser.add_argument("--fix", action="store_true", help="Apply auto-fixes")
    parser.add_argument("--dir", default=".", help="Base directory to scan")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--report", default=None, help="Write JSON report to file")
    args = parser.parse_args()
    
    governor = BrandGovernor()
    result = governor.scan_all(args.dir)
    
    # Get severity budget
    severity_budget = BRAND_CONFIG.get("brand_lint", {}).get("severity_budget", {})
    max_score = severity_budget.get("max_public_score", 50)
    fail_on_exceed = severity_budget.get("fail_on_exceed", True)
    
    # Check if we exceed budget
    exceeds_budget = result['severity_score'] > max_score
    
    if args.report:
        with open(args.report, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Report written to {args.report}")
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*60}")
        print("BRAND GOVERNOR SCAN REPORT")
        print(f"{'='*60}")
        print(f"Scanned: {result['files_scanned']} files (PUBLIC scope only)")
        print(f"Issues: {result['total_issues']} (severity score: {result['severity_score']})")
        print(f"Severity Budget: {max_score} (current: {result['severity_score']})")
        if exceeds_budget:
            print(f"⚠️  BUDGET EXCEEDED - score {result['severity_score']} > {max_score}")
        else:
            print(f"✅ Within budget")
        print(f"Auto-fixable: {result['auto_fixable']}")
        print(f"Needs approval: {result['needs_approval']}")
        print(f"\n{result['summary']}")
        print(f"{'='*60}\n")
        
        if args.fix:
            fix_result = governor.apply_auto_fixes(result, dry_run=False)
            print(f"Applied {fix_result['fixes_proposed']} fixes")
        elif result['auto_fixable'] > 0:
            print(f"Run with --fix to apply {result['auto_fixable']} auto-fixes")
    
    # Exit with code 1 if exceeds budget and fail_on_exceed is true
    if exceeds_budget and fail_on_exceed:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
