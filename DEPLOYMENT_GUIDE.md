# PhishGuard Enhancement Deployment Guide

## Pre-Deployment Checklist

- [ ] All services backed up
- [ ] Test environment ready
- [ ] Database backups taken
- [ ] Development team notified
- [ ] Maintenance window scheduled

---

## Step 1: Update ML Server

### Files to Update
- `ml_server/ml_server/app.py`

### What Changed
1. Added `import json` at top
2. Added UNSAFE_CHARS dictionary to PhishingEngine class
3. Added `_check_unsafe_characters()` method
4. Added `_check_protocol()` method
5. Updated `predict()` method with risk boosting logic
6. Updated `log_scan()` method signature and implementation
7. Updated database schema (add risk_reasons column)
8. Updated ScanResult model

### Deployment Steps
```bash
# 1. Backup current app.py
cp ml_server/ml_server/app.py ml_server/ml_server/app.py.backup

# 2. Replace with new version
# [Copy updated app.py]

# 3. Delete old database to regenerate schema
rm ml_server/ml_server/scan_history.db

# 4. Restart ML server
# (It will auto-create new schema on first run)
```

### Verification
```bash
# Test endpoint returns risk_reasons
curl -X POST http://localhost:8000/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{"url":"http://example.com"}'

# Should include risk_reasons array in response
```

---

## Step 2: Update Backend API

### Files to Update
- `backend/backend/server.js`
- `backend/backend/models/Scan.js`
- `backend/backend/models/ScanHistory.js`

### What Changed
1. POST /api/scan endpoint enhanced
2. risk_reasons field added to models
3. Database operations store risk_reasons

### Deployment Steps
```bash
# 1. Backup current files
cp backend/backend/server.js backend/backend/server.js.backup
cp backend/backend/models/Scan.js backend/backend/models/Scan.js.backup
cp backend/backend/models/ScanHistory.js backend/backend/models/ScanHistory.js.backup

# 2. Replace with new versions
# [Copy updated files]

# 3. Restart backend service
# npx nodemon server.js (or your startup command)
```

### Database Migration
**Note**: MongoDB will accept new fields automatically

```javascript
// Optional: Update existing records with empty risk_reasons
db.scans.updateMany({}, { $set: { risk_reasons: [] } });
db.scanhistories.updateMany({}, { $set: { risk_reasons: [] } });
```

### Verification
```bash
# Test API returns risk_reasons
curl -X POST http://localhost:3001/api/scan \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'

# Should include risk_reasons in response
```

---

## Step 3: Update Frontend

### Files to Update
- `frontend/phish-app2/src/App.jsx`
- `frontend/phish-app2/src/App.css`

### What Changed
1. App.jsx enhanced to capture risk_reasons
2. Result display section added for risk_reasons
3. CSS styling added for risk_reasons display

### Deployment Steps
```bash
# 1. Backup current files
cp frontend/phish-app2/src/App.jsx frontend/phish-app2/src/App.jsx.backup
cp frontend/phish-app2/src/App.css frontend/phish-app2/src/App.css.backup

# 2. Replace with new versions
# [Copy updated files]

# 3. Rebuild frontend
cd frontend/phish-app2
npm run build

# 4. Restart dev server or deploy build
npm run dev
```

### Verification
1. Open app in browser
2. Scan a URL
3. Verify risk_reasons display section appears (if reasons exist)
4. Check console for no errors

---

## Step 4: Test All Changes

### Run Test Suite
```bash
python test_unsafe_characters.py
```

Expected output:
```
================================================================================
Testing Unsafe Character Detection and Protocol Validation
================================================================================

Test: Safe HTTPS URL
URL: https://example.com
Risk Score: 15%
Status: SAFE
Risk Reasons: 0 reason(s)
✅ PASSED: Score is valid (LOW risk)

[... more tests ...]

================================================================================
Results: 12 passed, 0 failed out of 12 tests
================================================================================
```

### Manual Testing

#### Test Case 1: Safe URL
```
Input: https://google.com
Expected: Score < 30, no reasons, SAFE status
Check: UI shows green checkmark, no warnings
```

#### Test Case 2: HTTP Protocol
```
Input: http://example.com
Expected: Score 35-50, "http" reason, SUSPICIOUS status
Check: UI shows warning, reason visible
```

#### Test Case 3: Unsafe Character
```
Input: https://example.com/path<script>
Expected: Score 70-80, "Less Than" reason, PHISHING status
Check: UI shows red warning section with reason
```

#### Test Case 4: Multiple Issues
```
Input: http://example.com/path with"space
Expected: Score 80, 3 reasons, PHISHING status
Check: UI shows all reasons listed
```

---

## Step 5: Monitor & Validate

### Check Logs
```bash
# ML Server logs
tail -f ml_server/logs/app.log

# Backend logs
tail -f backend/logs/server.log

# Frontend console (browser DevTools)
```

### Database Validation
```bash
# ML Server (SQLite)
sqlite3 ml_server/ml_server/scan_history.db
> SELECT COUNT(*), COUNT(risk_reasons) FROM scan_history;
# Should show same count in both columns (all have reasons)

# Backend (MongoDB)
db.scans.findOne({}, { risk_reasons: 1 })
db.scanhistories.findOne({}, { risk_reasons: 1 })
# Both should have risk_reasons array
```

### Performance Monitoring
- Monitor response times (should be < 10ms overhead)
- Check database growth (minor increase from JSON storage)
- Monitor CPU/memory (no significant change)

---

## Rollback Procedure

### If Major Issues Occur

#### Option 1: Quick Rollback
```bash
# 1. Restore backups
cp ml_server/ml_server/app.py.backup ml_server/ml_server/app.py
cp backend/backend/server.js.backup backend/backend/server.js
cp frontend/phish-app2/src/App.jsx.backup frontend/phish-app2/src/App.jsx
cp frontend/phish-app2/src/App.css.backup frontend/phish-app2/src/App.css

# 2. Restart services
# [Restart all services]

# 3. Test connectivity
curl http://localhost:8000/api/v1/health
curl http://localhost:3001/api/health (if available)
```

#### Option 2: Database Rollback
```bash
# ML Server (SQLite)
# Delete risk_reasons column (optional)
sqlite3 ml_server/ml_server/scan_history.db
> ALTER TABLE scan_history DROP COLUMN risk_reasons;

# Backend (MongoDB)
# Remove risk_reasons field (optional)
db.scans.updateMany({}, { $unset: { risk_reasons: 1 } });
db.scanhistories.updateMany({}, { $unset: { risk_reasons: 1 } });
```

---

## Deployment Schedule

### Recommended Timeline

**Day 1: Preparation**
- [ ] Backup all systems
- [ ] Notify team
- [ ] Schedule maintenance window

**Day 2: Staging Deployment**
- [ ] Deploy to staging environment
- [ ] Run full test suite
- [ ] Manual testing
- [ ] Review logs

**Day 3: Production Deployment** (Off-peak hours)
- [ ] Deploy ML Server
- [ ] Verify ML Server healthy
- [ ] Deploy Backend
- [ ] Verify Backend connected
- [ ] Deploy Frontend
- [ ] Verify Frontend loads
- [ ] Run smoke tests
- [ ] Monitor for 1 hour

**Day 4: Validation**
- [ ] Check all logs
- [ ] Validate database
- [ ] Performance metrics
- [ ] User acceptance testing

---

## Post-Deployment Tasks

### Monitoring (First Week)
- [ ] Daily log reviews
- [ ] Performance metric tracking
- [ ] Error rate monitoring
- [ ] User feedback collection

### Documentation
- [ ] Update deployment docs
- [ ] Update API documentation
- [ ] Notify users of changes
- [ ] Archive old documentation

### Analytics
- [ ] Track unsafe character detections
- [ ] Monitor HTTP protocol usage
- [ ] Analyze risk score distribution
- [ ] Review user feedback

---

## Support Resources

### If Issues Arise
1. **Check Logs**: Look for specific error messages
2. **Run Tests**: Execute test_unsafe_characters.py
3. **Verify Connectivity**: Test all endpoints
4. **Database Check**: Validate data integrity
5. **Rollback**: Follow rollback procedure if needed

### Contact Points
- ML Server Issues: Check logs in ml_server/
- Backend Issues: Check logs in backend/
- Frontend Issues: Browser console (F12)
- Database Issues: Use respective DB tools

### Common Issues & Solutions

**Issue**: Score always 50%
- **Cause**: ML model not loading
- **Fix**: Check model file exists, permissions correct

**Issue**: risk_reasons empty
- **Cause**: No unsafe characters or protocol issues
- **Fix**: This is normal behavior

**Issue**: Frontend not updating
- **Cause**: Old build cached
- **Fix**: Clear browser cache, hard refresh (Ctrl+Shift+R)

**Issue**: Database errors
- **Cause**: Schema mismatch
- **Fix**: Delete ML server database, restart (auto-recreates)

---

## Success Criteria

All items should be true after deployment:

- [ ] ML server returns risk_reasons in all responses
- [ ] Backend stores risk_reasons in database
- [ ] Frontend displays risk_reasons when present
- [ ] Test suite passes all 12 tests
- [ ] No errors in application logs
- [ ] Response times normal (< 100ms)
- [ ] Database integrity verified
- [ ] Users can access application
- [ ] Score always 0-100 (never missing)
- [ ] Low-risk URLs stored on rescan
- [ ] Safe URLs stored on rescan

---

## Final Verification Command

Run this to verify full deployment:

```bash
# 1. Test ML Server
echo "Testing ML Server..."
curl -s -X POST http://localhost:8000/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{"url":"http://phishing.example.com"}' | grep -q "risk_reasons" && echo "✅ ML Server OK" || echo "❌ ML Server FAILED"

# 2. Test Backend
echo "Testing Backend..."
curl -s -X POST http://localhost:3001/api/scan \
  -H "Content-Type: application/json" \
  -d '{"url":"http://phishing.example.com"}' | grep -q "risk_reasons" && echo "✅ Backend OK" || echo "❌ Backend FAILED"

# 3. Test Frontend
echo "Frontend: Open http://localhost:5173 and verify UI loads"

# 4. Run Tests
echo "Running test suite..."
python test_unsafe_characters.py
```

---

## Deployment Complete!

When all steps are verified:
- Update deployment status
- Notify stakeholders
- Begin post-deployment monitoring
- Schedule team debrief
