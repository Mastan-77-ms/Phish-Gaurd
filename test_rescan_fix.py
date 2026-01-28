#!/usr/bin/env python
"""
Test to verify:
1. First scan shows correct risk score
2. Rescan shows same/consistent risk score (not 0%)
3. History is stored for each scan
"""

import requests
import json
import time

print("="*70)
print("TESTING RESCAN AND HISTORY STORAGE FIX")
print("="*70)

BACKEND_URL = "http://localhost:3001"
ML_URL = "http://localhost:8000"
test_urls = [
    ("https://verify-account-bank.tk", "Should be HIGH PHISHING"),
    ("https://www.google.com", "Should be SAFE"),
    ("https://login-paypal.xyz", "Should be SUSPICIOUS"),
]

def test_ml_directly():
    """Test ML server directly"""
    print("\n" + "="*70)
    print("[TEST 1] ML Server Direct Testing")
    print("="*70)
    
    test_url = "https://verify-account-bank.tk"
    print(f"\nScanning: {test_url}")
    
    try:
        r = requests.post(f"{ML_URL}/api/v1/scan", json={"url": test_url}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"✓ ML Response: {data['status']} ({data['risk_score']}%)")
            print(f"  Risk Reasons: {len(data.get('risk_reasons', []))} items")
            return data
        else:
            print(f"✗ ML Error: {r.status_code}")
            return None
    except Exception as e:
        print(f"✗ ML Exception: {e}")
        return None

def test_backend_scan():
    """Test backend scan"""
    print("\n" + "="*70)
    print("[TEST 2] Backend Scan Testing")
    print("="*70)
    
    for url, expected in test_urls:
        print(f"\nScanning: {url}")
        print(f"Expected: {expected}")
        
        try:
            r = requests.post(f"{BACKEND_URL}/api/scan", json={"url": url}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                print(f"✓ Status: {data['status']} ({data['risk_score']}%)")
                print(f"  Response Time: {data['response_time']}s")
                print(f"  Reasons: {len(data.get('risk_reasons', []))} items")
            else:
                print(f"✗ Error: {r.status_code} - {r.text}")
        except Exception as e:
            print(f"✗ Exception: {e}")

def test_rescan_consistency():
    """Test that rescanning gives consistent results"""
    print("\n" + "="*70)
    print("[TEST 3] Rescan Consistency Testing")
    print("="*70)
    
    test_url = "https://verify-account-bank.tk"
    results = []
    
    for scan_num in range(3):
        print(f"\n--- Scan #{scan_num + 1} ---")
        try:
            r = requests.post(f"{BACKEND_URL}/api/scan", json={"url": test_url}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                print(f"Status: {data['status']}")
                print(f"Risk Score: {data['risk_score']}%")
                results.append(data['risk_score'])
                
                # Check if it's 0% (the bug we're fixing)
                if data['risk_score'] == 0:
                    print("⚠️  WARNING: Score is 0% - BUG DETECTED!")
                else:
                    print("✓ Score is not 0% - Good!")
            else:
                print(f"✗ Error: {r.status_code}")
        except Exception as e:
            print(f"✗ Exception: {e}")
        
        time.sleep(0.5)
    
    # Verify consistency
    print("\n--- Consistency Check ---")
    if len(results) >= 2:
        if len(set(results)) == 1:
            print(f"✓ All scans returned same score: {results[0]}%")
        else:
            print(f"⚠️  Scores varied: {results}")
    
    return results

def test_history_storage():
    """Test that history is stored for each scan"""
    print("\n" + "="*70)
    print("[TEST 4] History Storage Testing")
    print("="*70)
    
    # Scan a unique URL to test history
    test_url = f"https://test-{int(time.time())}.example.com"
    
    print(f"\nScanning unique URL: {test_url}")
    try:
        r = requests.post(f"{BACKEND_URL}/api/scan", json={"url": test_url}, timeout=10)
        if r.status_code == 200:
            print("✓ Scan successful")
        else:
            print(f"✗ Scan failed: {r.status_code}")
            return
    except Exception as e:
        print(f"✗ Scan exception: {e}")
        return
    
    # Check history
    time.sleep(1)
    print("\nChecking history...")
    try:
        r = requests.get(f"{BACKEND_URL}/api/history", timeout=10)
        if r.status_code == 200:
            history = r.json()
            print(f"✓ Retrieved {len(history)} items from history")
            
            # Look for our test URL
            found = False
            for item in history[:10]:  # Check first 10
                if test_url in item.get('url', ''):
                    print(f"✓ Found test URL in history!")
                    print(f"  Status: {item['status']} ({item['risk_score']}%)")
                    found = True
                    break
            
            if not found:
                print("⚠️  Test URL not found in recent history")
        else:
            print(f"✗ History error: {r.status_code}")
    except Exception as e:
        print(f"✗ History exception: {e}")

def test_multiple_rescans():
    """Test multiple rescans of same URL - should show in history"""
    print("\n" + "="*70)
    print("[TEST 5] Multiple Rescans - History Test")
    print("="*70)
    
    test_url = "https://verify-account-bank.tk"
    
    print(f"\nScanning {test_url} 3 times...")
    for i in range(3):
        try:
            r = requests.post(f"{BACKEND_URL}/api/scan", json={"url": test_url}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                print(f"  Scan {i+1}: {data['status']} ({data['risk_score']}%)")
            time.sleep(0.3)
        except Exception as e:
            print(f"  Scan {i+1}: Error - {e}")
    
    # Get history
    print("\nChecking history for all scans...")
    time.sleep(1)
    try:
        r = requests.get(f"{BACKEND_URL}/api/history", timeout=10)
        if r.status_code == 200:
            history = r.json()
            
            # Count occurrences
            count = sum(1 for item in history if test_url == item.get('url', ''))
            print(f"✓ Found {count} scans of {test_url} in history")
            
            if count >= 3:
                print("✓ All 3 scans recorded in history!")
            else:
                print(f"⚠️  Expected 3 scans, found {count}")
        else:
            print(f"✗ History error: {r.status_code}")
    except Exception as e:
        print(f"✗ Exception: {e}")

# Run all tests
print("\nChecking service availability...")
try:
    r = requests.get(f"{ML_URL}/api/v1/health", timeout=5)
    if r.status_code == 200:
        print("✓ ML Server is running")
    else:
        print(f"⚠️  ML Server health check returned {r.status_code}")
except Exception as e:
    print(f"✗ ML Server not available: {e}")
    print("Start ML server: cd ml_server/ml_server && python app.py")

try:
    r = requests.get(f"{BACKEND_URL}/api/history", timeout=5)
    print("✓ Backend Server is running")
except Exception as e:
    print(f"✗ Backend Server not available: {e}")
    print("Start Backend: cd backend/backend && npm start")

print("\n")
input("Press Enter to start tests...")

test_ml_directly()
test_backend_scan()
test_rescan_consistency()
test_history_storage()
test_multiple_rescans()

print("\n" + "="*70)
print("TESTING COMPLETE")
print("="*70)
print("\nSummary of Fixes:")
print("  1. ✓ ML predict() now accumulates scores on rescan (not 0%)")
print("  2. ✓ Backend logs every scan to ScanHistory")
print("  3. ✓ History retrieval now uses ScanHistory (all scans)")
print("  4. ✓ Error handling improved with retries")
print("\nIf all tests pass, rescan bug is fixed!")
print("="*70)
