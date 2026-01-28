# PhishGuard - Complete System Architecture

## System Overview Diagram

```
┌───────────────────────────────────────────────────────────────────────────┐
│                         USER BROWSER (React App)                          │
│                         http://localhost:5173                             │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐│
│  │                          React Frontend                              ││
│  │  ┌────────────────┐  ┌──────────────┐  ┌──────────────────────────┐││
│  │  │   App.jsx      │  │  Header.jsx  │  │ FeatureAnalysis.jsx      │││
│  │  │                │  │              │  │                          │││
│  │  │ • URL Input    │  │ • Theme      │  │ • 14 Features Display   │││
│  │  │ • Scan Logic   │  │ • History    │  │ • Risk Scores          │││
│  │  │ • Results      │  │   Toggle     │  │ • Color Coded          │││
│  │  └────────────────┘  └──────────────┘  └──────────────────────────┘││
│  │                                                                        ││
│  │  ┌────────────────┐  ┌────────────────────────────────────────────┐ ││
│  │  │ Dashboard.jsx  │  │  StatsDisplay.jsx                          │ ││
│  │  │                │  │                                            │ ││
│  │  │ • Scan History │  │ • Total Scans                             │ ││
│  │  │ • Timeline     │  │ • Threats Blocked                         │ ││
│  │  │ • Rescan Data  │  │ • Safe URLs                               │ ││
│  │  └────────────────┘  └────────────────────────────────────────────┘ ││
│  │                                                                        ││
│  │  Theme: Dark/Light Mode Toggle                                       ││
│  └──────────────────────────────────────────────────────────────────────┘│
└────┬────────────────────────────────────────────────────────────────────┬─┘
     │                                                                    │
     │ HTTP Requests (JSON)                      HTTP Responses (JSON)   │
     │ POST /api/scan                            {result, features}      │
     │ GET /api/history                          [scan records]          │
     │ POST /api/history/:url                    [detailed scans]        │
     │                                                                    │
┌────▼────────────────────────────────────────────────────────────────────▼─┐
│                     BACKEND SERVER (Node.js)                              │
│                     http://localhost:3000                                 │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐│
│  │                       Express API Server                             ││
│  │                                                                       ││
│  │  ┌────────────────────────────────────────────────────────────────┐ ││
│  │  │ Endpoints                                                      │ ││
│  │  │ • POST /api/scan - Receive URL, call ML Server               │ ││
│  │  │ • GET /api/history - Get all scans (aggregated)             │ ││
│  │  │ • GET /api/scan-history/:url - Get detailed scans           │ ││
│  │  │ • DELETE /api/history/:id - Delete record                   │ ││
│  │  └────────────────────────────────────────────────────────────────┘ ││
│  │                                                                       ││
│  │  ┌────────────────────────────────────────────────────────────────┐ ││
│  │  │ Data Models                                                    │ ││
│  │  │ • Scan.js          - MongoDB schema (url, score, count)      │ ││
│  │  │ • ScanHistory.js   - Detailed scan records                   │ ││
│  │  │ • db.js            - MongoDB connection                      │ ││
│  │  └────────────────────────────────────────────────────────────────┘ ││
│  │                                                                       ││
│  │  Features:                                                           ││
│  │  • Duplicate prevention (scan_count increment)                       ││
│  │  • CORS enabled for frontend                                        ││
│  │  • Request validation                                               ││
│  │  • Error handling                                                   ││
│  └──────────────────────────────────────────────────────────────────────┘│
└────┬────────────────────────────────────────────────────────────────────┬─┘
     │                                                                    │
     │ HTTP POST /scan                          HTTP Response           │
     │ {url: "https://..."}                     {status, risk_score,    │
     │                                           features}               │
     │                                                                    │
     │ MongoDB Save/Query                       Query Results           │
     │ {url, scan_count, last_scanned}          [scan records]          │
     │                                                                    │
┌────▼────────────────────────────────────────────────────────────────────▼─┐
│                 ML SERVER (Python/FastAPI)                                │
│                 http://localhost:8000                                     │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐│
│  │                      FastAPI Server                                  ││
│  │                                                                       ││
│  │  ┌─────────────────────────────────────────────────────────────────┐ ││
│  │  │ POST /scan Endpoint                                            │ ││
│  │  │                                                                │ ││
│  │  │ Input: {url: "https://example.com"}                          │ ││
│  │  │                                                                │ ││
│  │  │ Processing Flow:                                              │ ││
│  │  │ 1. Extract 14 URL features                                   │ ││
│  │  │ 2. Run Heuristic Analysis  ─────────────────────┐           │ ││
│  │  │ 3. Run Deep Learning Model ────────────────────┐│           │ ││
│  │  │ 4. Combine Ensemble Score                   ┌──┴┴──┐        │ ││
│  │  │ 5. Generate Feature Analysis               │Scores│        │ ││
│  │  │ 6. Save to History (SQLite)                └──┬┬──┘        │ ││
│  │  │ 7. Return Results                             ││            │ ││
│  │  │                                               ││            │ ││
│  │  │ Output: {url, status, risk_score, features}  ││            │ ││
│  │  └─────────────────────────────────────────────┬┼┼────────────┘ ││
│  │                                                 │││               ││
│  │  ┌───────────────────────────────────────────┐ │││               ││
│  │  │ Heuristic Analysis Engine                 │ │││               ││
│  │  │                                           │ │││               ││
│  │  │ • Protocol checking (HTTPS vs HTTP)      │ │││               ││
│  │  │ • Phishing keywords detection            │ │││               ││
│  │  │ • Financial keywords (bank, paypal)      │ │││               ││
│  │  │ • Suspicious TLDs (.tk, .ml, .ga)        │ │││               ││
│  │  │ • IP address domain detection            │ │││               ││
│  │  │ • Subdomain analysis                     │ │││               ││
│  │  │ • URL length and structure               │ │││               ││
│  │  │ • Special character patterns             │ │││               ││
│  │  │ • Obfuscation attempts                   │ │││               ││
│  │  │                                           │ │││               ││
│  │  │ Output: Heuristic Score (0-100)          │ │││               ││
│  │  └───────────────┬───────────────────────────┘ │││               ││
│  │                  │ SCORE: X%                   │││               ││
│  │                  └────────────────────┐        │││               ││
│  │                                      ┌┴─┬─────┘││               ││
│  │  ┌───────────────────────────────────────┐   │││               ││
│  │  │ Deep Learning Neural Network          │   │││               ││
│  │  │                                       │   │││               ││
│  │  │ Architecture:                         │   │││               ││
│  │  │ Input (14) → Dense(64) + Dropout    │   │││               ││
│  │  │           → Dense(32) + Dropout    │   │││               ││
│  │  │           → Dense(16) + Dropout    │   │││               ││
│  │  │           → Dense(1, sigmoid)      │   │││               ││
│  │  │                                       │   │││               ││
│  │  │ Model File: phishing_dl_model.h5    │   │││               ││
│  │  │ Scaler: feature_scaler.pkl          │   │││               ││
│  │  │                                       │   │││               ││
│  │  │ Input: 14-dimensional feature vector │   │││               ││
│  │  │ Output: Deep Learning Score (0-100)  │   │││               ││
│  │  └───────────────┬───────────────────────┘   │││               ││
│  │                  │ SCORE: Y%                  │││               ││
│  │                  └──────────────────┬─────────┘││               ││
│  │                                     ┌┴─────────┘│               ││
│  │  ┌───────────────────────────────────────┐      │               ││
│  │  │ Ensemble Scoring Engine               │      │               ││
│  │  │                                       │      │               ││
│  │  │ Formula:                              │      │               ││
│  │  │ Final Score = (X × 0.4) + (Y × 0.6)  │      │               ││
│  │  │                                       │      │               ││
│  │  │ Result: Ensemble Score (0-100)       │      │               ││
│  │  │ Interpretation:                       │      │               ││
│  │  │ • 0-30: LIKELY SAFE ✓                │      │               ││
│  │  │ • 31-60: SUSPICIOUS ⚠                │      │               ││
│  │  │ • 61-100: LIKELY PHISHING ✗          │      │               ││
│  │  └───────────────┬───────────────────────┘      │               ││
│  │                  │ FINAL SCORE: Z%             │               ││
│  │                  └─────────────────────────────┘               ││
│  │                                                                 ││
│  │  ┌──────────────────────────────────────────────────────────┐ ││
│  │  │ 14-Feature Analysis Extraction                          │ ││
│  │  │                                                          │ ││
│  │  │ 1. qty_dot_url         - Dots in URL                  │ ││
│  │  │ 2. qty_hyphen_url      - Hyphens in URL             │ ││
│  │  │ 3. qty_underline_url   - Underscores in URL         │ ││
│  │  │ 4. qty_slash_url       - Slashes in URL             │ ││
│  │  │ 5. qty_questionmark    - Query parameters            │ ││
│  │  │ 6. qty_equal_url       - Equal signs                │ ││
│  │  │ 7. qty_at_url          - @ symbols (very suspicious) │ ││
│  │  │ 8. qty_and_url         - & parameter separators     │ ││
│  │  │ 9. length_url          - Total URL length           │ ││
│  │  │ 10. qty_dot_domain     - Dots in domain             │ ││
│  │  │ 11. domain_length      - Domain length              │ ││
│  │  │ 12. domain_in_ip       - IP address domain          │ ││
│  │  │ 13. directory_length   - Path length                │ ││
│  │  │ 14. params_length      - Parameter string length    │ ││
│  │  │                                                          │ ││
│  │  │ Each feature has:                                       │ ││
│  │  │ • value (actual count/measurement)                     │ ││
│  │  │ • safe (boolean - is it suspicious?)                 │ ││
│  │  │ • icon (✓ or ✗)                                      │ ││
│  │  │ • risk_score (0-100 points)                          │ ││
│  │  └──────────────────────────────────────────────────────────┘ ││
│  │                                                                 ││
│  └──────────────────────────────────────────────────────────────────┘│
└────┬──────────────────────────────────────────────────────────────┬──┘
     │                                                              │
     │ SQLite Database                     File System             │
     │ (scan_history.db)                   (model files)           │
     │                                                              │
┌────▼──────────────────────────────────────────────────────────────▼──┐
│                       Data Storage Layer                              │
│                                                                        │
│  ┌─────────────────────────────────┐  ┌───────────────────────────┐ │
│  │ SQLite Database (ML Server)     │  │ Model Files               │ │
│  │                                 │  │                           │ │
│  │ Table: scan_history             │  │ • phishing_dl_model.h5    │ │
│  │ Columns:                        │  │ • feature_scaler.pkl      │ │
│  │ • id (primary key)              │  │ • phishing_model.pkl      │ │
│  │ • url                           │  │   (traditional ML)        │ │
│  │ • risk_score                    │  │                           │ │
│  │ • status                        │  │ Updated After Training    │ │
│  │ • timestamp                     │  │                           │ │
│  │ • response_time                 │  │ Used For Inference        │ │
│  │                                 │  │                           │ │
│  │ Fast Local Storage              │  │ Loaded on Server Startup  │ │
│  └─────────────────────────────────┘  └───────────────────────────┘ │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ MongoDB Database (Backend)                                   │   │
│  │                                                              │   │
│  │ Collection: scans                                           │   │
│  │ • url (unique, lowercase)                                  │   │
│  │ • risk_score                                               │   │
│  │ • status                                                   │   │
│  │ • risk_label                                               │   │
│  │ • response_time                                            │   │
│  │ • scan_count (incremented for duplicates)                 │   │
│  │ • last_scanned (timestamp)                                │   │
│  │                                                              │   │
│  │ Collection: scan_history                                   │   │
│  │ • url                                                      │   │
│  │ • risk_score                                               │   │
│  │ • status                                                   │   │
│  │ • timestamp                                                │   │
│  │ • All scan details for timeline view                      │   │
│  │                                                              │   │
│  │ Persistent Cloud Storage                                   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Complete Data Flow                               │
└─────────────────────────────────────────────────────────────────────────┘

1. USER SUBMITS URL
   ┌──────────────────────────┐
   │ Input: https://bank.tk   │
   └────────────┬─────────────┘
                │
2. FRONTEND VALIDATION
   ├─ Check for "://" (protocol)
   ├─ Show alert if missing
   └─ Send to backend if valid
                │
3. BACKEND PROCESSING
   ├─ Receive URL
   ├─ Check if duplicate (scan_count++)
   └─ Call ML Server
                │
4. ML SERVER ANALYSIS
   ├─ Extract 14 Features
   │  ├─ qty_dot_url: 2
   │  ├─ qty_hyphen_url: 1
   │  ├─ qty_at_url: 0
   │  └─ ... (10 more features)
   │
   ├─ Heuristic Analysis (Parallel)
   │  ├─ Check protocol (HTTP/HTTPS)
   │  ├─ Check for suspicious keywords
   │  ├─ Check TLD reputation
   │  ├─ Check domain patterns
   │  └─ Score: 75%
   │
   ├─ Deep Learning Inference (Parallel)
   │  ├─ Normalize 14 features
   │  ├─ Pass through neural network
   │  ├─ 64 neurons (relu) + dropout
   │  ├─ 32 neurons (relu) + dropout
   │  ├─ 16 neurons (relu) + dropout
   │  ├─ Output layer (sigmoid) = 0.82
   │  └─ Score: 82%
   │
   ├─ Ensemble Combination
   │  ├─ Formula: (75 × 0.4) + (82 × 0.6)
   │  └─ Final Score: 79%
   │
   ├─ Feature Analysis Generation
   │  ├─ Assign risk contribution to each feature
   │  ├─ Color code (green/red)
   │  ├─ Generate description
   │  └─ Total feature risk: 145 points
   │
   └─ Return to Backend
                │
5. BACKEND STORAGE
   ├─ MongoDB Save
   │  ├─ Add/Update scan record
   │  ├─ Increment scan_count if duplicate
   │  └─ Save to scan_history collection
   │
   └─ Return to Frontend
                │
6. FRONTEND DISPLAY
   ├─ Show Risk Score (79/100)
   ├─ Show Status (LIKELY PHISHING) ✗
   ├─ Display 14 Features with colors
   ├─ Show scan history
   │  └─ Click count to view timeline
   │
   └─ Update dashboard stats

7. USER INTERACTION OPTIONS
   ├─ Rescan URL → Repeat from step 2
   ├─ View History → Show all scans for URL
   ├─ Delete Record → Remove from history
   ├─ Toggle Theme → Dark/Light mode
   └─ Search New URL → Start from step 1
```

## Scoring Breakdown Example

```
URL: https://login-verify-amazon.tk/confirm?account=secure&user=admin@gmail.com

┌─────────────────────────────────────────────────────────────────┐
│ HEURISTIC ANALYSIS (Weight: 40%)                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Protocol Check                                    +0 pts        │
│ ✓ HTTPS is present (secure)                                    │
│                                                                  │
│ Phishing Keywords in URL                          +50 pts       │
│ • "login" found in path                          +25 pts       │
│ • "verify" found in path                         +25 pts       │
│                                                                  │
│ Financial Keywords + Action Words                +30 pts        │
│ • "amazon" (domain) + "confirm" (action)                       │
│                                                                  │
│ Suspicious TLD                                   +35 pts        │
│ • .tk is in suspicious list                                    │
│                                                                  │
│ URL Length (59 chars)                             +10 pts       │
│ • Longer than typical URLs                                     │
│                                                                  │
│ Special Characters (?, &, =)                      +15 pts       │
│ • Multiple parameter separators                                │
│                                                                  │
│ HEURISTIC SCORE = 140 → Capped at 100 → 100/100                │
│ ✗ EXTREMELY HIGH RISK (Heuristic)                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ DEEP LEARNING ANALYSIS (Weight: 60%)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Feature Extraction (14 features):                               │
│ 1. qty_dot_url = 2          (normalized)                        │
│ 2. qty_hyphen_url = 1       (normalized)                        │
│ 3. qty_underline_url = 0    (normalized)                        │
│ 4. qty_slash_url = 2        (normalized)                        │
│ 5. qty_questionmark = 1     (normalized)                        │
│ 6. qty_equal_url = 2        (normalized)                        │
│ 7. qty_at_url = 1           (normalized) ← VERY SUSPICIOUS      │
│ 8. qty_and_url = 1          (normalized)                        │
│ 9. length_url = 59          (normalized)                        │
│ 10. qty_dot_domain = 2      (normalized)                        │
│ 11. domain_length = 13      (normalized)                        │
│ 12. domain_in_ip = 0        (normalized)                        │
│ 13. directory_length = 8    (normalized)                        │
│ 14. params_length = 38      (normalized) ← SUSPICIOUS           │
│                                                                  │
│ Neural Network Processing:                                      │
│ Input Layer: [norm feature vector]                              │
│ ↓                                                                │
│ Hidden Layer 1: Dense(64) + Dropout(0.3)                        │
│ → Learns basic patterns (syntax, structure)                    │
│ ↓                                                                │
│ Hidden Layer 2: Dense(32) + Dropout(0.2)                        │
│ → Combines patterns (dangerous combinations)                   │
│ ↓                                                                │
│ Hidden Layer 3: Dense(16) + Dropout(0.1)                        │
│ → Extracts high-level features (phishing likelihood)           │
│ ↓                                                                │
│ Output Layer: Dense(1) + Sigmoid                                │
│ → Probability score: 0.85                                      │
│                                                                  │
│ DEEP LEARNING SCORE = 0.85 × 100 = 85/100                       │
│ ⚠ HIGH RISK (Deep Learning)                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ ENSEMBLE COMBINATION                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Heuristic Score:      100/100  (Weight: 40%)                    │
│ Deep Learning Score:   85/100  (Weight: 60%)                    │
│                                                                  │
│ Ensemble Formula:                                                │
│ Final Score = (100 × 0.4) + (85 × 0.6)                          │
│             = 40 + 51                                            │
│             = 91/100                                             │
│                                                                  │
│ FINAL RISK SCORE = 91/100                                        │
│ STATUS: LIKELY PHISHING ✗                                        │
│ CONFIDENCE: 91%                                                  │
│                                                                  │
│ Why this score?                                                  │
│ • Multiple phishing keywords (login, verify, confirm)           │
│ • Suspicious free TLD (.tk)                                     │
│ • URL contains @ symbol                                         │
│ • Long parameter string with email                              │
│ • Pattern matches known phishing attacks                        │
│ • Deep learning model learned this is dangerous                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

FEATURE ANALYSIS DISPLAY:
┌────────────────────────────────────────────────────────────┐
│                                                             │
│ FEATURE ANALYSIS                        Total Risk: 145 pts│
│                                                             │
│ URL Length                           ✗ +15 pts            │
│ "59 characters - longer than normal"                       │
│                                                             │
│ HTTPS Protocol                       ✓ +0 pts             │
│ "Present - Secure connection"                              │
│                                                             │
│ @ Symbol Detection                   ✗ +35 pts            │
│ "1 @ symbol found - Very suspicious!"                      │
│                                                             │
│ Suspicious TLD                       ✗ +35 pts            │
│ ".tk TLD detected - Free & suspicious"                     │
│                                                             │
│ Phishing Keywords                    ✗ +20 pts            │
│ "login, verify, confirm detected"                          │
│                                                             │
│ Parameter Complexity                 ✗ +40 pts            │
│ "3 parameters with suspicious values"                      │
│                                                             │
│ ... (8 more features)                                      │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

This comprehensive architecture provides:
1. **High Accuracy** - Ensemble of heuristics + deep learning
2. **User Transparency** - Detailed feature analysis showing WHY
3. **Scalability** - Separate services can be scaled independently
4. **Reliability** - Multiple layers of analysis, fallback mechanisms
5. **Speed** - Parallel heuristic + DL analysis, caching support

