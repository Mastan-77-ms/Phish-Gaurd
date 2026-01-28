#!/usr/bin/env python
import subprocess
import time
import requests
import sys

print("="*70)
print("PHISHGUARD FULL SYSTEM STARTUP")
print("="*70)

# Start ML Server
print("\n[1] Starting ML Server on port 5000...")
ml_process = subprocess.Popen(
    [sys.executable, "app.py"],
    cwd="c:\\Mini-Project-fsd\\pi\\ml_server\\ml_server",
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT
)
print("   ML Server process started (PID: {})".format(ml_process.pid))
time.sleep(3)

# Start Backend
print("\n[2] Starting Backend Server on port 3001...")
backend_process = subprocess.Popen(
    ["node", "server.js"],
    cwd="c:\\Mini-Project-fsd\\pi\\backend\\backend",
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT
)
print("   Backend process started (PID: {})".format(backend_process.pid))
time.sleep(2)

# Test ML Server
print("\n[3] Testing ML Server...")
try:
    r = requests.post("http://localhost:5000/scan", json={"url": "https://example.com"}, timeout=5)
    if r.status_code == 200:
        print("   ✓ ML Server is responding")
        data = r.json()
        print("   ✓ Sample response: Risk Score = {}".format(data['risk_score']))
    else:
        print("   ✗ ML Server error: {}".format(r.status_code))
except Exception as e:
    print("   ✗ ML Server error: {}".format(e))

# Test Backend
print("\n[4] Testing Backend Server...")
try:
    r = requests.post("http://localhost:3001/api/scan", json={"url": "https://test.com"}, timeout=5)
    if r.status_code == 200:
        print("   ✓ Backend Server is responding")
        data = r.json()
        print("   ✓ Sample response: Risk Score = {}".format(data.get('risk_score', 'N/A')))
    else:
        print("   ✗ Backend error: {} - {}".format(r.status_code, r.text[:100]))
except Exception as e:
    print("   ✗ Backend error: {}".format(e))

print("\n" + "="*70)
print("SERVERS RUNNING - Test with:")
print("  Frontend: http://localhost:5174")
print("  ML Server: http://localhost:5000")
print("  Backend: http://localhost:3001")
print("="*70)

# Keep processes alive
try:
    ml_process.wait()
except KeyboardInterrupt:
    print("\nShutting down...")
    ml_process.terminate()
    backend_process.terminate()
