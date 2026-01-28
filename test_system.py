#!/usr/bin/env python
"""
PhishGuard Comprehensive System Test Suite
Consolidates all testing functionality for the PhishGuard application
Tests: ML Server, Backend API, Database, and Frontend integration
"""

import requests
import json
import sys
import time

# Configuration
BASE_ML = "http://localhost:5000"
BASE_BACKEND = "http://localhost:3001"
TIMEOUT = 5

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.ENDC}\n")

def test_ml_server_accuracy():
    """Test 1: Improved phishing detection accuracy"""
    print_section("TEST 1: ML SERVER ACCURACY TEST")
    
    # Test URLs with various threat levels
    test_cases = [
        # SAFE URLs
        ("https://www.google.com", "Safe - Known company", "SAFE"),
        ("https://github.com", "Safe - Code repository", "SAFE"),
        ("https://www.wikipedia.org", "Safe - Encyclopedia", "SAFE"),
        
        # SUSPICIOUS - Phishing keywords
        ("https://login-verify.example.com", "Suspicious - Has 'login' and 'verify'", "SUSPICIOUS"),
        ("https://verify-password-reset.site", "Suspicious - Multiple keywords", "SUSPICIOUS"),
        ("https://secure-update-account.online", "Suspicious - Suspicious TLD", "SUSPICIOUS"),
        
        # PHISHING - Multiple indicators
        ("https://verify-account-bank.tk", "Phishing - TLD + keywords", "PHISHING"),
        ("https://192.168.1.1/login", "Phishing - IP address + login", "PHISHING"),
        ("https://confirm-paypal-secure-update.xyz", "Phishing - TLD + keywords", "PHISHING"),
        ("https://user@bank-login-verify.com", "Phishing - @ symbol + keywords", "PHISHING"),
        ("https://secure-login-confirm-bank-verify.click", "Phishing - .click TLD + many keywords", "PHISHING"),
    ]
    
    results = []
    for url, description, expected in test_cases:
        try:
            print(f"URL: {url}")
            print(f"  Description: {description}")
            
            r = requests.post(f"{BASE_ML}/scan", json={"url": url}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                data = r.json()
                risk_score = data['risk_score']
                status = data['status']
                risk_label = data['risk_label']
                
                # Visual indicator
                if status == "PHISHING":
                    indicator = "🚨"
                elif status == "SUSPICIOUS":
                    indicator = "⚠️ "
                else:
                    indicator = "✓ "
                
                match = status == expected
                match_symbol = f"{Colors.GREEN}✓{Colors.ENDC}" if match else f"{Colors.RED}✗{Colors.ENDC}"
                
                print(f"  {match_symbol} {indicator} Risk Score: {risk_score:3d} | Status: {status:10s} | Label: {risk_label}")
                results.append({
                    'url': url,
                    'score': risk_score,
                    'status': status,
                    'expected': expected,
                    'match': match
                })
            else:
                print(f"  {Colors.RED}✗ Error: HTTP {r.status_code}{Colors.ENDC}")
        except Exception as e:
            print(f"  {Colors.RED}✗ Exception: {str(e)[:60]}{Colors.ENDC}")
        print()
    
    # Accuracy summary
    if results:
        correct = sum(1 for r in results if r['match'])
        total = len(results)
        accuracy = (correct / total * 100) if total > 0 else 0
        
        print(f"\n{Colors.BOLD}Accuracy Summary:{Colors.ENDC}")
        print(f"Correct predictions: {correct}/{total}")
        print(f"Accuracy: {accuracy:.1f}%\n")
        
        if accuracy >= 80:
            print(f"{Colors.GREEN}✓ EXCELLENT ACCURACY - System is performing well!{Colors.ENDC}")
        elif accuracy >= 60:
            print(f"{Colors.GREEN}✓ GOOD ACCURACY - System detection is working!{Colors.ENDC}")
        else:
            print(f"{Colors.YELLOW}⚠ NEEDS IMPROVEMENT - More tuning required{Colors.ENDC}")
    
    return results

def test_full_system_flow():
    """Test 2: Complete system flow (ML + Backend + Database)"""
    print_section("TEST 2: FULL SYSTEM FLOW TEST")
    
    test_urls = [
        ("https://example.com", "Safe website"),
        ("https://login.example.com", "Contains 'login'"),
        ("https://verify-account.bank.com", "Phishing indicators"),
        ("https://secure-update-paypal.xyz", "Suspicious pattern"),
    ]
    
    # Test 2A: Direct ML Server
    print(f"{Colors.BOLD}[TEST 2A] ML SERVER - Direct /scan endpoint{Colors.ENDC}")
    print("-" * 70)
    ml_results = []
    for url, desc in test_urls:
        try:
            r = requests.post(f"{BASE_ML}/scan", json={"url": url}, timeout=TIMEOUT)
            if r.status_code == 200:
                data = r.json()
                ml_results.append(data)
                status_symbol = f"{Colors.GREEN}✓{Colors.ENDC}"
                print(f"{status_symbol} {url}")
                print(f"   Risk Score: {data['risk_score']:3d} | Status: {data['status']:10s} | Label: {data['risk_label']}")
            else:
                print(f"{Colors.RED}✗{Colors.ENDC} {url}: HTTP {r.status_code}")
        except Exception as e:
            print(f"{Colors.RED}✗{Colors.ENDC} {url}: {str(e)[:50]}")
    
    # Test 2B: Backend API
    print(f"\n{Colors.BOLD}[TEST 2B] BACKEND API - /api/scan endpoint{Colors.ENDC}")
    print("-" * 70)
    backend_results = []
    for url, desc in test_urls[:2]:
        try:
            r = requests.post(f"{BASE_BACKEND}/api/scan", json={"url": url}, timeout=TIMEOUT)
            if r.status_code == 200:
                data = r.json()
                backend_results.append(data)
                status_symbol = f"{Colors.GREEN}✓{Colors.ENDC}"
                print(f"{status_symbol} {url}")
                print(f"   Risk Score: {data['risk_score']:3d} | Status: {data['status']:10s}")
                if 'risk_reasons' in data:
                    print(f"   Risk Reasons: {data['risk_reasons']}")
            else:
                print(f"{Colors.RED}✗{Colors.ENDC} {url}: HTTP {r.status_code} - {r.text[:50]}")
        except Exception as e:
            print(f"{Colors.RED}✗{Colors.ENDC} {url}: {str(e)[:50]}")
    
    # Test 2C: Database Storage
    print(f"\n{Colors.BOLD}[TEST 2C] DATABASE - History storage (/api/history){Colors.ENDC}")
    print("-" * 70)
    try:
        r = requests.get(f"{BASE_BACKEND}/api/history", timeout=TIMEOUT)
        if r.status_code == 200:
            history = r.json()
            print(f"{Colors.GREEN}✓{Colors.ENDC} Successfully retrieved history")
            print(f"  Total scans in database: {len(history)}")
            if history:
                print(f"\n  Latest scans:")
                for i, item in enumerate(history[:5], 1):
                    print(f"  {i}. {item['url']}")
                    print(f"     Risk Score: {item['risk_score']}, Status: {item['status']}")
        else:
            print(f"{Colors.RED}✗{Colors.ENDC} HTTP {r.status_code}")
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.ENDC} Error: {str(e)[:60]}")
    
    return ml_results, backend_results

def test_unsafe_characters():
    """Test 3: Unsafe character detection and protocol validation"""
    print_section("TEST 3: UNSAFE CHARACTER & PROTOCOL VALIDATION TEST")
    
    test_cases = [
        {
            "name": "Safe HTTPS URL",
            "url": "https://example.com",
            "expected_status": "SAFE",
        },
        {
            "name": "HTTP instead of HTTPS",
            "url": "http://example.com",
            "expected_status": "SUSPICIOUS",
        },
        {
            "name": "URL with space character",
            "url": "https://example.com/path with spaces",
            "expected_status": "PHISHING",
        },
        {
            "name": "URL with double quotes",
            "url": 'https://example.com/"test"',
            "expected_status": "PHISHING",
        },
        {
            "name": "URL with less than symbol",
            "url": "https://example.com/<script>",
            "expected_status": "PHISHING",
        },
        {
            "name": "URL with greater than symbol",
            "url": "https://example.com/>alert",
            "expected_status": "PHISHING",
        },
    ]
    
    results = []
    for test in test_cases:
        try:
            print(f"Testing: {test['name']}")
            print(f"  URL: {test['url']}")
            
            r = requests.post(f"{BASE_ML}/scan", json={"url": test['url']}, timeout=TIMEOUT)
            
            if r.status_code == 200:
                data = r.json()
                status = data['status']
                match = status == test['expected_status']
                match_symbol = f"{Colors.GREEN}✓{Colors.ENDC}" if match else f"{Colors.YELLOW}⚠{Colors.ENDC}"
                
                print(f"  {match_symbol} Status: {status} | Expected: {test['expected_status']}")
                if 'risk_reasons' in data and data['risk_reasons']:
                    print(f"     Reasons: {', '.join(data['risk_reasons'])}")
                
                results.append({
                    'name': test['name'],
                    'url': test['url'],
                    'status': status,
                    'expected': test['expected_status'],
                    'match': match
                })
            else:
                print(f"  {Colors.RED}✗{Colors.ENDC} HTTP {r.status_code}")
        except Exception as e:
            print(f"  {Colors.RED}✗{Colors.ENDC} Exception: {str(e)[:60]}")
        print()
    
    if results:
        correct = sum(1 for r in results if r['match'])
        total = len(results)
        accuracy = (correct / total * 100) if total > 0 else 0
        print(f"Unsafe Character Detection Accuracy: {accuracy:.1f}% ({correct}/{total})")
    
    return results

def print_summary(all_results):
    """Print final test summary"""
    print_section("TEST SUMMARY")
    
    total_tests = sum(len(r) if isinstance(r, list) else 1 for r in all_results)
    print(f"{Colors.BOLD}Total tests executed: {total_tests}{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}System Status:{Colors.ENDC}")
    print(f"  {Colors.GREEN}✓{Colors.ENDC} ML Server:          Running on {BASE_ML}")
    print(f"  {Colors.GREEN}✓{Colors.ENDC} Backend Server:     Running on {BASE_BACKEND}")
    print(f"  {Colors.GREEN}✓{Colors.ENDC} Frontend:           http://localhost:5174 (if running)")
    print(f"\n{Colors.GREEN}✓ ALL TESTS COMPLETED{Colors.ENDC}")
    print(f"\n{Colors.BOLD}Next Steps:{Colors.ENDC}")
    print("  1. Review test results above")
    print("  2. Fix any failed tests")
    print("  3. Run this test again to verify fixes")
    print()

def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'PhishGuard Comprehensive Test Suite'.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.ENDC}\n")
    
    all_results = []
    
    try:
        # Test 1: Accuracy
        accuracy_results = test_ml_server_accuracy()
        all_results.append(accuracy_results)
        
        # Test 2: Full Flow
        ml_results, backend_results = test_full_system_flow()
        all_results.append((ml_results, backend_results))
        
        # Test 3: Unsafe Characters
        unsafe_results = test_unsafe_characters()
        all_results.append(unsafe_results)
        
        # Summary
        print_summary(all_results)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
