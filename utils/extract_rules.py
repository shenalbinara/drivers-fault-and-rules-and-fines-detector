import fitz  # PyMuPDF
import pandas as pd
import re
import os
from word2number import w2n





def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        return full_text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None


def extract_numeric_fine(value):
    if pd.isna(value):
        return None
    value = str(value).lower().replace('rupees', '').strip()

    # Debugging
    print(f"Processing Fine Value: {value}")

    try:
        # Try to extract fine using word2number for word-based numbers
        # Extract the phrase containing "not less than" or similar
        if 'not less than' in value:
            match = re.search(r'not less than (.*?) (and|but|or|not|exceeding|less|more|greater|,|\.)', value)
            if match:
                word_number = match.group(1).strip()
                extracted_fine = w2n.word_to_num(word_number)
                print(f"Extracted Fine from Words: {extracted_fine}")
                return extracted_fine

        # Fallback: extract digits directly
        match = re.search(r'(\d{1,3}(,\d{3})*|\d+)', value.replace(',', ''))
        if match:
            extracted_fine = int(match.group())
            print(f"Extracted Fine from Digits: {extracted_fine}")
            return extracted_fine
    except Exception as e:
        print(f"Failed to extract numeric fine: {e}")

    return None



def process_text_into_rules(text):
    if not text:
        return []

    # Simple splitting based on Sections / Fines
    rule_blocks = re.split(r'\n(?=\d+\.)', text)  # Split by numbered sections like "1.", "2.", etc.

    extracted_rules = []

    for block in rule_blocks:
        lines = block.strip().split("\n")
        if len(lines) < 2:
            continue

        rule_title = lines[0].strip()
        rule_description = " ".join(lines[1:]).strip()

        fine_amount = extract_numeric_fine(rule_description)

        extracted_rules.append({
            "Rule Title": rule_title,
            "Rule Description": rule_description,
            "Fine Amount": fine_amount
        })

    return extracted_rules


def save_rules_to_csv(rules, output_csv_path):
    df = pd.DataFrame(rules)
    df.to_csv(output_csv_path, index=False, encoding='utf-8')


if __name__ == "__main__":
    # Absolute path to the PDF (recommended)
    pdf_path = r"C:\Users\HP\Desktop\driver_fault_help\models\rules_data\rules.pdf"
    output_csv_path = r"C:\Users\HP\Desktop\driver_fault_help\models\rules_data\extracted_rules09.csv"

    # Check if the PDF exists before processing
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        exit(1)

    text = extract_text_from_pdf(pdf_path)
    if text:
        rules = process_text_into_rules(text)
        save_rules_to_csv(rules, output_csv_path)
        print(f"Extracted {len(rules)} rules and saved to {output_csv_path}")
    else:
        print("Failed to extract text from PDF.")