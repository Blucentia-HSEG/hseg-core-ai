import requests
import json

BASE_URL = "http://localhost:8001"

def test_individual():
    print("Testing individual prediction...")
    data = {
        "response_id": "test_001",
        "domain": "Business",
        "survey_responses": {
            "q1": 2.0, "q2": 3.0, "q3": 3.0, "q4": 2.5, "q5": 3.0,
            "q6": 2.0, "q7": 3.5, "q8": 2.5, "q9": 3.0, "q10": 2.5,
            "q11": 3.0, "q12": 2.0, "q13": 3.5, "q14": 2.5, "q15": 3.0,
            "q16": 2.5, "q17": 3.0, "q18": 2.0, "q19": 3.5, "q20": 2.5,
            "q21": 3.0, "q22": 2.5
        },
        "text_responses": {
            "Q23": "Management needs better communication",
            "Q24": "Work stress affecting sleep and anxiety", 
            "Q25": "Technical resources are excellent"
        },
        "demographics": {
            "age_range": "35-44",
            "gender_identity": "Woman",
            "tenure_range": "1-3_years",
            "position_level": "Mid",
            "department": "Engineering"
        }
    }
    response = requests.post(f"{BASE_URL}/predict/individual", json=data)
    if response.status_code == 200:
        result = response.json()
        print(f"SUCCESS! HSEG Score: {result[\"overall_hseg_score\"]:.2f}")
        print(f"Risk Tier: {result[\"overall_risk_tier\"]}")
        print(f"Processing Time: {result[\"processing_time_ms\"]:.1f}ms")

if __name__ == "__main__":
    print("HSEG AI API Test")
    test_individual()
