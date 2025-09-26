
import os
import json
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import BertTokenizer, BertForSequenceClassification, DataCollatorWithPadding
from sklearn.model_selection import train_test_split
from tqdm import tqdm

# Define constants
DATA_DIR = "data"
MODEL_OUTPUT_DIR = "app/models/trained/communication_risk_model"
MODEL_NAME = "bert-base-uncased"
MAX_LEN = 256
BATCH_SIZE = 16
EPOCHS = 3
LEARNING_RATE = 2e-5

# Define HSEG categories and keywords
CATEGORY_KEYWORDS = {
    1: ['bully', 'harass', 'intimidate', 'threat', 'retaliate', 'suppress', 'silence', 'power abuse'],
    2: ['discriminate', 'exclude', 'bias', 'racism', 'sexism', 'unfair', 'unequal', 'prejudice'],
    3: ['manipulate', 'gaslight', 'toxic', 'micromanage', 'unethical', 'deceit', 'dishonest'],
    4: ['accountability', 'consequences', 'complacency', 'inaction', 'ignore', 'neglect', 'cover-up'],
    5: ['mental health', 'anxiety', 'stress', 'burnout', 'depression', 'well-being', 'overwhelmed'],
    6: ['voice', 'autonomy', 'feedback', 'empowerment', 'involvement', 'decision-making', 'control']
}

# Load and merge data
def load_data():
    json_files = [f for f in os.listdir(DATA_DIR) if f.startswith('hseg_data_part_') and f.endswith('.json')]
    df_list = []
    for file in json_files:
        with open(os.path.join(DATA_DIR, file), 'r') as f:
            data = json.load(f)
            df_list.append(pd.DataFrame(data))
    df = pd.concat(df_list, ignore_index=True)
    return df

# Create labels
def create_labels(df):
    df['text'] = df['q23'].fillna('') + ' ' + df['q24'].fillna('') + ' ' + df['q25'].fillna('')
    for category_id, keywords in CATEGORY_KEYWORDS.items():
        df[f'category_{category_id}'] = df['text'].str.lower().apply(
            lambda x: 1 if any(kw in x for kw in keywords) else 0
        )
    return df

# Create dataset class
class RiskDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, item):
        text = str(self.texts[item])
        labels = self.labels[item]
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            truncation=True,
            return_attention_mask=True,
        )
        return {
            'input_ids': encoding['input_ids'],
            'attention_mask': encoding['attention_mask'],
            'labels': torch.tensor(labels, dtype=torch.float)
        }

# Main training function
def train_model():
    # Load and prepare data
    print("Loading and preparing data...")
    df = load_data()

    # For faster testing, uncomment the following line to use a fraction of the data
    # df = df.sample(frac=0.1, random_state=42).reset_index(drop=True)

    df = create_labels(df)
    labels = [f'category_{i}' for i in range(1, 7)]
    X_train, X_val, y_train, y_val = train_test_split(
        df['text'].to_numpy(),
        df[labels].to_numpy(),
        test_size=0.1,
        random_state=42
    )

    # Initialize tokenizer and model
    print("Initializing tokenizer and model...")
    tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    model = BertForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(labels),
        problem_type="multi_label_classification"
    )

    # Create datasets and dataloaders
    train_dataset = RiskDataset(X_train, y_train, tokenizer, MAX_LEN)
    val_dataset = RiskDataset(X_val, y_val, tokenizer, MAX_LEN)
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, collate_fn=data_collator)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, collate_fn=data_collator)

    # Set up optimizer and device
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    print(f"Using device: {device}")
    print(f"Number of training samples: {len(train_dataset)}")

    # Training loop
    print("Starting training...")
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0
        for batch in tqdm(train_loader, desc=f"Epoch {epoch + 1}/{EPOCHS}"):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            optimizer.zero_grad()
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            loss = outputs.loss
            total_loss += loss.item()
            loss.backward()
            optimizer.step()

        avg_train_loss = total_loss / len(train_loader)
        print(f"Epoch {epoch + 1} | Average Training Loss: {avg_train_loss:.4f}")

    # Save the model
    print("Saving model...")
    os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)
    model.save_pretrained(MODEL_OUTPUT_DIR)
    tokenizer.save_pretrained(MODEL_OUTPUT_DIR)

if __name__ == "__main__":
    train_model()
