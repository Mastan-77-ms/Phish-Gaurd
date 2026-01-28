import pandas as pd
import requests
import io
import os

# Verified Source: Raw URLs + Labels
DATA_URL = "https://raw.githubusercontent.com/GregaVrbancic/Phishing-Dataset/master/dataset_small.csv"
OUTPUT_FILE = "phishing_data.csv"

def get_data():
    print("--- DOWNLOADING CORRECT DATA ---")
    
    # 1. Force remove old file if it exists
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
        print("Deleted old bad file.")

    try:
        response = requests.get(DATA_URL)
        response.raise_for_status()
        
        # Read the content
        csv_data = io.StringIO(response.text)
        df = pd.read_csv(csv_data)
        
        # FIX: Rename columns to strict 'URL' and 'Label'
        df.columns = [c.lower() for c in df.columns]
        
        rename_map = {}
        if 'url' in df.columns: rename_map['url'] = 'URL'
        elif 'phish_url' in df.columns: rename_map['phish_url'] = 'URL'
        
        if 'label' in df.columns: rename_map['label'] = 'Label'
        elif 'status' in df.columns: rename_map['status'] = 'Label'
        elif 'phishing' in df.columns: rename_map['phishing'] = 'Label'

        df.rename(columns=rename_map, inplace=True)
        
        # Save
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"✅ SUCCESS! Correct data saved to '{OUTPUT_FILE}'")
        print(f"Rows: {len(df)}")
        print("You can now run 'python train_model.py'")
        
    except Exception as e:
        print(f"❌ Download Failed: {e}")

if __name__ == "__main__":
    get_data()