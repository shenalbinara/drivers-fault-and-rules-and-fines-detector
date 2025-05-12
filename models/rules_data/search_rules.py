import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# 1. Load the cleaned rules with absolute path
rules_path = r"C:\Users\HP\Desktop\driver_fault_help\models\rules_data\cleaned_rules02.csv"
rules_df = pd.read_csv(rules_path)

# 2. Initialize Sentence Transformer model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')


# 3. Encode all Rule Descriptions
rule_texts = rules_df['Rule Description'].tolist()
rule_embeddings = model.encode(rule_texts)

# 4. Function to find best matching rules
# 4. Function to find the best matching rule (1 only)
def find_best_match_summary(user_input):
    # Encode user input
    user_embedding = model.encode([user_input])

    # Calculate similarity with all rules
    similarities = cosine_similarity(user_embedding, rule_embeddings)[0]

    # Get index of the best match
    best_idx = similarities.argmax()

    # Get and shorten description (approx. 15 words)
    full_description = rules_df.iloc[best_idx]['Rule Description']
    short_description = ' '.join(full_description.split()[:15]) + '...'

    # Prepare result
    best_match = {
        'Rule Title': rules_df.iloc[best_idx]['Rule Title'],
        'Short Description': short_description,
        'Fine Amount': rules_df.iloc[best_idx]['Fine Amount'],
        'Similarity Score': similarities[best_idx]
    }

    return best_match


# 5. Simple Fault Decider
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

# 6. --- For testing ---
if __name__ == "__main__":
    user_input = input("Describe your incident: ")

    match = find_best_match_summary(user_input)

    print("\nBest Matching Rule: \n")
    print(f"Rule Title: {match['Rule Title']}\n + \n ")
    print(f"Short Description: {match['Short Description']}\n")
    print(f"Fine Amount: {match['Fine Amount']}\n + \n")
    print(rules_df[rules_df['Rule Title'].str.startswith("145. (1)\n + \n")])

    print(f"Similarity Score: {match['Similarity Score']:.4f}\n + \n ")

    fault_decision = decide_fault(user_input)
    print("\nFault Decision:", fault_decision)
