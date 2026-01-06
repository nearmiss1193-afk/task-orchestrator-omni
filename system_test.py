#!/usr/bin/env python3
"""
SOVEREIGN SYSTEM TEST SUITE
Comprehensive testing tool for the Empire Unified system.
Tests all channels: SMS, Email, Voice, Dashboard API, and integrations.

Usage: python system_test.py [--full|--quick|--voice|--sms|--email|--api]
"""

import os
import sys
import json
import time
import urllib.request
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except: pass

# Terminal colors
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title):
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {title}{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")

def print_test(name, status, details=""):
    icon = f"{Colors.GREEN}✅{Colors.END}" if status else f"{Colors.RED}❌{Colors.END}"
    print(f"  {icon} {name}")
    if details:
        print(f"      {Colors.YELLOW}→ {details}{Colors.END}")

def print_warn(msg):
    print(f"  {Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg):
    print(f"  {Colors.BLUE}ℹ️  {msg}{Colors.END}")

# ==================== TESTS ====================

def test_env_vars():
    """Test that all required environment variables are set"""
    print_header("ENVIRONMENT VARIABLES")
    
    required = [
        ("VAPI_PRIVATE_KEY", "Vapi API access"),
        ("ANTHROPIC_API_KEY", "Claude AI"),
        ("GEMINI_API_KEY", "Gemini AI fallback"),
        ("GHL_API_KEY", "GoHighLevel CRM"),
        ("RESEND_API_KEY", "Email delivery"),
    ]
    
    optional = [
        ("VAPI_PHONE_ID", "Outbound call phone"),
        ("TURSO_DATABASE_URL", "Database connection"),
        ("VERCEL_URL", "Deployment URL"),
    ]
    
    all_ok = True
    for var, desc in required:
        value = os.environ.get(var, "")
        if value:
            masked = value[:8] + "..." if len(value) > 8 else value
            print_test(f"{var}: {masked}", True, desc)
        else:
            print_test(f"{var} (MISSING)", False, desc)
            all_ok = False
    
    print()
    print_info("Optional Variables:")
    for var, desc in optional:
        value = os.environ.get(var, "")
        if value:
            masked = value[:8] + "..." if len(value) > 8 else value
            print_test(f"{var}: {masked}", True, desc)
        else:
            print_warn(f"{var} not set ({desc})")
    
    return all_ok


def test_vapi_connection():
    """Test Vapi API connection and list assistants"""
    print_header("VAPI CONNECTION TEST")
    
    VAPI_KEY = os.environ.get("VAPI_PRIVATE_KEY", "")
    if not VAPI_KEY:
        print_test("Vapi API Key", False, "VAPI_PRIVATE_KEY not set")
        return False
    
    try:
        req = urllib.request.Request(
            "https://api.vapi.ai/assistant",
            headers={
                "Authorization": f"Bearer {VAPI_KEY}",
                "Content-Type": "application/json"
            }
        )
        
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            
            print_test("Vapi API Connection", True)
            print_info(f"Found {len(data)} assistant(s):")
            
            for asst in data[:5]:  # Show first 5
                name = asst.get('name', 'Unknown')
                asst_id = asst.get('id', '')[:12]
                print(f"      • {name} ({asst_id}...)")
            
            return True
            
    except Exception as e:
        print_test("Vapi API Connection", False, str(e)[:50])
        return False


def test_claude_api():
    """Test Claude API connection"""
    print_header("CLAUDE AI TEST")
    
    ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    if not ANTHROPIC_KEY:
        print_test("Claude API Key", False, "ANTHROPIC_API_KEY not set")
        return False
    
    try:
        payload = json.dumps({
            "model": "claude-3-haiku-20240307",
            "max_tokens": 50,
            "messages": [{"role": "user", "content": "Say 'System Online' in 3 words max."}]
        }).encode('utf-8')
        
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'x-api-key': ANTHROPIC_KEY,
                'anthropic-version': '2023-06-01'
            }
        )
        
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            response = data.get('content', [{}])[0].get('text', '')
            print_test("Claude API Connection", True, f'Response: "{response}"')
            return True
            
    except Exception as e:
        print_test("Claude API Connection", False, str(e)[:50])
        return False


def test_gemini_api():
    """Test Gemini API connection"""
    print_header("GEMINI AI TEST")
    
    GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
    if not GEMINI_KEY:
        print_test("Gemini API Key", False, "GEMINI_API_KEY not set")
        return False
    
    try:
        payload = json.dumps({
            "contents": [{"parts": [{"text": "Say 'Fallback Online' in 3 words max."}]}]
        }).encode('utf-8')
        
        req = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}",
            data=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            response = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            print_test("Gemini API Connection", True, f'Response: "{response[:30]}..."')
            return True
            
    except Exception as e:
        print_test("Gemini API Connection", False, str(e)[:50])
        return False


def test_dashboard_api():
    """Test dashboard API endpoint"""
    print_header("DASHBOARD API TEST")
    
    api_url = "https://empire-sovereign-cloud.vercel.app/api/chat"
    
    try:
        payload = json.dumps({
            "command": "status report"
        }).encode('utf-8')
        
        req = urllib.request.Request(
            api_url,
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            response = data.get('response', 'No response')
            print_test("Dashboard API Connection", True)
            print_info(f'Response: "{response[:80]}..."')
            return True
            
    except Exception as e:
        print_test("Dashboard API Connection", False, str(e)[:50])
        return False


def test_resend_api():
    """Test Resend email API connection"""
    print_header("RESEND EMAIL TEST")
    
    RESEND_KEY = os.environ.get("RESEND_API_KEY", "")
    if not RESEND_KEY:
        print_test("Resend API Key", False, "RESEND_API_KEY not set")
        return False
    
    try:
        # Just verify the API key by checking domains
        req = urllib.request.Request(
            "https://api.resend.com/domains",
            headers={
                "Authorization": f"Bearer {RESEND_KEY}",
                "Content-Type": "application/json"
            }
        )
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            domains = data.get('data', [])
            print_test("Resend API Connection", True)
            if domains:
                for d in domains[:3]:
                    print_info(f"Domain: {d.get('name')} ({d.get('status')})")
            return True
            
    except Exception as e:
        print_test("Resend API Connection", False, str(e)[:50])
        return False


def test_ghl_api():
    """Test GoHighLevel API connection"""
    print_header("GOHIGHLEVEL CRM TEST")
    
    GHL_KEY = os.environ.get("GHL_API_KEY", "")
    if not GHL_KEY:
        print_test("GHL API Key", False, "GHL_API_KEY not set")
        return False
    
    try:
        req = urllib.request.Request(
            "https://rest.gohighlevel.com/v1/contacts/?limit=1",
            headers={
                "Authorization": f"Bearer {GHL_KEY}",
                "Content-Type": "application/json"
            }
        )
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            contacts = data.get('contacts', [])
            print_test("GHL API Connection", True)
            print_info(f"Found contacts in location")
            return True
            
    except Exception as e:
        print_test("GHL API Connection", False, str(e)[:50])
        return False


def run_full_suite():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║       SOVEREIGN SYSTEM TEST SUITE - FULL DIAGNOSTIC       ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Run all tests
    results['env'] = test_env_vars()
    results['vapi'] = test_vapi_connection()
    results['claude'] = test_claude_api()
    results['gemini'] = test_gemini_api()
    results['dashboard'] = test_dashboard_api()
    results['resend'] = test_resend_api()
    results['ghl'] = test_ghl_api()
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, status in results.items():
        icon = f"{Colors.GREEN}PASS{Colors.END}" if status else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {name.upper():12} [{icon}]")
    
    print()
    pct = (passed / total) * 100
    color = Colors.GREEN if pct >= 80 else Colors.YELLOW if pct >= 50 else Colors.RED
    print(f"  {color}{Colors.BOLD}Overall: {passed}/{total} tests passed ({pct:.0f}%){Colors.END}")
    
    if pct == 100:
        print(f"\n  {Colors.GREEN}{Colors.BOLD}🎉 ALL SYSTEMS OPERATIONAL!{Colors.END}")
    elif pct >= 70:
        print(f"\n  {Colors.YELLOW}⚠️  Some systems need attention.{Colors.END}")
    else:
        print(f"\n  {Colors.RED}🔴 Critical issues detected!{Colors.END}")
    
    return results


if __name__ == "__main__":
    args = sys.argv[1:] if len(sys.argv) > 1 else ['--full']
    
    if '--full' in args or len(args) == 0:
        run_full_suite()
    elif '--env' in args:
        test_env_vars()
    elif '--vapi' in args or '--voice' in args:
        test_vapi_connection()
    elif '--claude' in args:
        test_claude_api()
    elif '--gemini' in args:
        test_gemini_api()
    elif '--api' in args:
        test_dashboard_api()
    elif '--email' in args:
        test_resend_api()
    elif '--ghl' in args:
        test_ghl_api()
    else:
        print("Usage: python system_test.py [--full|--env|--vapi|--claude|--gemini|--api|--email|--ghl]")
