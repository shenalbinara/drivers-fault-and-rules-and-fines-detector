import pandas as pd
import re

# Step 1: Read the extracted CSV
df = pd.read_csv('extracted_rules09.csv')

# Step 2: Clean the text
def clean_text(text):
    if pd.isna(text):
        return ""
    # Remove unwanted characters
    text = re.sub(r'\s+', ' ', text)  # Replace multiple whitespace/newlines with a single space
    text = re.sub(r'[^a-zA-Z0-9.,;:()\-\'"\s]', '', text)  # Remove weird characters (except punctuation)
    text = text.strip()
    text = text.lower()  # Optional: lowercase all text for uniformity
    return text

# Apply cleaning to text columns
df['Rule Title'] = df['Rule Title'].apply(clean_text)
df['Rule Description'] = df['Rule Description'].apply(clean_text)

# Clean and convert Fine Amount to integer (or None if invalid)
def clean_fine_amount(x):
    try:
        if pd.isna(x) or str(x).strip() == '':
            return None
        return int(float(x))  # handles values like 3000.0 -> 3000
    except:
        return None

df['Fine Amount'] = df['Fine Amount'].apply(clean_fine_amount)

# Step 3: Save the cleaned data
df.to_csv('cleaned_rules02.csv', index=False)

print("✅ Cleaning complete. Saved to cleaned_rules02.csv.")
