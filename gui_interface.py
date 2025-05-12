import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import Image, ImageTk
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
from PIL import Image

# Load the rules CSV
rules_path = r"C:\Users\HP\Desktop\driver_fault_help\models\rules_data\cleaned_rules02.csv"
rules_df = pd.read_csv(rules_path)

# --- Extract numeric fine from string ---
def extract_numeric_fine(value):
    if pd.isna(value):
        return None
    value = str(value).lower().replace('rupees', '').strip()
    if 'not less than' in value:
        match = re.search(r'(\d{1,3}(,\d{3})*|\d+)', value.replace(',', ''))
        if match:
            return int(match.group())
    match = re.search(r'(\d{1,3}(,\d{3})*|\d+)', value.replace(',', ''))
    if match:
        return int(match.group())
    return None

rules_df['Numeric Fine'] = rules_df['Fine Amount'].apply(extract_numeric_fine)

# Load the model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
rule_texts = rules_df['Rule Description'].tolist()
rule_embeddings = model.encode(rule_texts)

# --- Fault Decision Function ---
def decide_fault(user_input):
    keywords_driver_fault = ['speeding', 'brake', 'red light', 'illegal', 'overload', 'drink', 'not stop']
    keywords_other_fault = ['dog', 'animal', 'other car', 'another vehicle', 'bike hit', 'lorry']
    user_input_lower = user_input.lower()
    driver_fault = any(keyword in user_input_lower for keyword in keywords_driver_fault)
    other_fault = any(keyword in user_input_lower for keyword in keywords_other_fault)
    if driver_fault and not other_fault:
        return "You are at fault."
    elif other_fault and not driver_fault:
        return "Other party seems at fault."
    elif driver_fault and other_fault:
        return "Shared fault. Further investigation needed."
    else:
        return "Unable to determine. Please provide more details."

# --- Best Match Function ---
def find_best_match_summary(user_input):
    user_embedding = model.encode([user_input])
    similarities = cosine_similarity(user_embedding, rule_embeddings)[0]
    best_idx = similarities.argmax()
    full_description = rules_df.iloc[best_idx]['Rule Description']
    short_description = ' '.join(full_description.split()[:15]) + '...'
    return {
        'Rule Title': rules_df.iloc[best_idx]['Rule Title'],
        'Short Description': short_description,
        'Fine Amount': rules_df.iloc[best_idx]['Numeric Fine'],
        'Similarity Score': similarities[best_idx]
    }

# --- GUI Logic ---
def analyze_input():
    user_input = input_text.get("1.0", tk.END).strip()
    if not user_input:
        messagebox.showwarning("Input Required", "Please describe your incident.")
        return
    result = find_best_match_summary(user_input)
    fault = decide_fault(user_input)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, f"Best Matching Rule:\n")
    output_text.insert(tk.END, f"Title: {result['Rule Title']}\n")
    output_text.insert(tk.END, f"Description: {result['Short Description']}\n")
    fine_amount = result['Fine Amount']
    fine_text = f"RS: {fine_amount:,}" if fine_amount is not None else "Not Available"
    output_text.insert(tk.END, f"Fine: {fine_text}\n")
    output_text.insert(tk.END, f"Similarity Score: {result['Similarity Score']:.4f}\n\n")
    output_text.insert(tk.END, f"Fault Decision: {fault}")

# --- GUI Setup ---
root = tk.Tk()
root.title("Driver Fault Helper")
root.geometry("700x500")
root.resizable(False, False)

# Load and display the image at the top
try:
    image_path = "images/images-removebg-preview.png"
    image = image.resize((80, 80), Image.Resampling.LANCZOS)
    loaded_image = Image.open(image_path)
    resized_image = loaded_image.resize((100, 100), Image.ANTIALIAS)
    tk_image = ImageTk.PhotoImage(resized_image)
    img_label = tk.Label(root, image=tk_image)
    img_label.image = tk_image  # Keep a reference to prevent garbage collection
    img_label.pack(pady=(5, 0))
except Exception as e:
    print(f"Error loading image: {e}")

tk.Label(root, text="Enter Incident Description:", font=('Arial', 14)).pack(pady=10)
input_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=7, font=('Arial', 12))
input_text.pack(padx=10, pady=5)

analyze_button = tk.Button(root, text="Analyze", command=analyze_input, font=('Arial', 12), bg="lightblue")
analyze_button.pack(pady=10)

tk.Label(root, text="Result:", font=('Arial', 14)).pack(pady=5)
output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=12, font=('Arial', 12))
output_text.pack(padx=10, pady=5)

root.mainloop()
