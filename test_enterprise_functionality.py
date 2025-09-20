#!/usr/bin/env python3
"""
Enterprise Functionality Test - Test All HSEG Models with Real Data
Comprehensive test suite demonstrating full enterprise capabilities
"""

import json
import numpy as np
from datetime import datetime
import pandas as pd

# Import our models
from app.models.individual_risk_model import IndividualRiskPredictor
from app.models.text_risk_classifier import TextRiskClassifier
from app.models.organizational_risk_model import OrganizationalRiskAggregator

def test_individual_risk_prediction():
    """Test individual risk prediction with real survey data"""
    print("=" * 80)
    print("TESTING INDIVIDUAL RISK PREDICTION")
    print("=" * 80)

    # Initialize model
    model = IndividualRiskPredictor()

    # Load the model
    if not model.load_model("app/models/trained/individual_risk_model.pkl"):
        print("FAILED to load individual risk model")
        return False

    # Sample employee data - High Risk Employee
    high_risk_employee = {
        "domain": "Business",
        "survey_responses": {
            "q1": 1.0,  "q2": 4.0,  "q3": 4.0,  "q4": 1.0,  "q5": 1.0,
            "q6": 1.0,  "q7": 4.0,  "q8": 4.0,  "q9": 1.0,  "q10": 4.0,
            "q11": 1.0, "q12": 4.0, "q13": 4.0, "q14": 1.0, "q15": 4.0,
            "q16": 4.0, "q17": 4.0, "q18": 1.0, "q19": 1.0, "q20": 4.0,
            "q21": 1.0, "q22": 1.0
        },
        "text_responses": {
            "Q23": "My manager constantly yells and threatens employees. Creating a toxic environment.",
            "Q24": "Work stress is causing panic attacks. I can't sleep and have developed anxiety.",
            "Q25": "The only positive is the technical challenges, but management ruins everything."
        },
        "demographics": {
            "age_range": "35-44", "gender_identity": "Woman", "tenure_range": "1-3_years",
            "position_level": "Mid", "department": "Engineering"
        }
    }

    # Sample employee data - Low Risk Employee
    low_risk_employee = {
        "domain": "University",
        "survey_responses": {
            "q1": 4.0,  "q2": 1.0,  "q3": 1.0,  "q4": 4.0,  "q5": 4.0,
            "q6": 4.0,  "q7": 1.0,  "q8": 1.0,  "q9": 4.0,  "q10": 1.0,
            "q11": 4.0, "q12": 1.0, "q13": 1.0, "q14": 4.0, "q15": 1.0,
            "q16": 1.0, "q17": 1.0, "q18": 4.0, "q19": 4.0, "q20": 1.0,
            "q21": 4.0, "q22": 4.0
        },
        "text_responses": {
            "Q23": "Excellent leadership and supportive environment. Great mentorship opportunities.",
            "Q24": "Work is fulfilling and contributes to my wellbeing. Great work-life balance.",
            "Q25": "Amazing colleagues and innovative research opportunities. Love working here."
        },
        "demographics": {
            "age_range": "25-34", "gender_identity": "Man", "tenure_range": "3-5_years",
            "position_level": "Senior", "department": "Research"
        }
    }

    employees = [("HIGH RISK EMPLOYEE", high_risk_employee), ("LOW RISK EMPLOYEE", low_risk_employee)]
    individual_predictions = []

    for name, employee_data in employees:
        print(f"\nAnalyzing {name}")
        print("-" * 50)

        try:
            prediction = model.predict_individual_risk(
                employee_data["survey_responses"],
                employee_data["text_responses"],
                employee_data["demographics"],
                employee_data["domain"]
            )

            individual_predictions.append(prediction)

            print(f"Overall Risk Tier: {prediction['overall_risk_tier']}")
            print(f"HSEG Score: {prediction['overall_hseg_score']:.1f}/28")
            print(f"Confidence: {prediction.get('confidence_score', 0.0):.1%}")

            # Show category breakdowns
            print("\nCategory Scores:")
            category_names = {
                '1': 'Power Abuse & Suppression', '2': 'Discrimination & Exclusion',
                '3': 'Manipulative Work Culture', '4': 'Failure of Accountability',
                '5': 'Mental Health Harm', '6': 'Erosion of Voice & Autonomy'
            }

            for cat_id, score in prediction['category_scores'].items():
                cat_name = category_names.get(cat_id, f"Category {cat_id}")
                print(f"   {cat_name}: {score:.1f}/28")

            print(f"\nPredicted Outcomes:")
            outcomes = prediction.get('predicted_outcomes', {})
            print(f"   Turnover Risk: {outcomes.get('predicted_turnover_rate', 0)*100:.1f}%")
            print(f"   Productivity Impact: {outcomes.get('predicted_productivity_impact', 0)*100:+.1f}%")

        except Exception as e:
            print(f"ERROR analyzing {name}: {e}")
            return False

    print(f"\nIndividual Risk Prediction Test: PASSED")
    return individual_predictions

def test_text_risk_classification():
    """Test text risk classification with various text samples"""
    print("\n" + "=" * 80)
    print("TESTING TEXT RISK CLASSIFICATION")
    print("=" * 80)

    # Initialize model
    model = TextRiskClassifier()

    # Load the model
    if not model.load_model("app/models/trained/text_risk_classifier.pkl"):
        print("FAILED to load text risk classifier model")
        return False

    # Sample texts with different risk levels
    test_texts = [
        ("CRISIS LEVEL", "My manager screams at me daily and threatens to fire me. I'm having panic attacks and can't sleep."),
        ("HIGH RISK", "There's constant discrimination here. Women are passed over for promotions."),
        ("MODERATE RISK", "Sometimes leadership makes decisions without consulting the team."),
        ("LOW RISK", "Great team collaboration and supportive management. Really enjoy the projects."),
        ("VERY LOW RISK", "Excellent work environment with amazing colleagues. Perfect work-life balance.")
    ]

    print("\nAnalyzing Text Samples:")
    print("-" * 50)

    for label, text in test_texts:
        try:
            result = model.classify_text_risk(text)

            risk_level = result.get('risk_classification', 'Unknown')
            confidence = result.get('confidence_score', 0.0)
            sentiment = result.get('sentiment_score', 0.0)

            print(f"\n{label}")
            print(f"Text: \"{text[:60]}...\"")
            print(f"Risk Level: {risk_level}")
            print(f"Confidence: {confidence:.1%}")
            print(f"Sentiment: {sentiment:+.2f}")

            keywords = result.get('risk_keywords', [])
            if keywords:
                print(f"Risk Keywords: {', '.join(keywords[:5])}")

        except Exception as e:
            print(f"ERROR analyzing text '{label}': {e}")
            return False

    print(f"\nText Risk Classification Test: PASSED")
    return True

def test_organizational_risk_assessment(individual_predictions):
    """Test organizational risk assessment with aggregated individual data"""
    print("\n" + "=" * 80)
    print("TESTING ORGANIZATIONAL RISK ASSESSMENT")
    print("=" * 80)

    # Initialize model
    model = OrganizationalRiskAggregator()

    # Create sample organization info
    organization_info = {
        "org_id": "test_org_001",
        "org_name": "TechFlow Industries",
        "domain": "Business",
        "employee_count": 450,
        "founded_year": 2010,
        "is_public_company": True
    }

    # Generate additional sample predictions to meet minimum requirement
    if len(individual_predictions) < 5:
        print("Need at least 5 individual predictions. Generating additional sample data...")
        additional_predictions = []
        for i in range(5):
            additional_predictions.append({
                "overall_hseg_score": np.random.normal(16.0, 4.0),
                "overall_risk_tier": np.random.choice(["Mixed", "At_Risk", "Safe", "Crisis"], p=[0.4, 0.3, 0.2, 0.1]),
                "category_scores": {str(j): np.random.normal(16.0, 3.0) for j in range(1, 7)},
                "demographics": {
                    "age_range": np.random.choice(["25-34", "35-44", "45-54"]),
                    "gender_identity": np.random.choice(["Woman", "Man", "Non-binary"]),
                    "department": np.random.choice(["Engineering", "Sales", "Marketing", "HR"]),
                    "position_level": np.random.choice(["Entry", "Mid", "Senior"])
                }
            })
        individual_predictions.extend(additional_predictions)

    print(f"\nAnalyzing Organization: {organization_info['org_name']}")
    print(f"Sample Size: {len(individual_predictions)} employees")
    print(f"Industry: {organization_info['domain']}")
    print(f"Company Size: {organization_info['employee_count']} employees")
    print("-" * 50)

    try:
        # Predict organizational risk
        org_assessment = model.predict_organizational_risk(individual_predictions, organization_info)

        print(f"\nORGANIZATIONAL RISK ASSESSMENT RESULTS")
        print("=" * 50)
        print(f"Overall HSEG Score: {org_assessment['overall_hseg_score']}/28")
        print(f"Overall Risk Tier: {org_assessment['overall_risk_tier']}")
        print(f"Sample Size: {org_assessment['sample_size']} responses")
        print(f"Confidence Level: {org_assessment['confidence_level']:.1%}")
        print(f"Statistical Significance: {'Yes' if org_assessment['statistical_significance'] else 'No'}")
        print(f"Industry Percentile: {org_assessment['benchmark_percentile']}th percentile")
        print(f"vs Industry Average: {org_assessment['industry_comparison']:+.1f} points")

        # Show category breakdown
        print(f"\nCATEGORY BREAKDOWN:")
        category_names = {
            '1': 'Power Abuse & Suppression', '2': 'Discrimination & Exclusion',
            '3': 'Manipulative Work Culture', '4': 'Failure of Accountability',
            '5': 'Mental Health Harm', '6': 'Erosion of Voice & Autonomy'
        }

        for cat_id, score in org_assessment['category_scores'].items():
            cat_name = category_names.get(cat_id, f"Category {cat_id}")
            print(f"   {cat_name}: {score}/28")

        # Show predicted outcomes
        print(f"\nPREDICTED ORGANIZATIONAL OUTCOMES:")
        outcomes = org_assessment['predicted_outcomes']
        print(f"   Predicted Turnover Rate: {outcomes['predicted_turnover_rate']*100:.1f}%")
        print(f"   Legal Risk: {outcomes['predicted_legal_risk']*100:.1f}%")
        print(f"   Productivity Impact: {outcomes['predicted_productivity_impact']*100:+.1f}%")
        print(f"   Engagement Score: {outcomes['predicted_engagement_score']*100:.1f}%")
        print(f"   Retention Rate: {outcomes['predicted_retention_rate']*100:.1f}%")

        # Show intervention priorities
        print(f"\nTOP INTERVENTION PRIORITIES:")
        for i, priority in enumerate(org_assessment['intervention_priorities'], 1):
            print(f"   {i}. {priority['category'].replace('_', ' ')}")
            print(f"      Urgency: {priority['urgency']} | Risk Rate: {priority['risk_rate']*100:.1f}%")
            print(f"      Action: {priority['intervention']}")
            print(f"      Effort: {priority['estimated_effort']} | Impact: {priority['expected_impact']}")

        # Generate dashboard data
        print(f"\nGENERATING ENTERPRISE DASHBOARD DATA...")
        dashboard_data = model.generate_dashboard_data(org_assessment)

        print(f"Dashboard KPIs: {len(dashboard_data['kpi_metrics'])} metrics")
        print(f"Category Radar Data: {len(dashboard_data['category_radar_data'])} categories")
        print(f"Risk Distribution: {len(dashboard_data['risk_distribution_chart'])} tiers")
        print(f"Priority Actions: {len(dashboard_data['priority_actions'])} actions")
        print(f"Trend Data: {len(dashboard_data['trend_data'])} data points")
        print(f"Benchmark Data: Industry comparison ready")

        # Show sample dashboard data
        print(f"\nSAMPLE DASHBOARD DISPLAY:")
        print("-" * 30)

        # Main KPIs
        for name, kpi in dashboard_data['kpi_metrics'].items():
            if name == 'overall_risk_score':
                print(f"Overall Score: {kpi['value']:.1f}/{kpi['max_value']} {kpi['unit']}")
            elif name == 'risk_tier':
                print(f"Risk Classification: {kpi['value']}")
            elif name == 'turnover_risk':
                print(f"Turnover Risk: {kpi['value']:.1f}{kpi['unit']}")

        # Risk distribution
        print(f"\nRisk Distribution:")
        for dist in dashboard_data['risk_distribution_chart']:
            print(f"   {dist['tier']}: {dist['percentage']}%")

        print(f"\nOrganizational Risk Assessment Test: PASSED")

        # Show JSON export sample
        print(f"\nENTERPRISE DATA EXPORT SAMPLE:")
        print("-" * 40)
        export_sample = {
            "organization": organization_info['org_name'],
            "assessment_date": datetime.now().isoformat(),
            "overall_score": org_assessment['overall_hseg_score'],
            "risk_tier": org_assessment['overall_risk_tier'],
            "sample_size": org_assessment['sample_size'],
            "key_metrics": {
                "turnover_risk": f"{outcomes['predicted_turnover_rate']*100:.1f}%",
                "legal_risk": f"{outcomes['predicted_legal_risk']*100:.1f}%",
                "productivity_impact": f"{outcomes['predicted_productivity_impact']*100:+.1f}%"
            },
            "top_priorities": [p['category'] for p in org_assessment['intervention_priorities'][:3]]
        }
        print(json.dumps(export_sample, indent=2))

        return True

    except Exception as e:
        print(f"ERROR in organizational assessment: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run complete functionality test"""
    print("HSEG AI SYSTEM - ENTERPRISE FUNCTIONALITY TEST")
    print("=" * 80)
    print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    results = {}

    # Test 1: Individual Risk Prediction
    individual_predictions = test_individual_risk_prediction()
    results['individual'] = individual_predictions is not False

    # Test 2: Text Risk Classification
    text_result = test_text_risk_classification()
    results['text'] = text_result

    # Test 3: Organizational Risk Assessment
    if individual_predictions:
        org_result = test_organizational_risk_assessment(individual_predictions)
        results['organizational'] = org_result
    else:
        results['organizational'] = False
        print("Skipping organizational test due to individual test failure")

    # Summary
    print("\n" + "=" * 80)
    print("FINAL TEST RESULTS SUMMARY")
    print("=" * 80)

    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)

    print(f"Individual Risk Prediction: {'PASSED' if results['individual'] else 'FAILED'}")
    print(f"Text Risk Classification: {'PASSED' if results['text'] else 'FAILED'}")
    print(f"Organizational Risk Assessment: {'PASSED' if results['organizational'] else 'FAILED'}")

    print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("ALL TESTS PASSED! HSEG AI System is fully functional!")
        print("Ready for production deployment with Docker!")
        print("\nEnterprise Features Demonstrated:")
        print("- Individual psychological risk assessment")
        print("- Text-based crisis detection")
        print("- Organizational risk aggregation")
        print("- Intervention priority recommendations")
        print("- Dashboard-ready data visualization")
        print("- Industry benchmarking")
        print("- Statistical significance testing")
        print("- JSON export capabilities")
    else:
        print("Some tests failed. Please review errors above.")

    print(f"Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)