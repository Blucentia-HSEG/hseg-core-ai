#!/usr/bin/env python3
"""
Train Individual Risk Predictor Model
XGBoost-based model for predicting individual psychological risk tiers
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import xgboost as xgb
import pickle
import os

def train_individual_risk_model():
    """Train the individual risk predictor model"""

    print('Training Individual Risk Predictor Model...')

    # Load data
    df = pd.read_csv('data/hseg_data.csv')
    print(f'Loaded {len(df)} records')

    # Create target variable based on HSEG scoring
    survey_cols = [f'q{i}' for i in range(1, 23)]
    df['hseg_score'] = df[survey_cols].sum(axis=1)

    # Create risk tiers based on HSEG score
    def get_risk_tier(score):
        if score <= 44:  # Very low scores indicate crisis
            return 'Crisis'
        elif score <= 55:
            return 'At_Risk'
        elif score <= 66:
            return 'Mixed'
        elif score <= 77:
            return 'Safe'
        else:
            return 'Thriving'

    df['risk_tier'] = df['hseg_score'].apply(get_risk_tier)
    print('Risk tier distribution:')
    print(df['risk_tier'].value_counts())

    # Prepare features
    feature_cols = survey_cols + ['domain', 'department', 'position_level', 'age_range', 'gender_identity', 'tenure_range', 'supervises_others']

    # Encode categorical variables
    le_domain = LabelEncoder()
    le_dept = LabelEncoder()
    le_position = LabelEncoder()
    le_age = LabelEncoder()
    le_gender = LabelEncoder()
    le_tenure = LabelEncoder()

    df['domain_encoded'] = le_domain.fit_transform(df['domain'])
    df['department_encoded'] = le_dept.fit_transform(df['department'])
    df['position_encoded'] = le_position.fit_transform(df['position_level'])
    df['age_encoded'] = le_age.fit_transform(df['age_range'])
    df['gender_encoded'] = le_gender.fit_transform(df['gender_identity'])
    df['tenure_encoded'] = le_tenure.fit_transform(df['tenure_range'])
    df['supervises_encoded'] = df['supervises_others'].astype(int)

    # Final feature set
    feature_cols_encoded = survey_cols + ['domain_encoded', 'department_encoded', 'position_encoded', 'age_encoded', 'gender_encoded', 'tenure_encoded', 'supervises_encoded']

    X = df[feature_cols_encoded]
    y = df['risk_tier']

    # Encode target
    le_target = LabelEncoder()
    y_encoded = le_target.fit_transform(y)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)

    print(f'Training set: {len(X_train)} samples')
    print(f'Test set: {len(X_test)} samples')

    # Train XGBoost model
    print('Training XGBoost model...')
    xgb_model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        n_jobs=-1
    )

    xgb_model.fit(X_train, y_train)

    # Predictions
    y_pred = xgb_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f'XGBoost Accuracy: {accuracy:.3f}')
    print('Classification Report:')
    print(classification_report(y_test, y_pred, target_names=le_target.classes_))

    # Save model and encoders
    os.makedirs('app/models/trained', exist_ok=True)

    with open('app/models/trained/individual_risk_model.pkl', 'wb') as f:
        pickle.dump({
            'model': xgb_model,
            'target_encoder': le_target,
            'feature_encoders': {
                'domain': le_domain,
                'department': le_dept,
                'position_level': le_position,
                'age_range': le_age,
                'gender_identity': le_gender,
                'tenure_range': le_tenure
            },
            'feature_columns': feature_cols_encoded,
            'risk_tiers': list(le_target.classes_)
        }, f)

    print('Individual Risk Predictor model saved to app/models/trained/individual_risk_model.pkl')
    return accuracy

if __name__ == "__main__":
    accuracy = train_individual_risk_model()
    print(f"Model training completed with accuracy: {accuracy:.3f}")