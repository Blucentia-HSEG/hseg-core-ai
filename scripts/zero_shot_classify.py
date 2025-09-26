
import os
import json
import pandas as pd
from transformers import pipeline
import torch

# --- Configuration ---
# Directory where your JSON data files are located
DATA_DIR = "data"
# The categories you want to classify the text into.
# These are derived from the categories in your training script.
CANDIDATE_LABELS = [
    "Power Abuse & Suppression",
    "Failure of Accountability",
    "Discrimination & Exclusion",
    "Mental Health Harm",
    "Manipulative Work Culture",
    "Erosion of Voice & Autonomy"
]
# Number of sample texts to classify. Change this to classify more or less.
NUM_SAMPLES = 5

# --- Data Loading ---
def load_data():
    """
    Loads and merges all 'hseg_data_part_*.json' files from the DATA_DIR.
    """
    json_files = [f for f in os.listdir(DATA_DIR) if f.startswith('hseg_data_part_') and f.endswith('.json')]
    if not json_files:
        print(f"Error: No data files found in '{DATA_DIR}'. Please ensure your data is there.")
        return pd.DataFrame()
        
    df_list = []
    for file in json_files:
        with open(os.path.join(DATA_DIR, file), 'r') as f:
            data = json.load(f)
            df_list.append(pd.DataFrame(data))
    df = pd.concat(df_list, ignore_index=True)
    return df

# --- Main Classification Logic ---
def classify_text_zero_shot():
    """
    Loads data, initializes a zero-shot classification pipeline,
    and classifies a sample of the text data.
    """
    print("Loading data...")
    df = load_data()
    if df.empty:
        return

    # Combine the relevant text fields, handling potential missing values
    df['text'] = df['q23'].fillna('') + ' ' + df['q24'].fillna('') + ' ' + df['q25'].fillna('')
    
    # Filter out rows where the combined text is empty
    texts_to_classify = df[df['text'].str.strip() != '']['text'].tolist()
    
    if not texts_to_classify:
        print("No text found to classify after combining q23, q24, and q25.")
        return

    # Determine the device to run the model on (GPU if available)
    device = 0 if torch.cuda.is_available() else -1
    device_name = "GPU" if device == 0 else "CPU"

    print(f"Initializing zero-shot classification pipeline on {device_name}...")
    # This will download the model on the first run
    classifier = pipeline("zero-shot-classification", device=device)

    print(f"\n--- Classifying {NUM_SAMPLES} sample texts (out of {len(texts_to_classify)} total) ---\n")

    # Take a sample of the texts to classify
    sample_texts = texts_to_classify[:NUM_SAMPLES]

    # Classify the texts
    results = classifier(sample_texts, CANDIDATE_LABELS, multi_label=True)

    # Display the results
    for i, result in enumerate(results):
        print(f"--- Sample {i+1} ---")
        print(f"Text: {result['sequence']}\n")
        print("Predicted Categories:")
        # Sort labels by score in descending order
        sorted_labels = sorted(zip(result['labels'], result['scores']), key=lambda x: x[1], reverse=True)
        for label, score in sorted_labels:
            print(f"  - {label}: {score:.4f}")
        print("\n" + "="*40 + "\n")

if __name__ == "__main__":
    classify_text_zero_shot()
