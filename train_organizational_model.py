#!/usr/bin/env python3
"""
Train Organizational Risk Aggregator Model
LightGBM-based model for predicting organizational-level risks
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, mean_squared_error
import lightgbm as lgb
import pickle
import os

def create_organizational_features(df):
    """Create organizational-level features from individual responses"""

    org_features = []

    # Group by organization
    for org_name, group in df.groupby('organization_name'):
        if len(group) < 5:  # Skip organizations with too few responses
            continue

        org_data = {
            'organization_name': org_name,
            'domain': group['domain'].iloc[0],
            'employee_count': group['employee_count'].iloc[0],
            'total_responses': len(group)
        }

        # Survey score aggregations
        survey_cols = [f'q{i}' for i in range(1, 23)]
        for col in survey_cols:
            org_data[f'{col}_mean'] = group[col].mean()
            org_data[f'{col}_std'] = group[col].std()

        # Demographic distributions
        org_data['pct_women'] = (group['gender_identity'] == 'Woman').mean()
        org_data['pct_men'] = (group['gender_identity'] == 'Man').mean()
        org_data['pct_entry_level'] = (group['position_level'] == 'Entry').mean()
        org_data['pct_senior'] = (group['position_level'] == 'Senior').mean()
        org_data['pct_supervisors'] = group['supervises_others'].mean()

        # Age distribution
        org_data['pct_young'] = group['age_range'].isin(['22-24', '25-34']).mean()
        org_data['pct_older'] = group['age_range'].isin(['45-54', '55+']).mean()

        # Tenure distribution
        org_data['pct_new_employees'] = group['tenure_range'].isin(['<1_year', '1-3_years']).mean()
        org_data['pct_veteran_employees'] = group['tenure_range'].isin(['3-7_years', '7+_years']).mean()

        # Calculate organizational risk indicators
        org_data['hseg_score_mean'] = group[[f'q{i}' for i in range(1, 23)]].sum(axis=1).mean()
        org_data['hseg_score_std'] = group[[f'q{i}' for i in range(1, 23)]].sum(axis=1).std()

        # Risk tier distribution
        def get_risk_tier(score):
            if score <= 44:
                return 'Crisis'
            elif score <= 55:
                return 'At_Risk'
            elif score <= 66:
                return 'Mixed'
            elif score <= 77:
                return 'Safe'
            else:
                return 'Thriving'

        individual_risks = group[[f'q{i}' for i in range(1, 23)]].sum(axis=1).apply(get_risk_tier)
        org_data['pct_crisis'] = (individual_risks == 'Crisis').mean()
        org_data['pct_at_risk'] = (individual_risks == 'At_Risk').mean()
        org_data['pct_mixed'] = (individual_risks == 'Mixed').mean()
        org_data['pct_safe'] = (individual_risks == 'Safe').mean()
        org_data['pct_thriving'] = (individual_risks == 'Thriving').mean()

        # Text-based risk indicators (simplified)
        combined_text = ' '.join(group[['q23_text', 'q24_text', 'q25_text']].fillna('').apply(lambda x: ' '.join(x), axis=1))

        crisis_keywords = ['suicide', 'panic', 'anxiety', 'depression', 'trauma', 'abuse', 'harassment', 'toxic']
        org_data['crisis_keyword_frequency'] = sum(combined_text.lower().count(word) for word in crisis_keywords) / len(combined_text)

        # Create organizational risk tier
        if org_data['pct_crisis'] > 0.3 or org_data['hseg_score_mean'] < 50:
            org_data['org_risk_tier'] = 'High_Risk'
        elif org_data['pct_crisis'] > 0.15 or org_data['hseg_score_mean'] < 60:
            org_data['org_risk_tier'] = 'Medium_Risk'
        else:
            org_data['org_risk_tier'] = 'Low_Risk'

        # Predicted outcomes
        org_data['predicted_turnover_rate'] = min(0.8, org_data['pct_crisis'] * 2 + org_data['pct_at_risk'] * 0.5)
        org_data['predicted_legal_risk'] = min(0.6, org_data['crisis_keyword_frequency'] * 100 + org_data['pct_crisis'])

        org_features.append(org_data)

    return pd.DataFrame(org_features)

def train_organizational_risk_model():
    """Train the organizational risk aggregator model"""

    print('Training Organizational Risk Aggregator Model...')

    # Load data
    df = pd.read_csv('data/hseg_data.csv')
    print(f'Loaded {len(df)} records')

    # Create organizational features
    org_df = create_organizational_features(df)
    print(f'Created organizational dataset with {len(org_df)} organizations')

    print('Organizational risk distribution:')
    print(org_df['org_risk_tier'].value_counts())

    # Prepare features for model
    feature_cols = [col for col in org_df.columns if col not in [
        'organization_name', 'org_risk_tier', 'predicted_turnover_rate', 'predicted_legal_risk'
    ]]

    # Encode categorical variables
    le_domain = LabelEncoder()
    org_df['domain_encoded'] = le_domain.fit_transform(org_df['domain'])

    # Update feature columns
    feature_cols = [col for col in feature_cols if col != 'domain'] + ['domain_encoded']

    X = org_df[feature_cols]
    y_risk = org_df['org_risk_tier']
    y_turnover = org_df['predicted_turnover_rate']

    # Encode risk tier target
    le_risk = LabelEncoder()
    y_risk_encoded = le_risk.fit_transform(y_risk)

    # Split data
    X_train, X_test, y_risk_train, y_risk_test, y_turnover_train, y_turnover_test = train_test_split(
        X, y_risk_encoded, y_turnover, test_size=0.2, random_state=42, stratify=y_risk_encoded
    )

    print(f'Training set: {len(X_train)} organizations')
    print(f'Test set: {len(X_test)} organizations')

    # Train LightGBM for risk classification
    print('Training LightGBM risk classifier...')
    risk_model = lgb.LGBMClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        n_jobs=-1
    )

    risk_model.fit(X_train, y_risk_train)

    # Train LightGBM for turnover prediction
    print('Training LightGBM turnover predictor...')
    turnover_model = lgb.LGBMRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        n_jobs=-1
    )

    turnover_model.fit(X_train, y_turnover_train)

    # Evaluate risk model
    y_risk_pred = risk_model.predict(X_test)
    risk_accuracy = accuracy_score(y_risk_test, y_risk_pred)

    print(f'Risk Classification Accuracy: {risk_accuracy:.3f}')
    print('Risk Classification Report:')
    print(classification_report(y_risk_test, y_risk_pred, target_names=le_risk.classes_))

    # Evaluate turnover model
    y_turnover_pred = turnover_model.predict(X_test)
    turnover_rmse = np.sqrt(mean_squared_error(y_turnover_test, y_turnover_pred))

    print(f'Turnover Prediction RMSE: {turnover_rmse:.3f}')

    # Save models
    os.makedirs('app/models/trained', exist_ok=True)

    with open('app/models/trained/organizational_risk_model.pkl', 'wb') as f:
        pickle.dump({
            'risk_model': risk_model,
            'turnover_model': turnover_model,
            'risk_encoder': le_risk,
            'domain_encoder': le_domain,
            'feature_columns': feature_cols,
            'risk_tiers': list(le_risk.classes_)
        }, f)

    print('Organizational Risk Aggregator model saved to app/models/trained/organizational_risk_model.pkl')

    return risk_accuracy, turnover_rmse

if __name__ == "__main__":
    risk_acc, turnover_rmse = train_organizational_risk_model()
    print(f"Organizational model training completed - Risk Accuracy: {risk_acc:.3f}, Turnover RMSE: {turnover_rmse:.3f}")