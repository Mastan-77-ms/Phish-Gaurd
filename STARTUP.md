# PhishGuard - Complete Startup and Quick Reference Guide

> **Start Here!** This guide consolidates all setup instructions for the PhishGuard Deep Learning Phishing Detection System.

---

## 🚀 Quick Start (2 Minutes)

### For First Time Users (RECOMMENDED)

```bash
# Option 1: Interactive Setup Wizard (Easiest)
cd ml_server/ml_server
python quick_start.py
# Then follow the prompts and select option "5" for full setup
```

### For Experienced Users (Manual Setup)

```bash
# Terminal 1: ML Server
cd ml_server/ml_server
pip install -r requirements.txt
python train_dl_model.py  # Train the model (1-5 min)
python app.py              # Start ML server

# Terminal 2: Backend
cd backend/backend
npm install
npm start

# Terminal 3: Frontend
cd frontend/phish-app2
npm install
npm run dev

# Browser: Open http://localhost:5173
```

---

## 📋 System Architecture

### Services & Ports

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| **Frontend** | 5173 | http://localhost:5173 | React Web UI |
| **Backend** | 3000 | http://localhost:3000 | Express API Server |
| **ML Server** | 8000 | http://localhost:8000 | FastAPI + Deep Learning |
| **FastAPI Docs** | 8000 | http://localhost:8000/docs | API Documentation |
| **MongoDB** | 27017 | mongodb://localhost:27017 | Database |

### Ensemble Scoring Architecture

```
┌──────────────────────────────────┐
│       Input URL                  │
└──────────┬───────────────────────┘
           │
    ┌──────┴───────┐
    │              │
    ▼              ▼
┌──────────┐  ┌───────────────┐
│Heuristic │  │Deep Learning  │
│Analysis  │  │Neural Network │
│(40%)     │  │(60%)          │
└────┬─────┘  └───────┬───────┘
     │                │
     └────────┬───────┘
              │
         ┌────▼──────┐
         │  Ensemble │
         │  Scoring  │
         └────┬──────┘
              │
     ┌────────▼─────────┐
     │ Risk Score (0-100)│
     └──────────────────┘
```

---

## 📝 Detailed Setup Instructions

### Step 1: Prerequisites

Before starting, verify you have:

```bash
# Check Python (3.8+)
python --version

# Check Node.js (16+)
node --version
npm --version

# Check MongoDB is running (if local)
# Windows: mongod should be running in background
# Linux/Mac: mongod or brew services start mongodb-community
```

### Step 2: ML Server Setup (Python)

The ML server runs the deep learning model and heuristic analysis.

```bash
# Navigate to ML server
cd ml_server/ml_server

# Install dependencies
pip install -r requirements.txt
# Key packages: tensorflow, flask, numpy, pandas, requests

# Train the deep learning model (IMPORTANT - First time only)
python train_dl_model.py

# Expected output:
# Generating synthetic data...
# Building neural network...
# Training model...
# Epoch 1/10
# Epoch 2/10
# ...
# Model saved to: phishing_dl_model.h5
# Scaler saved to: feature_scaler.pkl

# Wait for completion (1-5 minutes depending on system)
```

**Verify Training Completed:**
- Check for `phishing_dl_model.h5` in ml_server/ml_server/
- Check for `feature_scaler.pkl` in ml_server/ml_server/

### Step 3: Backend Setup (Node.js)

The backend provides the REST API and database integration.

```bash
# Navigate to backend
cd backend/backend

# Install dependencies
npm install

# Update MongoDB connection if needed (edit db.js):
# Local: mongodb://localhost:27017/phishguard
# Atlas: mongodb+srv://user:pass@cluster...

# Verify structure:
# ✓ server.js
# ✓ db.js (with correct MongoDB URI)
# ✓ models/Scan.js
# ✓ models/ScanHistory.js
```

### Step 4: Frontend Setup (React + Vite)

The frontend provides the web user interface.

```bash
# Navigate to frontend
cd frontend/phish-app2

# Install dependencies
npm install

# Check configuration in vite.config.js:
# - Port should be 5173
# - Verify backend API URL is http://localhost:3000

# Optional: Check environment
# VITE_API_URL=http://localhost:3000 npm run dev
```

### Step 5: Running the System

Open **3 separate terminals** and start each service:

#### Terminal 1: ML Server
```bash
cd ml_server/ml_server
python app.py

# Expected output:
# [STARTUP] PhishGuard API Ready!
# Uvicorn running on http://127.0.0.1:8000
# FastAPI docs: http://localhost:8000/docs
```

#### Terminal 2: Backend Server
```bash
cd backend/backend
npm start

# Expected output:
# Server running on port 3000
# MongoDB connected successfully
# API ready for requests
```

#### Terminal 3: Frontend Server
```bash
cd frontend/phish-app2
npm run dev

# Expected output:
# VITE v4.x.x  ready in xxx ms
# ➜  Local:   http://localhost:5173/
# ➜  press h + enter to show help
```

#### Browser: Open Application
```
http://localhost:5173
```

---

## ✅ Verification Checklist

After starting all 3 services:

- [ ] Frontend loads at http://localhost:5173
- [ ] Can enter a URL and get analysis
- [ ] Risk score displays (0-100)
- [ ] Feature analysis shows 14 features
- [ ] History shows previous scans
- [ ] No console errors in browser
- [ ] ML Server logs show prediction scores
- [ ] Backend logs show API requests

### Test URLs

Use these URLs to verify the system:

```
✓ SAFE URLs:
  https://www.google.com (Score: 10-20, Status: SAFE)
  https://www.github.com (Score: 15-25, Status: SAFE)

⚠ SUSPICIOUS URLs:
  https://login.example.com (Score: 40-60, Status: SUSPICIOUS)
  https://secure-update.online (Score: 50-70, Status: SUSPICIOUS)

🚨 PHISHING URLs:
  https://login-verify-google.tk (Score: 80-95, Status: PHISHING)
  https://confirm-paypal-secure.xyz (Score: 85-100, Status: PHISHING)
```

---

## 🧪 Testing & Verification

### Run Comprehensive Tests

```bash
# Test the full system flow
cd c:\Mini-Project-fsd\pi
python test_system.py

# Test ML server only
cd ml_server/ml_server
python test_ml.py

# Verify system setup
python verify_system.py
```

### Test API Directly

```bash
# Test ML server endpoint
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# View API documentation
# Open: http://localhost:8000/docs

# Test backend API
curl -X POST http://localhost:3000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Get scan history
curl http://localhost:3000/api/history
```

---

## 📊 Deep Learning Integration Explained

### The 14 URL Features Analyzed

1. **URL Length** - Phishing URLs often have unusual lengths
2. **Domain Length** - Legit domains typically 10-20 chars
3. **Subdomain Count** - Multiple subdomains = suspicious
4. **Hyphen Count** - Common in phishing URLs
5. **Protocol Security** - HTTPS > HTTP
6. **Query Parameter Count** - Too many = suspicious
7. **Path Segments** - Deep paths suggest complexity
8. **Special Characters** - @, !, %, etc. = risky
9. **Numeric Characters** - Excessive numbers = suspicious
10. **IP Address Usage** - Direct IPs are phishing red flag
11. **TLD Suspicion** - .tk, .xyz, .click are often phishing
12. **Entropy Score** - Randomness indicates obfuscation
13. **Encoding Detection** - URL encoding can hide malware
14. **Suspicious Keywords** - login, verify, confirm, update, etc.

### Ensemble Scoring Formula

```
Final Risk Score = (Heuristic Score × 0.4) + (DL Prediction × 0.6)

Where:
- Heuristic Score = Rule-based analysis (0-100)
- DL Prediction = Neural network output (0-100)

Risk Classifications:
- 0-30:   SAFE ✓ (Low risk)
- 31-60:  SUSPICIOUS ⚠ (Medium risk)
- 61-100: PHISHING 🚨 (High risk - block immediately)
```

### Neural Network Architecture

```
Input Layer (14 features)
    ↓
Dense(64) + ReLU + Dropout(0.3) + BatchNorm
    ↓
Dense(32) + ReLU + Dropout(0.2) + BatchNorm
    ↓
Dense(16) + ReLU + Dropout(0.1)
    ↓
Dense(1) + Sigmoid (Output: 0-1)
    ↓
Scale to 0-100 Risk Score

Training Configuration:
- Optimizer: Adam (learning_rate=0.001)
- Loss: Binary Crossentropy
- Metrics: Accuracy, Precision, Recall, AUC
- Epochs: 10
- Batch Size: 32
- Validation Split: 20%
```

---

## 🐛 Troubleshooting

### "Port X already in use"

```bash
# Windows - Find and kill process using port
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5173
kill -9 <PID>
```

### "ModuleNotFoundError: No module named 'tensorflow'"

```bash
cd ml_server/ml_server
pip install tensorflow
# Or for GPU support: pip install tensorflow-gpu
```

### "MongoDB connection refused"

```bash
# Check if MongoDB is running
# Windows: Run mongod from Command Prompt or Services
# Linux: sudo systemctl start mongodb
# Mac: brew services start mongodb-community

# Or update to remote MongoDB Atlas connection in db.js
```

### "phishing_dl_model.h5 not found"

```bash
# Train the model first
cd ml_server/ml_server
python train_dl_model.py

# Wait for completion before starting app.py
```

### "Frontend shows blank page"

```bash
# Check browser console (F12) for errors
# Check backend is running (http://localhost:3000/api/scan should work)
# Check ML server is running (http://localhost:8000/docs should load)
# Clear browser cache: Ctrl+Shift+Delete
```

### "Risk scores not displaying"

```bash
# Verify ML server is responding
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Check browser console for errors
# Verify CORS is enabled in backend
```

### "Different scores on rescan"

This is **normal behavior**! The system may give slightly different scores due to:
- Random elements in neural network initialization
- Different feature extraction timing
- Database state changes

To get consistent scores, restart all services and clear cache.

---

## 📂 Project Structure

```
PhishGuard/
├── README.md                        (Start here)
├── STARTUP.md                       (This file - Complete setup guide)
├── QUICK_REFERENCE.md              (2-page cheat sheet)
│
├── ml_server/ml_server/             (Python - Deep Learning)
│   ├── app.py                       (FastAPI + Ensemble scoring)
│   ├── deep_learning_model.py       (Neural network definition)
│   ├── train_dl_model.py            (Training pipeline)
│   ├── requirements.txt             (Python dependencies)
│   ├── phishing_dl_model.h5         (Trained model - generated)
│   ├── feature_scaler.pkl           (Feature normalizer - generated)
│   ├── test_ml.py                   (ML server tests)
│   └── [other files...]
│
├── backend/backend/                 (Node.js - API & Database)
│   ├── server.js                    (Express server)
│   ├── db.js                        (MongoDB connection)
│   ├── package.json                 (Dependencies)
│   ├── models/
│   │   ├── Scan.js                 (Scan data model)
│   │   └── ScanHistory.js          (History data model)
│   └── [other files...]
│
├── frontend/phish-app2/             (React - Web UI)
│   ├── src/
│   │   ├── App.jsx                 (Main component)
│   │   ├── Dashboard.jsx           (History & stats)
│   │   ├── FeatureAnalysis.jsx     (14 features display)
│   │   ├── Header.jsx              (Navigation)
│   │   └── [styles...]
│   ├── package.json                (Dependencies)
│   ├── vite.config.js              (Build configuration)
│   └── [other files...]
│
├── test_system.py                   (Comprehensive system tests)
└── [documentation files...]
```

---

## 🎯 Key Files Reference

### Must-Know Python Files (ML Server)
- `app.py` - Main API server with ensemble scoring
- `train_dl_model.py` - Train the neural network
- `test_ml.py` - Run ML server tests
- `requirements.txt` - Python dependencies to install

### Must-Know Node Files (Backend)
- `server.js` - Express API with all endpoints
- `db.js` - MongoDB connection configuration
- `models/Scan.js` - URL scan data model
- `models/ScanHistory.js` - Historical scan records

### Must-Know React Files (Frontend)
- `App.jsx` - Main application component
- `Dashboard.jsx` - History and statistics display
- `FeatureAnalysis.jsx` - Shows 14 URL features
- `vite.config.js` - Build and dev server config

---

## 🚀 Advanced Topics

### Training a Custom Model

```bash
cd ml_server/ml_server

# Generate your own training data
python create_sample_data.py --samples 10000 --output custom_urls.csv

# Train with custom data
python train_dl_model.py --data custom_urls.csv --epochs 20
```

### Adjusting Ensemble Weights

Edit `ml_server/ml_server/app.py`:
```python
# Current: 40% heuristic, 60% deep learning
HEURISTIC_WEIGHT = 0.4
DL_WEIGHT = 0.6

# Change to: 50% heuristic, 50% deep learning
HEURISTIC_WEIGHT = 0.5
DL_WEIGHT = 0.5
```

### Using Remote MongoDB

Edit `backend/backend/db.js`:
```javascript
// Replace this:
const uri = "mongodb://localhost:27017/phishguard";

// With your MongoDB Atlas URI:
const uri = "mongodb+srv://username:password@cluster.mongodb.net/phishguard";
```

---

## 📞 Support & Questions

- **Quick help**: Check the [QUICK_REFERENCE.md](QUICK_REFERENCE.md) 2-page guide
- **Deep learning details**: See [ml_server/ml_server/DEEP_LEARNING_GUIDE.md](ml_server/ml_server/DEEP_LEARNING_GUIDE.md)
- **System architecture**: See [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)
- **API reference**: Open http://localhost:8000/docs when ML server is running

---

## ✨ What You Get

### Core Features
- ✅ Deep Learning Neural Network (TensorFlow/Keras)
- ✅ Heuristic Rule-Based Analysis
- ✅ Ensemble Scoring (Combined predictions)
- ✅ 14-Feature URL Analysis
- ✅ Risk Score (0-100) and Classifications
- ✅ Scan History Database
- ✅ Real-time Dashboard
- ✅ Responsive Web UI

### Production Ready
- ✅ Error handling and validation
- ✅ Database persistence
- ✅ API documentation (Swagger/OpenAPI)
- ✅ Comprehensive logging
- ✅ Test suites
- ✅ Security checks
- ✅ Performance optimization

---

## 🎓 Learning Resources

### Understanding Phishing Detection
- [OWASP Phishing Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Phishing_Prevention_Cheat_Sheet.html)
- [URL Structure Analysis](https://en.wikipedia.org/wiki/URL)

### Deep Learning & Neural Networks
- [TensorFlow Documentation](https://www.tensorflow.org/)
- [Keras Sequential Models](https://keras.io/guides/sequential_model/)

### Web Development
- [React Documentation](https://react.dev/)
- [Express.js Guide](https://expressjs.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)

---

**Last Updated**: January 2026  
**Version**: 1.0  
**Status**: Production Ready ✅

---

**Next Steps**:
1. Follow the Quick Start section above
2. Verify all services are running
3. Test with the provided test URLs
4. Explore the Dashboard and Features
5. Read the [README.md](README.md) for more information
