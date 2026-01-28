#!/usr/bin/env python
"""
PhishGuard ML Server Comprehensive Test Suite
Consolidates all ML server testing functionality
Tests: API endpoints, integration, risk scoring, and database storage
"""

import requests
import json
import time
import sys

# Configuration
ML_SERVER_URL = "http://localhost:5000"
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

def test_quick_scan():
    """Test 1: Quick single scan"""
    print_section("TEST 1: QUICK API SCAN")
    
    print(f"{Colors.BOLD}Single URL Scan Test:{Colors.ENDC}")
    url = "https://login.example.com"
    
    try:
        response = requests.post(
            f'{ML_SERVER_URL}/scan',
            json={'url': url},
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"{Colors.GREEN}✓{Colors.ENDC} Response Status: {response.status_code}")
            print(f"  URL: {data['url']}")
            print(f"  Status: {data['status']}")
            print(f"  Risk Score: {data['risk_score']}")
            print(f"  Risk Label: {data['risk_label']}")
            print(f"  Response Time: {data['response_time']}s")
            return True
        else:
            print(f"{Colors.RED}✗{Colors.ENDC} Error: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.ENDC} Exception: {str(e)}")
        return False

def test_batch_scanning():
    """Test 2: Batch scanning of multiple URLs"""
    print_section("TEST 2: BATCH SCANNING")
    
    test_urls = [
        "https://example.com",
        "https://login.example.com",
        "https://verify-account.banking.com",
        "https://secure-update-needed.com"
    ]
    
    print(f"{Colors.BOLD}Scanning {len(test_urls)} URLs:{Colors.ENDC}\n")
    
    results = []
    for url in test_urls:
        try:
            print(f"Scanning: {url}")
            response = requests.post(
                f"{ML_SERVER_URL}/scan",
                json={"url": url},
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                results.append(data)
                status_emoji = "✓" if data['status'] == 'SAFE' else ("⚠️" if data['status'] == 'SUSPICIOUS' else "🚨")
                print(f"  {Colors.GREEN}✓{Colors.ENDC} Risk Score: {data['risk_score']} | Status: {data['status']}")
            else:
                print(f"  {Colors.RED}✗{Colors.ENDC} HTTP {response.status_code}")
        except Exception as e:
            print(f"  {Colors.RED}✗{Colors.ENDC} Exception: {str(e)[:50]}")
    
    print(f"\n{Colors.BOLD}Scanning Summary:{Colors.ENDC}")
    print(f"Successfully scanned: {len(results)}/{len(test_urls)} URLs\n")
    
    return results

def test_risk_scoring():
    """Test 3: Risk score calculation"""
    print_section("TEST 3: RISK SCORE CALCULATION")
    
    test_cases = [
        ("https://www.google.com", "Safe - Known company", "SAFE", (0, 20)),
        ("https://login.example.com", "Suspicious - Login keyword", "SUSPICIOUS", (30, 70)),
        ("https://verify-account-bank.tk", "Phishing - Free TLD + keywords", "PHISHING", (75, 100)),
    ]
    
    print(f"{Colors.BOLD}Testing Risk Score Ranges:{Colors.ENDC}\n")
    
    results = []
    for url, description, expected_status, score_range in test_cases:
        try:
            print(f"URL: {url}")
            print(f"Description: {description}")
            print(f"Expected Status: {expected_status}, Score Range: {score_range[0]}-{score_range[1]}")
            
            response = requests.post(
                f"{ML_SERVER_URL}/scan",
                json={"url": url},
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                score = data['risk_score']
                status = data['status']
                
                status_match = status == expected_status
                score_in_range = score_range[0] <= score <= score_range[1]
                
                status_symbol = f"{Colors.GREEN}✓{Colors.ENDC}" if status_match else f"{Colors.RED}✗{Colors.ENDC}"
                score_symbol = f"{Colors.GREEN}✓{Colors.ENDC}" if score_in_range else f"{Colors.YELLOW}⚠{Colors.ENDC}"
                
                print(f"  {status_symbol} Status: {status}")
                print(f"  {score_symbol} Risk Score: {score}")
                
                results.append({
                    'url': url,
                    'score': score,
                    'status': status,
                    'expected_status': expected_status,
                    'status_match': status_match,
                    'score_in_range': score_in_range
                })
            else:
                print(f"  {Colors.RED}✗{Colors.ENDC} HTTP {response.status_code}")
        except Exception as e:
            print(f"  {Colors.RED}✗{Colors.ENDC} Exception: {str(e)[:50]}")
        print()
    
    return results

def test_database_storage():
    """Test 4: Database history and stats"""
    print_section("TEST 4: DATABASE STORAGE & STATS")
    
    print(f"{Colors.BOLD}Checking History:{Colors.ENDC}")
    try:
        response = requests.get(
            f'{ML_SERVER_URL}/history',
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            history = response.json()
            print(f"{Colors.GREEN}✓{Colors.ENDC} Successfully retrieved history")
            print(f"  Total scans stored: {len(history)}")
            
            if history:
                print(f"\n  Recent scans:")
                for i, item in enumerate(history[:5], 1):
                    print(f"    {i}. {item['url']}")
                    print(f"       Status: {item['status']}, Score: {item['risk_score']}, Time: {item.get('timestamp', 'N/A')}")
        else:
            print(f"{Colors.RED}✗{Colors.ENDC} HTTP {response.status_code}")
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.ENDC} Exception: {str(e)[:50]}")
    
    print(f"\n{Colors.BOLD}Checking Statistics:{Colors.ENDC}")
    try:
        response = requests.get(
            f'{ML_SERVER_URL}/stats',
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            stats = response.json()
            print(f"{Colors.GREEN}✓{Colors.ENDC} Successfully retrieved stats")
            print(f"  Total Scans: {stats.get('total_scans', 'N/A')}")
            print(f"  Threats Blocked: {stats.get('threats_blocked', 'N/A')}")
            print(f"  Safe URLs: {stats.get('safe_urls', 'N/A')}")
            print(f"  Avg Response Time: {stats.get('avg_response_time', 'N/A')}s")
        else:
            print(f"{Colors.RED}✗{Colors.ENDC} HTTP {response.status_code}")
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.ENDC} Exception: {str(e)[:50]}")

def test_deep_learning_integration():
    """Test 5: Deep learning model integration"""
    print_section("TEST 5: DEEP LEARNING INTEGRATION")
    
    test_urls = [
        {
            "url": "https://www.google.com",
            "expected_status": "SAFE",
            "description": "Google main site - definitely safe"
        },
        {
            "url": "https://www.github.com/user/repo",
            "expected_status": "SAFE",
            "description": "GitHub repo - safe"
        },
        {
            "url": "https://login-verify-google.tk/verify?user=admin@gmail.com",
            "expected_status": "PHISHING",
            "description": "Suspicious free TLD with login keywords"
        },
        {
            "url": "http://192.168.1.1/verify/paypal/login",
            "expected_status": "PHISHING",
            "description": "IP address with PayPal + login keywords"
        },
    ]
    
    print(f"{Colors.BOLD}Testing Deep Learning Model Predictions:{Colors.ENDC}\n")
    
    results = []
    for test_case in test_urls:
        url = test_case["url"]
        print(f"[{test_case['description']}]")
        print(f"URL: {url}")
        
        try:
            response = requests.post(
                f"{ML_SERVER_URL}/scan",
                json={"url": url},
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                
                status_match = data['status'] == test_case['expected_status']
                status_symbol = f"{Colors.GREEN}✓{Colors.ENDC}" if status_match else f"{Colors.YELLOW}⚠{Colors.ENDC}"
                
                print(f"  {status_symbol} Status: {data['status']} (Expected: {test_case['expected_status']})")
                print(f"  Risk Score: {data['risk_score']}/100")
                print(f"  Response Time: {data['response_time']:.3f}s")
                
                if 'risk_reasons' in data and data['risk_reasons']:
                    print(f"  Risk Reasons: {', '.join(data['risk_reasons'])}")
                
                results.append({
                    "url": url,
                    "success": True,
                    "risk_score": data['risk_score'],
                    "status": data['status'],
                    "expected": test_case['expected_status'],
                    "match": status_match
                })
            else:
                print(f"  {Colors.RED}✗{Colors.ENDC} HTTP {response.status_code}")
                results.append({"url": url, "success": False})
        except Exception as e:
            print(f"  {Colors.RED}✗{Colors.ENDC} Exception: {str(e)[:50]}")
            results.append({"url": url, "success": False})
        
        print()
    
    correct = sum(1 for r in results if r.get('success') and r.get('match'))
    total = len([r for r in results if r.get('success')])
    accuracy = (correct / total * 100) if total > 0 else 0
    print(f"{Colors.BOLD}Prediction Accuracy: {accuracy:.1f}% ({correct}/{total}){Colors.ENDC}\n")
    
    return results

def main():
    """Run all ML server tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'PhishGuard ML Server Test Suite'.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.ENDC}\n")
    
    print(f"Testing ML Server at: {ML_SERVER_URL}\n")
    
    try:
        # Run tests
        test_quick_scan()
        test_batch_scanning()
        test_risk_scoring()
        test_database_storage()
        test_deep_learning_integration()
        
        # Summary
        print_section("TEST COMPLETE")
        print(f"{Colors.GREEN}✓ All ML server tests completed{Colors.ENDC}")
        print(f"  Next: Test Backend API and Frontend integration")
        print()
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
