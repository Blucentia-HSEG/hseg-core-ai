#!/usr/bin/env python3
"""
Test script for HSEG AI API
Demonstrates how to use the psychological risk assessment endpoints
"""

import requests
import json
import pandas as pd

# API base URL
BASE_URL = "http://localhost:8001"

def test_health_check():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_individual_prediction():
    """Test individual psychological risk prediction"""
    print("🧠 Testing individual risk prediction...")

    # Sample data representing a person at moderate risk
    test_data = {
        "response_id": "test_individual_001",
        "domain": "Business",
        "survey_responses": {
            "q1": 2.0,  # Safe speaking up
            "q2": 3.0,  # Leadership silencing
            "q3": 3.0,  # Fear consequences
            "q4": 2.5,  # Power dynamics
            "q5": 3.0,  # Discrimination
            "q6": 2.0,  # Harassment
            "q7": 3.5,  # Manipulation
            "q8": 2.5,  # Gaslighting
            "q9": 3.0,  # Accountability
            "q10": 2.5, # Leadership response
            "q11": 3.0, # Mental health impact
            "q12": 2.0, # Stress levels
            "q13": 3.5, # Work-life balance
            "q14": 2.5, # Support systems
            "q15": 3.0, # Voice and autonomy
            "q16": 2.5, # Decision making
            "q17": 3.0, # Recognition
            "q18": 2.0, # Growth opportunities
            "q19": 3.5, # Feedback quality
            "q20": 2.5, # Communication
            "q21": 3.0, # Team dynamics
            "q22": 2.5  # Overall satisfaction
        },
        "text_responses": {
            "Q23": "Management needs better communication and transparency with employees",
            "Q24": "Work stress has been affecting my sleep and causing some anxiety",
            "Q25": "The technical resources and office facilities are excellent"
        },
        "demographics": {
            "age_range": "35-44",
            "gender_identity": "Woman",
            "tenure_range": "1-3_years",
            "position_level": "Mid",
            "department": "Engineering",
            "supervises_others": False,
            "work_location": "Hybrid",
            "employment_status": "Full_Time",
            "education_level": "Bachelors",
            "ethnicity_group": "White"
        }
    }

    response = requests.post(f"{BASE_URL}/predict/individual", json=test_data)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Prediction successful!")
        print(f"Response ID: {result['response_id']}")
        print(f"Overall HSEG Score: {result['overall_hseg_score']:.2f}/28")
        print(f"Risk Tier: {result['overall_risk_tier']}")
        print(f"Confidence: {result['confidence_score']:.1%}")
        print(f"Processing Time: {result['processing_time_ms']:.1f}ms")

        print("\n📊 Category Scores:")
        categories = {
            "1": "Power Abuse & Suppression",
            "2": "Discrimination & Harassment",
            "3": "Manipulation & Gaslighting",
            "4": "Accountability & Leadership",
            "5": "Mental Health Impact",
            "6": "Voice & Autonomy"
        }

        for cat_id, name in categories.items():
            score = result['category_scores'][cat_id]
            level = result['category_risk_levels'][cat_id]
            print(f"  {name}: {score:.2f} ({level})")

        print("\n💡 Recommended Interventions:")
        for intervention in result['recommended_interventions']:
            print(f"  • {intervention['category']}: {intervention['intervention']}")
            print(f"    Urgency: {intervention['urgency']}, Impact: {intervention['impact']}")
    else:
        print(f"❌ Error: {response.text}")
    print()

def test_organizational_prediction():
    """Test organizational risk assessment"""
    print("🏢 Testing organizational risk prediction...")

    # Create sample organizational data with 5+ individuals
    org_data = {
        "organization_info": {
            "org_id": "test_company_001",
            "org_name": "TechFlow Industries",
            "domain": "Business",
            "employee_count": 150
        },
        "individual_responses": []
    }

    # Generate 5 sample employee responses
    for i in range(5):
        response = {
            "response_id": f"emp_{i+1:03d}",
            "domain": "Business",
            "survey_responses": {f"q{j}": 2.0 + (i * 0.3) + (j % 3 * 0.2) for j in range(1, 23)},
            "text_responses": {
                "Q23": f"Employee {i+1} feedback on workplace culture and management",
                "Q24": f"Mental health status varies with stress level {i+1}",
                "Q25": f"Resources and facilities feedback from employee {i+1}"
            },
            "demographics": {
                "age_range": ["25-34", "35-44", "25-34", "45-54", "35-44"][i],
                "gender_identity": ["Woman", "Man", "Non-binary", "Woman", "Man"][i],
                "tenure_range": ["1-3_years", "4-7_years", "1-3_years", "8+_years", "1-3_years"][i],
                "position_level": ["Entry", "Mid", "Mid", "Senior", "Mid"][i],
                "department": ["Engineering", "Sales", "Marketing", "Engineering", "Finance"][i],
                "supervises_others": [False, False, True, True, False][i],
                "work_location": "Hybrid",
                "employment_status": "Full_Time",
                "education_level": "Bachelors",
                "ethnicity_group": "White"
            }
        }
        org_data["individual_responses"].append(response)

    response = requests.post(f"{BASE_URL}/predict/organizational", json=org_data)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Organizational assessment successful!")
        overall = result['overall_assessment']
        print(f"Organization: {overall['org_name']}")
        print(f"Overall Risk Tier: {overall['overall_risk_tier']}")
        print(f"Average HSEG Score: {overall['average_hseg_score']:.2f}/28")
        print(f"Predicted Turnover Rate: {overall['predicted_turnover_rate']:.1%}")
        print(f"Responses Analyzed: {overall['total_responses']}")
    else:
        print(f"❌ Error: {response.text}")
    print()

def main():
    """Run all API tests"""
    print("🚀 HSEG AI API Testing Suite")
    print("=" * 50)

    try:
        test_health_check()
        test_individual_prediction()
        test_organizational_prediction()

        print("✅ All tests completed!")
        print("\n📖 Next steps:")
        print("• Visit http://localhost:8001/docs for interactive API documentation")
        print("• Upload CSV files using the /upload/survey-data endpoint")
        print("• Monitor system health at /health endpoint")

    except requests.ConnectionError:
        print("❌ Error: Could not connect to API server")
        print("Make sure the server is running on http://localhost:8001")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()