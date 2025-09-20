#!/usr/bin/env python3
"""
Train Text Risk Classifier Model
BERT-based model for detecting crisis language in open-ended responses
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import pickle
import os
import re

def preprocess_text(text):
    """Basic text preprocessing"""
    if pd.isna(text):
        return ""

    # Convert to lowercase
    text = str(text).lower()

    # Remove special characters but keep sentence structure
    text = re.sub(r'[^\w\s\.\!\?]', ' ', text)

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def create_crisis_labels(df):
    """Create crisis labels based on text content and survey scores"""

    # Keywords indicating crisis
    crisis_keywords = [
        'suicide', 'suicidal', 'kill myself', 'end my life', 'want to die',
        'panic attack', 'panic disorder', 'ptsd', 'trauma', 'flashback',
        'can\'t sleep', 'anxiety attack', 'severe depression', 'breakdown',
        'self-harm', 'self harm', 'cutting', 'drinking to cope', 'substance abuse',
        'abuse', 'harassment', 'discrimination', 'retaliation', 'gaslighting',
        'toxic', 'bullying', 'threatened', 'violated', 'destroyed'
    ]

    support_keywords = [
        'therapy', 'counseling', 'therapist', 'support', 'help',
        'medication', 'treatment', 'recovery', 'healing', 'better'
    ]

    # Combine all text responses
    df['combined_text'] = (
        df['q23_text'].fillna('') + ' ' +
        df['q24_text'].fillna('') + ' ' +
        df['q25_text'].fillna('')
    ).apply(preprocess_text)

    # Calculate crisis score based on HSEG survey (lower = more crisis)
    survey_cols = [f'q{i}' for i in range(1, 23)]
    df['hseg_score'] = df[survey_cols].sum(axis=1)

    # Create labels
    def get_crisis_label(row):
        text = row['combined_text']
        score = row['hseg_score']

        # Check for crisis keywords
        crisis_count = sum(1 for keyword in crisis_keywords if keyword in text)
        support_count = sum(1 for keyword in support_keywords if keyword in text)

        # Severe crisis indicators
        if crisis_count >= 3 or score <= 40:
            return 'Crisis'
        elif crisis_count >= 2 or score <= 50:
            return 'High_Risk'
        elif crisis_count >= 1 or score <= 60:
            return 'Moderate_Risk'
        else:
            return 'Low_Risk'

    df['crisis_label'] = df.apply(get_crisis_label, axis=1)

    return df

def train_text_risk_classifier():
    """Train the text crisis detection model"""

    print('Training Text Risk Classifier Model...')

    # Load data
    df = pd.read_csv('data/hseg_data.csv')
    print(f'Loaded {len(df)} records')

    # Create crisis labels
    df = create_crisis_labels(df)

    print('Crisis label distribution:')
    print(df['crisis_label'].value_counts())

    # Prepare text data
    X = df['combined_text']
    y = df['crisis_label']

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f'Training set: {len(X_train)} samples')
    print(f'Test set: {len(X_test)} samples')

    # Create pipeline with TF-IDF and Logistic Regression
    # (Using simpler model than BERT for faster training and deployment)
    print('Training TF-IDF + Logistic Regression model...')

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 3),
            stop_words='english',
            min_df=2,
            max_df=0.95
        )),
        ('classifier', LogisticRegression(
            random_state=42,
            max_iter=1000,
            class_weight='balanced'
        ))
    ])

    # Train model
    pipeline.fit(X_train, y_train)

    # Predictions
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f'Text Classifier Accuracy: {accuracy:.3f}')
    print('Classification Report:')
    print(classification_report(y_test, y_pred))

    # Save model
    os.makedirs('app/models/trained', exist_ok=True)

    with open('app/models/trained/text_risk_classifier.pkl', 'wb') as f:
        pickle.dump({
            'model': pipeline,
            'crisis_labels': list(set(y)),
            'feature_extraction': 'tfidf'
        }, f)

    print('Text Risk Classifier model saved to app/models/trained/text_risk_classifier.pkl')

    # Test some sample predictions
    print('\nSample Predictions:')
    test_texts = [
        "I can't take this anymore, having panic attacks every day",
        "The work environment is supportive and positive",
        "Manager is abusive and I'm developing severe anxiety",
        "Great team collaboration and meaningful projects"
    ]

    predictions = pipeline.predict(test_texts)
    for text, pred in zip(test_texts, predictions):
        print(f'Text: "{text[:50]}..." -> Prediction: {pred}')

    return accuracy

if __name__ == "__main__":
    accuracy = train_text_risk_classifier()
    print(f"Text classifier training completed with accuracy: {accuracy:.3f}")