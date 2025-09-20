#!/usr/bin/env python3
"""
Complete Pipeline Test - Test all three models working together
Tests individual, text, and organizational models integration
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent / 'app'))
sys.path.append(str(Path(__file__).parent / 'app' / 'models'))
sys.path.append(str(Path(__file__).parent / 'app' / 'core'))

# Import models directly
from app.models.individual_risk_model import IndividualRiskPredictor, create_sample_response_data
from app.models.text_risk_classifier import TextRiskClassifier
from app.models.organizational_risk_model import OrganizationalRiskAggregator

def test_individual_model():
    """Test individual risk model"""
    print("=" * 60)
    print("TESTING INDIVIDUAL RISK MODEL")
    print("=" * 60)

    try:
        # Initialize model
        model = IndividualRiskPredictor()

        # Load trained model
        model_path = "app/models/trained/individual_risk_model.pkl"
        if os.path.exists(model_path):
            model.load_model(model_path)
            print("✅ Individual model loaded successfully")
        else:
            print("❌ Individual model file not found")
            return False

        # Test prediction
        sample_data = create_sample_response_data()
        prediction = model.predict(sample_data)

        if 'error' in prediction:
            print(f"❌ Individual prediction failed: {prediction['error']}")
            return False

        print(f"✅ Individual prediction successful")
        print(f"   Overall HSEG Score: {prediction['overall_hseg_score']}")
        print(f"   Risk Tier: {prediction['overall_risk_tier']}")
        print(f"   Confidence: {prediction['confidence_score']:.3f}")

        return True

    except Exception as e:
        print(f"❌ Individual model test failed: {e}")
        return False

def test_text_classifier():
    """Test text risk classifier"""
    print("\n" + "=" * 60)
    print("TESTING TEXT RISK CLASSIFIER")
    print("=" * 60)

    try:
        # Initialize classifier
        classifier = TextRiskClassifier()

        # Test texts
        test_texts = [
            "My manager screams at me daily and I'm having panic attacks. HR ignores my complaints.",
            "Great workplace with supportive colleagues and excellent work-life balance!",
            "Sometimes management is difficult but generally okay.",
            "Feeling discriminated against because of my background but trying to cope."
        ]

        print("✅ Text classifier initialized")

        # Test predictions
        for i, text in enumerate(test_texts, 1):
            prediction = classifier.predict_text_risk(text)

            if 'error' in prediction:
                print(f"❌ Text prediction {i} failed: {prediction['error']}")
                continue

            print(f"✅ Text {i}: {prediction['overall_risk_level']} risk")
            print(f"   Crisis Detection: {prediction['crisis_detection']['has_crisis_language']}")
            print(f"   Emotional Intensity: {prediction['emotional_intensity']:.3f}")

        return True

    except Exception as e:
        print(f"❌ Text classifier test failed: {e}")
        return False

def test_organizational_model():
    """Test organizational risk model"""
    print("\n" + "=" * 60)
    print("TESTING ORGANIZATIONAL RISK MODEL")
    print("=" * 60)

    try:
        # Initialize model
        org_model = OrganizationalRiskAggregator()

        # Load trained model
        model_path = "app/models/trained/organizational_risk_model.pkl"
        if os.path.exists(model_path):
            org_model.load_model(model_path)
            print("✅ Organizational model loaded successfully")
        else:
            print("❌ Organizational model file not found")
            return False

        # Create sample individual predictions
        individual_model = IndividualRiskPredictor()
        individual_model.load_model("app/models/trained/individual_risk_model.pkl")

        individual_predictions = []
        for i in range(15):  # Generate 15 sample predictions
            sample_data = create_sample_response_data()
            sample_data['response_id'] = f'test_org_resp_{i}'
            prediction = individual_model.predict(sample_data)

            if 'error' not in prediction:
                individual_predictions.append(prediction)

        # Organization info
        org_info = {
            'org_id': 'test_org_001',
            'org_name': 'Test Organization',
            'domain': 'Business',
            'employee_count': 150,
            'founded_year': 2015,
            'is_public_company': False
        }

        # Predict organizational risk
        org_prediction = org_model.predict(individual_predictions, org_info)

        if 'error' in org_prediction:
            print(f"❌ Organizational prediction failed: {org_prediction['error']}")
            return False

        print(f"✅ Organizational prediction successful")
        print(f"   Organization: {org_info['org_name']}")
        print(f"   Sample Size: {len(individual_predictions)}")
        print(f"   Overall Score: {org_prediction['overall_assessment']['overall_hseg_score']}")
        print(f"   Risk Tier: {org_prediction['overall_assessment']['overall_risk_tier']}")
        print(f"   Turnover Risk: {org_prediction['overall_assessment']['predicted_turnover_rate']:.2%}")

        if org_prediction.get('intervention_recommendations'):
            print(f"   Interventions: {len(org_prediction['intervention_recommendations'])} recommended")

        return True

    except Exception as e:
        print(f"❌ Organizational model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integrated_pipeline():
    """Test complete pipeline integration"""
    print("\n" + "=" * 60)
    print("TESTING INTEGRATED PIPELINE")
    print("=" * 60)

    try:
        # Initialize all models
        individual_model = IndividualRiskPredictor()
        text_classifier = TextRiskClassifier()
        org_model = OrganizationalRiskAggregator()

        # Load trained models
        individual_model.load_model("app/models/trained/individual_risk_model.pkl")
        org_model.load_model("app/models/trained/organizational_risk_model.pkl")

        print("✅ All models loaded for integration test")

        # Simulate complete workflow
        print("\n📊 Processing simulated survey campaign...")

        # Generate multiple responses with text
        responses = []
        for i in range(20):
            sample_data = create_sample_response_data()
            sample_data['response_id'] = f'campaign_resp_{i}'

            # Add text responses
            sample_texts = [
                "Management is very supportive and creates a positive work environment.",
                "Sometimes feel overwhelmed but generally manageable workload.",
                "Experiencing some workplace stress but getting support from colleagues.",
                "Manager can be difficult at times but overall okay.",
                "Having serious issues with workplace harassment and feeling unsafe."
            ]

            sample_data['text_responses'] = {
                'q23': sample_texts[i % len(sample_texts)]
            }

            responses.append(sample_data)

        # Process individual predictions with text analysis
        individual_predictions = []
        for response_data in responses:
            # Analyze text first
            text_analysis = {}
            if response_data.get('text_responses'):
                combined_text = ' '.join(response_data['text_responses'].values())
                text_analysis = text_classifier.predict_text_risk(combined_text)

            # Add text analysis to response
            response_data['text_analysis'] = text_analysis

            # Predict individual risk
            individual_pred = individual_model.predict(response_data)

            if 'error' not in individual_pred:
                # Add text risk info
                individual_pred['text_risk_analysis'] = text_analysis
                individual_predictions.append(individual_pred)

        print(f"✅ Processed {len(individual_predictions)} individual predictions")

        # Organization info
        org_info = {
            'org_id': 'integration_test_org',
            'org_name': 'Integration Test Organization',
            'domain': 'Business',
            'employee_count': 200,
            'founded_year': 2018,
            'is_public_company': True
        }

        # Predict organizational risk
        org_prediction = org_model.predict(individual_predictions, org_info)

        if 'error' in org_prediction:
            print(f"❌ Integrated organizational prediction failed: {org_prediction['error']}")
            return False

        print(f"✅ Integrated pipeline completed successfully")
        print(f"\n📈 FINAL RESULTS:")
        print(f"   Organization: {org_info['org_name']}")
        print(f"   Responses Processed: {len(individual_predictions)}")
        print(f"   Overall HSEG Score: {org_prediction['overall_assessment']['overall_hseg_score']}")
        print(f"   Risk Tier: {org_prediction['overall_assessment']['overall_risk_tier']}")
        print(f"   Confidence: {org_prediction['benchmarking']['confidence_score']:.3f}")

        # Show category breakdown
        print(f"\n📊 Category Breakdown:")
        for cat_id, cat_data in org_prediction['category_breakdown'].items():
            print(f"   Category {cat_id}: {cat_data['score']:.2f} ({cat_data['tier']})")

        # Show interventions if any
        if org_prediction.get('intervention_recommendations'):
            print(f"\n🎯 Intervention Recommendations:")
            for intervention in org_prediction['intervention_recommendations'][:3]:
                print(f"   • {intervention['category_name']}: {intervention['intervention']}")

        return True

    except Exception as e:
        print(f"❌ Integrated pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 HSEG AI MODELS - COMPLETE TESTING SUITE")
    print("=" * 80)

    # Run individual tests
    tests = [
        ("Individual Risk Model", test_individual_model),
        ("Text Risk Classifier", test_text_classifier),
        ("Organizational Risk Model", test_organizational_model),
        ("Integrated Pipeline", test_integrated_pipeline)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)

    passed = 0
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:.<30} {status}")
        if success:
            passed += 1

    print("-" * 80)
    print(f"TOTAL: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("🎉 ALL TESTS PASSED! The HSEG AI system is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)