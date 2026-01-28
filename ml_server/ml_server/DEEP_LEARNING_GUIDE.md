# PhishGuard - Deep Learning Integration Guide

## Overview

PhishGuard now uses an **ensemble approach** combining:
1. **Heuristic Analysis** (40% weight) - Rule-based feature extraction
2. **Deep Learning Neural Network** (60% weight) - TensorFlow/Keras model

This combination provides better accuracy in detecting phishing URLs compared to either method alone.

---

## Architecture

### Deep Learning Model

**Neural Network Structure:**
```
Input Layer (14 features)
    ↓
Dense(64, relu) + Dropout(0.3) + BatchNorm
    ↓
Dense(32, relu) + Dropout(0.2) + BatchNorm
    ↓
Dense(16, relu) + Dropout(0.1)
    ↓
Dense(1, sigmoid) → Output: Phishing Probability (0-1)
```

**Model Configuration:**
- **Optimizer**: Adam (learning_rate=0.001)
- **Loss Function**: Binary Crossentropy
- **Metrics**: BinaryAccuracy, Precision, Recall, AUC
- **Input Features**: 14 URL characteristics
- **Output**: Phishing probability (converted to 0-100 score)

### Feature Set (14 Features)

The model analyzes these URL characteristics:

1. **qty_dot_url** - Number of dots in full URL
2. **qty_hyphen_url** - Number of hyphens in URL
3. **qty_underline_url** - Number of underscores in URL
4. **qty_slash_url** - Number of slashes in URL
5. **qty_questionmark_url** - Number of query parameters
6. **qty_equal_url** - Number of equal signs (parameter assignments)
7. **qty_at_url** - Number of @ symbols (rare in legitimate URLs)
8. **qty_and_url** - Number of & symbols (parameter separators)
9. **qty_exclamation_url** - Number of exclamation marks
10. **qty_space_url** - Number of spaces
11. **qty_tilde_url** - Number of tildes
12. **qty_comma_url** - Number of commas
13. **qty_plus_url** - Number of plus signs
14. **qty_asterisk_url** - Number of asterisks

### Ensemble Scoring

```
Final Score = (Heuristic Score × 0.4) + (DL Score × 0.6)
```

**Example:**
- Heuristic Analysis: 75/100
- Deep Learning Model: 85/100
- Ensemble Score: (75 × 0.4) + (85 × 0.6) = 30 + 51 = **81/100**

---

## Setup and Training

### 1. Install Dependencies

```bash
cd ml_server/ml_server
pip install -r requirements.txt
```

**Required packages:**
- fastapi
- uvicorn
- tensorflow (>= 2.10)
- keras
- scikit-learn
- pandas
- numpy
- joblib

### 2. Train the Deep Learning Model

```bash
python train_dl_model.py
```

**What this does:**
- Generates synthetic training data (1000 samples by default)
- OR loads real data from `phishing_data.csv` if available
- Splits data into train/validation/test sets (60/20/20)
- Trains the neural network for 50 epochs
- Saves the trained model to `phishing_dl_model.h5`
- Saves the feature scaler to `feature_scaler.pkl`

**Expected output:**
```
[TRAINING] Starting Deep Learning Model Training...
[TRAINING] Using synthetic training data
Generated 1000 training samples
Safe URLs: 500
Phishing URLs: 500

Data split:
  Training: 640 samples
  Validation: 160 samples
  Testing: 200 samples

[TRAINING] Training the Deep Learning Model...
Epoch 1/50
32/20 [==============================] - 0s 2ms/step - loss: 0.6932 - ...
...
[EVALUATION] Evaluating on Test Set...
[COMPLETE] Deep Learning Model Training Complete!
```

### 3. Verify Files

After training, check that these files exist in `ml_server/ml_server/`:
- `phishing_dl_model.h5` - Trained neural network
- `feature_scaler.pkl` - Feature normalization scaler
- `phishing_model.pkl` - Traditional ML model (if available)

---

## Running the System

### Start the ML Server

```bash
cd ml_server/ml_server
python app.py
```

**Output:**
```
[STARTUP] PhishGuard API Ready!
[STARTUP] Available endpoints:
  POST  /scan - Scan a URL
  GET   /history - Get scan history
  GET   /stats - Get dashboard stats

Uvicorn running on http://127.0.0.1:8000
```

### Start the Backend

```bash
cd backend/backend
npm install
npm start
```

### Start the Frontend

```bash
cd frontend/phish-app2
npm install
npm run dev
```

---

## Testing the Integration

### Test ML Server Only

```bash
python test_ml_endpoint.py
```

### Test Full System (ML + Backend + Frontend)

```bash
python test_dl_integration.py
```

This tests:
- ML server deep learning predictions
- Backend API integration
- Ensemble score calculation
- Feature analysis output

**Sample test output:**
```
[TEST] Suspicious free TLD with login keywords
       URL: https://login-verify-google.tk/verify?user=admin@gmail.com&pass=123
       Status: phishing
       Risk Score: 78/100
       Risk Label: LIKELY PHISHING
       Response Time: 0.042s
       Features Analyzed: 14 features
       Total Feature Risk: 125
```

---

## API Endpoints

### POST /scan
Scans a URL using ensemble method

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "url": "https://example.com",
  "status": "safe",
  "risk_score": 15,
  "risk_label": "LIKELY SAFE",
  "response_time": 0.032,
  "features": {
    "url_length": {
      "value": 18,
      "safe": true,
      "icon": "✓",
      "risk_score": 0
    },
    ...
  }
}
```

**How it works:**
1. Extract URL features (14-dimensional feature vector)
2. Get heuristic score from rule-based analysis
3. Get deep learning score from neural network
4. Combine using ensemble weights (40% + 60%)
5. Generate detailed feature analysis
6. Return combined score and features

### GET /history
Returns scan history

### GET /stats
Returns dashboard statistics

---

## Understanding the Predictions

### Risk Score Interpretation

```
0-30:    LIKELY SAFE          ✓ Green
31-60:   SUSPICIOUS            ⚠ Yellow
61-100:  LIKELY PHISHING       ✗ Red
```

### Feature Analysis

Each feature shows:
- **Value**: The actual count/measurement from the URL
- **Safe**: Whether this feature indicates phishing (True/False)
- **Icon**: Visual indicator (✓ safe, ✗ suspicious)
- **Risk Score**: Points added to total risk (0-100)

**Example:**
```
URL Length: 42 characters
  Safe: true
  Risk Score: 0 points  ✓

Suspicious Characters (@): 1 found
  Safe: false
  Risk Score: 35 points  ✗
```

---

## Model Performance Metrics

The trained model tracks:

1. **Binary Accuracy** - Percentage of correct predictions
2. **Precision** - Of predicted phishing, how many are actually phishing
3. **Recall** - Of actual phishing URLs, how many were caught
4. **AUC (Area Under Curve)** - Overall model performance

**Expected performance (with good training data):**
- Accuracy: > 85%
- Precision: > 80%
- Recall: > 80%
- AUC: > 0.90

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'tensorflow'"

```bash
pip install tensorflow
```

### "phishing_dl_model.h5 not found"

The model hasn't been trained yet. Run:
```bash
python train_dl_model.py
```

### "Port 8000 already in use"

The ML server is already running. Check:
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

Kill the process and restart.

### Low accuracy or wrong predictions

The model might need:
1. **More training data** - Use a larger dataset
2. **Better hyperparameters** - Adjust learning_rate, epochs, layer sizes
3. **More features** - Add domain age, SSL certificate analysis, etc.
4. **Different weights** - Try different ensemble ratios (not 40/60)

---

## Customization

### Adjust Ensemble Weights

Edit `ml_server/ml_server/app.py`, line ~585:

```python
# Current: 40% heuristic, 60% deep learning
ensemble_score = int((heuristic_score * 0.4) + (dl_score * 0.6))

# Example: 50% heuristic, 50% deep learning
ensemble_score = int((heuristic_score * 0.5) + (dl_score * 0.5))

# Example: 30% heuristic, 70% deep learning
ensemble_score = int((heuristic_score * 0.3) + (dl_score * 0.7))
```

### Add More Features

In `ml_server/ml_server/deep_learning_model.py`:

```python
# Change input shape from (14,) to match new feature count
layers.Input(shape=(20,)),  # If adding 6 more features
```

### Modify Neural Network Architecture

In `deep_learning_model.py`, `create_model()` method:

```python
# Add more layers
layers.Dense(128, activation='relu', name='hidden_1'),
layers.Dropout(0.4),
layers.BatchNormalization(),
layers.Dense(64, activation='relu', name='hidden_2'),
layers.Dropout(0.3),
layers.BatchNormalization(),
# ... more layers
```

---

## File Structure

```
ml_server/ml_server/
├── app.py                      # FastAPI server with ensemble prediction
├── deep_learning_model.py      # Neural network implementation
├── train_dl_model.py           # Training script
├── test_dl_integration.py      # Integration tests
├── requirements.txt            # Python dependencies
├── phishing_dl_model.h5        # Trained model (generated after training)
├── feature_scaler.pkl          # Feature normalization (generated after training)
└── phishing_model.pkl          # Traditional ML model (if available)
```

---

## Next Steps

1. ✅ **Train the model**: `python train_dl_model.py`
2. ✅ **Start ML server**: `python app.py`
3. ✅ **Test integration**: `python test_dl_integration.py`
4. ✅ **Run full system**: Start backend and frontend
5. 📊 **Monitor performance**: Check accuracy metrics in logs
6. 🔄 **Retrain periodically**: With new phishing examples

---

## References

- **TensorFlow/Keras**: https://www.tensorflow.org/
- **Binary Classification**: https://en.wikipedia.org/wiki/Binary_classification
- **Ensemble Methods**: https://en.wikipedia.org/wiki/Ensemble_learning
- **Phishing Detection**: https://en.wikipedia.org/wiki/Phishing

---

**Last Updated**: 2024
**Version**: 1.0 with Deep Learning Integration
