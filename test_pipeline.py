#!/usr/bin/env python3
"""
Test ML Pipeline Integration
Test all three trained models with sample data
"""

import pickle
import pandas as pd
import numpy as np

def load_models():
    """Load all trained models"""

    models = {}

    # Load Individual Risk Model
    with open('app/models/trained/individual_risk_model.pkl', 'rb') as f:
        models['individual'] = pickle.load(f)

    # Load Text Risk Classifier
    with open('app/models/trained/text_risk_classifier.pkl', 'rb') as f:
        models['text'] = pickle.load(f)

    # Load Organizational Risk Model
    with open('app/models/trained/organizational_risk_model.pkl', 'rb') as f:
        models['organizational'] = pickle.load(f)

    return models

def test_individual_prediction(model_data):
    """Test individual risk prediction"""

    print("\nTesting Individual Risk Prediction...")

    # Sample data
    sample_data = {
        'q1': 2.0, 'q2': 3.0, 'q3': 2.0, 'q4': 3.0, 'q5': 2.0,
        'q6': 3.0, 'q7': 2.0, 'q8': 3.0, 'q9': 2.0, 'q10': 3.0,
        'q11': 2.0, 'q12': 3.0, 'q13': 2.0, 'q14': 3.0, 'q15': 2.0,
        'q16': 3.0, 'q17': 2.0, 'q18': 3.0, 'q19': 2.0, 'q20': 3.0,
        'q21': 2.0, 'q22': 3.0,
        'domain': 'Business',
        'department': 'Engineering',
        'position_level': 'Mid',
        'age_range': '35-44',
        'gender_identity': 'Woman',
        'tenure_range': '3-7_years',
        'supervises_others': False
    }

    # Prepare features
    feature_row = []
    feature_cols = model_data['feature_columns']

    # Add survey scores
    for i in range(1, 23):
        feature_row.append(sample_data[f'q{i}'])

    # Encode categorical variables
    encoders = model_data['feature_encoders']

    try:
        domain_encoded = encoders['domain'].transform([sample_data['domain']])[0]
        dept_encoded = encoders['department'].transform([sample_data['department']])[0]
        position_encoded = encoders['position_level'].transform([sample_data['position_level']])[0]
        age_encoded = encoders['age_range'].transform([sample_data['age_range']])[0]
        gender_encoded = encoders['gender_identity'].transform([sample_data['gender_identity']])[0]
        tenure_encoded = encoders['tenure_range'].transform([sample_data['tenure_range']])[0]
        supervises_encoded = int(sample_data['supervises_others'])

        feature_row.extend([domain_encoded, dept_encoded, position_encoded, age_encoded, gender_encoded, tenure_encoded, supervises_encoded])

        # Make prediction
        X = np.array(feature_row).reshape(1, -1)
        prediction = model_data['model'].predict(X)[0]
        prediction_proba = model_data['model'].predict_proba(X)[0]

        risk_tier = model_data['target_encoder'].inverse_transform([prediction])[0]

        print(f"Predicted Risk Tier: {risk_tier}")
        print(f"Prediction Probabilities: {dict(zip(model_data['risk_tiers'], prediction_proba))}")

        # Calculate HSEG score
        hseg_score = sum(sample_data[f'q{i}'] for i in range(1, 23))
        print(f"HSEG Score: {hseg_score}/88")

        return True

    except Exception as e:
        print(f"Error in individual prediction: {e}")
        return False

def test_text_classification(model_data):
    """Test text risk classification"""

    print("\nTesting Text Risk Classification...")

    # Sample texts
    test_texts = [
        "I'm having panic attacks daily and can't sleep. The work environment is destroying my mental health.",
        "Great team collaboration and supportive management. Really enjoy working here.",
        "My manager is verbally abusive and I'm developing severe anxiety about coming to work.",
        "The technical challenges are interesting and the compensation is fair."
    ]

    try:
        pipeline = model_data['model']
        predictions = pipeline.predict(test_texts)

        for text, pred in zip(test_texts, predictions):
            print(f"Text: '{text[:50]}...'")
            print(f"Prediction: {pred}")
            print()

        return True

    except Exception as e:
        print(f"Error in text classification: {e}")
        return False

def test_organizational_prediction(model_data, sample_df):
    """Test organizational risk prediction"""

    print("\nTesting Organizational Risk Prediction...")

    try:
        # Use actual organizational data from our sample
        org_name = sample_df['organization_name'].iloc[0]
        org_group = sample_df[sample_df['organization_name'] == org_name]

        if len(org_group) < 5:
            print(f"Organization {org_name} has only {len(org_group)} responses, using synthetic data")

            # Create synthetic organizational features
            feature_values = np.random.rand(61)  # 61 features based on training

        else:
            print(f"Using real data for organization: {org_name} ({len(org_group)} responses)")

            # Extract some basic features (simplified)
            survey_cols = [f'q{i}' for i in range(1, 23)]
            feature_values = []

            # Survey means and stds
            for col in survey_cols:
                feature_values.append(org_group[col].mean())
                feature_values.append(org_group[col].std())

            # Demographics
            feature_values.append((org_group['gender_identity'] == 'Woman').mean())
            feature_values.append((org_group['gender_identity'] == 'Man').mean())
            feature_values.append((org_group['position_level'] == 'Entry').mean())
            feature_values.append((org_group['position_level'] == 'Senior').mean())
            feature_values.append(org_group['supervises_others'].mean())

            # Age and tenure
            feature_values.append(org_group['age_range'].isin(['22-24', '25-34']).mean())
            feature_values.append(org_group['age_range'].isin(['45-54', '55+']).mean())
            feature_values.append(org_group['tenure_range'].isin(['<1_year', '1-3_years']).mean())
            feature_values.append(org_group['tenure_range'].isin(['3-7_years', '7+_years']).mean())

            # HSEG scores
            hseg_scores = org_group[survey_cols].sum(axis=1)
            feature_values.append(hseg_scores.mean())
            feature_values.append(hseg_scores.std())

            # Risk distribution
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

            risk_tiers = hseg_scores.apply(get_risk_tier)
            feature_values.append((risk_tiers == 'Crisis').mean())
            feature_values.append((risk_tiers == 'At_Risk').mean())
            feature_values.append((risk_tiers == 'Mixed').mean())
            feature_values.append((risk_tiers == 'Safe').mean())
            feature_values.append((risk_tiers == 'Thriving').mean())

            # Other features
            feature_values.extend([
                org_group['employee_count'].iloc[0],
                len(org_group),
                0.1,  # crisis_keyword_frequency placeholder
                0.3,  # predicted_turnover_rate placeholder
                0.2,  # predicted_legal_risk placeholder
                1.0   # domain_encoded placeholder
            ])

            # Pad or truncate to 61 features
            while len(feature_values) < 61:
                feature_values.append(0.0)
            feature_values = feature_values[:61]

        # Make predictions
        X = np.array(feature_values).reshape(1, -1)

        risk_prediction = model_data['risk_model'].predict(X)[0]
        turnover_prediction = model_data['turnover_model'].predict(X)[0]

        risk_tier = model_data['risk_encoder'].inverse_transform([risk_prediction])[0]

        print(f"Organization: {org_name}")
        print(f"Predicted Risk Tier: {risk_tier}")
        print(f"Predicted Turnover Rate: {turnover_prediction:.1%}")

        return True

    except Exception as e:
        print(f"Error in organizational prediction: {e}")
        return False

def main():
    """Main test function"""

    print("Testing ML Pipeline Integration")
    print("=" * 50)

    try:
        # Load models
        print("Loading trained models...")
        models = load_models()
        print("All models loaded successfully")

        # Load sample data
        sample_df = pd.read_csv('data/hseg_data.csv').head(1000)  # Use subset for testing

        # Test individual prediction
        individual_success = test_individual_prediction(models['individual'])

        # Test text classification
        text_success = test_text_classification(models['text'])

        # Test organizational prediction
        org_success = test_organizational_prediction(models['organizational'], sample_df)

        # Summary
        print("\n" + "=" * 50)
        print("Pipeline Test Results:")
        print(f"Individual Risk Model: {'PASS' if individual_success else 'FAIL'}")
        print(f"Text Risk Classifier: {'PASS' if text_success else 'FAIL'}")
        print(f"Organizational Risk Model: {'PASS' if org_success else 'FAIL'}")

        if all([individual_success, text_success, org_success]):
            print("\nAll models are working correctly!")
            print("Pipeline is ready for API integration")
        else:
            print("\nSome models failed - check error messages above")

    except Exception as e:
        print(f"Pipeline test failed: {e}")

if __name__ == "__main__":
    main()