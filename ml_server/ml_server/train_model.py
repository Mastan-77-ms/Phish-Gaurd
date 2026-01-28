import pandas as pd
import joblib
import time
import os
import sys
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# CONFIG
DATASET_PATH = "phishing_data.csv"
MODEL_FILE = "phishing_model.pkl"

def train():
    print("--- [STEP 2] TRAINING MODEL ---")
    
    # 1. Load Data
    if not os.path.exists(DATASET_PATH):
        print(f"❌ Error: '{DATASET_PATH}' not found. Please run 'get_data.py' first!")
        return

    print(f"Loading {DATASET_PATH}...")
    try:
        df = pd.read_csv(DATASET_PATH)
        print(f"Original Columns found: {list(df.columns)}")
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return

    # --- AUTO-FIX COLUMN NAMES (The Self-Healing Part) ---
    # 1. Clean whitespace from column names
    df.columns = [c.strip() for c in df.columns]
    
    # 2. Find the Label column
    label_col = None
    possible_label_names = ['label', 'status', 'phishing', 'class', 'type', 'result']
    
    for col in df.columns:
        if col.lower() in possible_label_names:
            label_col = col
            break
            
    # Fallback: If no name matches, assume the last column is the label
    if not label_col:
        label_col = df.columns[-1]

    if not label_col:
        print("❌ Critical Error: Could not identify Label column.")
        print(f"Columns in file: {list(df.columns)}")
        sys.exit(1)

    print(f"✅ Using '{label_col}' as Label column")
    df.rename(columns={label_col: 'Label'}, inplace=True)
    # ---------------------------------------------------------

    # 2. Normalize Labels (0=Safe, 1=Phishing)
    df['Label'] = df['Label'].astype(str).str.lower()
    label_map = {
        '0': 0, 'good': 0, 'safe': 0, 'benign': 0,
        '1': 1, 'bad': 1, 'phishing': 1, 'malicious': 1
    }
    df['target'] = df['Label'].map(label_map)
    
    # Remove rows we couldn't understand
    df.dropna(subset=['target'], inplace=True)
    print(f"Training on {len(df)} valid rows...")

    # 3. Prepare features (drop Label column, use all feature columns)
    print("Preparing feature matrix...")
    X = df.drop(columns=['Label', 'target'])
    y = df['target'].astype(int)
    vectorizer = None

    # 4. Train
    print("Training Random Forest...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=60, n_jobs=-1)
    model.fit(X_train, y_train)

    # 5. Save
    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"✅ Model Trained! Accuracy: {acc*100:.2f}%")
    
    joblib.dump({"model": model, "vectorizer": vectorizer, "feature_names": list(X.columns)}, MODEL_FILE)
    print(f"✅ Saved to '{MODEL_FILE}'")

if __name__ == "__main__":
    train()