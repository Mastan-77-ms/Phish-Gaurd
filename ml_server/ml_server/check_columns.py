import pandas as pd

# Load the file
df = pd.read_csv("phishing_data.csv")

# Print the column names
print("\n--- YOUR CSV COLUMNS ARE: ---")
print(df.columns.tolist())
print("-----------------------------\n")