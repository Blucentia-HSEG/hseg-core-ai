# HSEG AI System - Psychological Risk Assessment Platform

A comprehensive AI-powered system for assessing psychological safety and workplace culture risks across Healthcare, Universities, and Business organizations.

## 🎯 System Overview

The HSEG (Healthcare, Schools, Enterprise, Government) AI System provides:

- **Individual Risk Assessment**: ML-powered psychological risk prediction for individual employees
- **Text Crisis Detection**: NLP analysis of open-ended responses to identify crisis situations
- **Organizational Risk Aggregation**: Company-wide culture health assessment and benchmarking
- **Real-time Intervention Recommendations**: Actionable guidance for culture improvement
- **Complete REST API**: Full integration capabilities for dashboards and applications

## 🏗️ Project Structure

```
ai-modeling/
├── app/                          # Main application code
│   ├── api/                      # FastAPI endpoints
│   │   └── main.py              # REST API server
│   ├── config/                   # Configuration files
│   │   └── database_config.py   # Database configuration
│   ├── core/                     # Core business logic
│   │   └── ml_pipeline.py       # ML pipeline integration
│   └── models/                   # ML models and database models
│       ├── database_models.py   # SQLAlchemy models
│       ├── individual_risk_model.py    # Individual risk prediction
│       ├── text_risk_classifier.py     # Text crisis detection
│       └── organizational_risk_model.py # Organizational assessment
├── docker/                       # Docker configuration
│   ├── docker-compose.yml       # Container orchestration
│   ├── docker-entrypoint.sh     # Startup script
│   └── nginx.conf               # Reverse proxy config
├── tests/                        # Test files
├── docs/                         # Documentation
├── scripts/                      # Utility scripts
├── database/                     # Database files (generated)
├── Dockerfile                    # Docker image definition
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🚀 Quick Start

### Docker Deployment (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd ai-modeling

# Build and run with Docker
docker build -t hseg-ai .
docker run -p 8000:8000 hseg-ai

# Or use Docker Compose
cd docker
docker-compose up -d
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app.config.database_config import create_database; create_database()"

# Start server
uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

### First Time Setup

```bash
# Train models (first run only)
docker exec -it hseg-ai-api train-models

# Check system health
curl http://localhost:8000/health

# Access API documentation
open http://localhost:8000/docs
```

## 📊 API Usage Examples

### Individual Risk Prediction

```python
import requests

# Predict individual psychological risk
response = requests.post("http://localhost:8000/predict/individual", json={
    "domain": "Business",
    "survey_responses": {
        "q1": 2.0,  # Safe speaking up
        "q2": 3.0,  # Leadership silencing
        "q3": 3.0,  # Fear consequences
        # ... Q4-Q22
    },
    "text_responses": {
        "Q23": "My manager constantly yells and threatens employees",
        "Q24": "Work stress is causing panic attacks",
        "Q25": "Great technical resources when management isn't involved"
    },
    "demographics": {
        "age_range": "35-44",
        "gender_identity": "Woman",
        "tenure_range": "1-3_years",
        "position_level": "Mid",
        "department": "Engineering"
    }
})

result = response.json()
print(f"Risk Tier: {result['overall_risk_tier']}")
print(f"HSEG Score: {result['overall_hseg_score']}/28")
```

### Organizational Assessment

```python
# Predict organizational risk from multiple individuals
org_request = {
    "organization_info": {
        "org_id": "tech_company_001",
        "org_name": "TechFlow Industries",
        "domain": "Business",
        "employee_count": 450
    },
    "individual_responses": [
        # List of individual survey responses (minimum 5)
        {...}, {...}, {...}
    ]
}

response = requests.post("http://localhost:8000/predict/organizational", json=org_request)
org_assessment = response.json()

print(f"Organization Risk: {org_assessment['overall_assessment']['overall_risk_tier']}")
print(f"Turnover Risk: {org_assessment['overall_assessment']['predicted_turnover_rate']:.1%}")
```

### File Upload

```python
# Upload CSV of survey data
with open("survey_responses.csv", "rb") as f:
    response = requests.post(
        "http://localhost:8000/upload/survey-data",
        files={"file": f},
        headers={"Authorization": "Bearer test-token"}
    )

upload_result = response.json()
print(f"Processed {upload_result['successful_predictions']} responses")
```

## 🔧 Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=sqlite:///./data/hseg_database.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1

# Model Configuration
MODEL_VERSION=v1.0.0
ENABLE_MODEL_TRAINING=true
MODEL_CACHE_SIZE=100

# Security
SECRET_KEY=your-secret-key-here
ENABLE_AUTH=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/hseg.log
```

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
pytest

# Test specific components
pytest tests/test_individual_model.py
pytest tests/test_text_classifier.py
pytest tests/test_api_endpoints.py

## 📋 Sample Questionnaire Payloads

Use these base values to quickly test the API without hunting for inputs. They match the improved survey and HSEG scoring documentation.

### Individual Prediction (POST `/predict/individual`)

```bash
curl -X POST http://localhost:8000/predict/individual \
  -H "Content-Type: application/json" \
  -d '{
    "response_id": "sample_001",
    "domain": "Business",
    "survey_responses": {
      "q1": 3.0, "q2": 3.0, "q3": 2.5, "q4": 3.0,
      "q5": 3.0, "q6": 3.0, "q7": 2.5,
      "q8": 3.0, "q9": 2.5, "q10": 3.0,
      "q11": 3.0, "q12": 2.5, "q13": 3.0, "q14": 2.5,
      "q15": 2.5, "q16": 2.5, "q17": 3.0, "q18": 3.0,
      "q19": 3.0, "q20": 3.0, "q21": 2.5, "q22": 3.0
    },
    "text_responses": {
      "q23": "Improve transparency in decisions affecting teams.",
      "q24": "Work has caused occasional anxiety in busy periods.",
      "q25": "Strong peer collaboration and knowledge sharing."
    },
    "demographics": {
      "age_range": "25-34",
      "gender_identity": "Prefer_not_to_say",
      "tenure_range": "1-3_years",
      "position_level": "Mid",
      "department": "Engineering",
      "supervises_others": false,
      "work_location": "Hybrid",
      "employment_status": "Full_Time",
      "education_level": "Bachelors"
    }
  }'
```

Expected: Response contains `overall_hseg_score` on the 28‑point scale, tier in [`Crisis`,`At Risk`,`Mixed`,`Safe`,`Thriving`], `category_scores` on 1–4.

### Organizational Prediction (POST `/predict/organizational`)

Requires 5+ individual responses. This payload provides five varied employees for a quick end‑to‑end test.

```bash
curl -X POST http://localhost:8000/predict/organizational \
  -H "Content-Type: application/json" \
  -d '{
    "organization_info": {
      "org_id": "org_demo_001",
      "org_name": "Demo Org",
      "domain": "Business",
      "employee_count": 120
    },
    "individual_responses": [
      {"response_id":"e1","domain":"Business","survey_responses":{"q1":3,"q2":3,"q3":3,"q4":3,"q5":3,"q6":3,"q7":3,"q8":3,"q9":3,"q10":3,"q11":3,"q12":3,"q13":3,"q14":3,"q15":3,"q16":3,"q17":3,"q18":3,"q19":3,"q20":3,"q21":3,"q22":3},"text_responses":{},"demographics":{"age_range":"25-34","gender_identity":"Man","tenure_range":"1-3_years","position_level":"Mid","department":"Engineering"}},
      {"response_id":"e2","domain":"Business","survey_responses":{ "q1":2.5,"q2":2.5,"q3":2.5,"q4":2.5,"q5":2.5,"q6":2.5,"q7":2.5,"q8":2.5,"q9":2.5,"q10":2.5,"q11":2.5,"q12":2.5,"q13":2.5,"q14":2.5,"q15":2.5,"q16":2.5,"q17":2.5,"q18":2.5,"q19":2.5,"q20":2.5,"q21":2.5,"q22":2.5},"text_responses":{},"demographics":{"age_range":"35-44","gender_identity":"Woman","tenure_range":"4-7_years","position_level":"Senior","department":"Sales"}},
      {"response_id":"e3","domain":"Business","survey_responses":{ "q1":3.5,"q2":3.5,"q3":3.0,"q4":3.5,"q5":3.5,"q6":3.0,"q7":3.0,"q8":3.5,"q9":3.0,"q10":3.5,"q11":3.0,"q12":3.0,"q13":3.5,"q14":3.0,"q15":3.0,"q16":3.5,"q17":3.0,"q18":3.0,"q19":3.5,"q20":3.0,"q21":3.0,"q22":3.5},"text_responses":{},"demographics":{"age_range":"45-54","gender_identity":"Non-binary","tenure_range":"8+_years","position_level":"Executive","department":"Operations"}},
      {"response_id":"e4","domain":"Business","survey_responses":{ "q1":2.0,"q2":2.0,"q3":2.0,"q4":2.0,"q5":2.0,"q6":2.0,"q7":2.0,"q8":2.0,"q9":2.0,"q10":2.0,"q11":2.0,"q12":2.0,"q13":2.0,"q14":2.0,"q15":2.0,"q16":2.0,"q17":2.0,"q18":2.0,"q19":2.0,"q20":2.0,"q21":2.0,"q22":2.0},"text_responses":{},"demographics":{"age_range":"18-24","gender_identity":"Man","tenure_range":"<1_year","position_level":"Entry","department":"Support"}},
      {"response_id":"e5","domain":"Business","survey_responses":{ "q1":3.0,"q2":2.5,"q3":2.5,"q4":3.0,"q5":3.0,"q6":2.5,"q7":2.5,"q8":3.0,"q9":2.5,"q10":3.0,"q11":3.0,"q12":2.5,"q13":3.0,"q14":2.5,"q15":2.5,"q16":2.5,"q17":3.0,"q18":3.0,"q19":3.0,"q20":3.0,"q21":2.5,"q22":3.0},"text_responses":{},"demographics":{"age_range":"25-34","gender_identity":"Prefer_not_to_say","tenure_range":"1-3_years","position_level":"Mid","department":"Engineering"}}
    ]
  }'
```

Expected: Response includes `overall_assessment`, `category_breakdown`, `risk_indicators`, and top intervention recommendations.

## 🚀 Run The Portal (Step‑By‑Step)

The “portal” refers to the React frontend (this repo) that talks to the FastAPI backend.

1) Prepare models (from the final dataset)
- `python scripts/train_all_from_final_dataset.py`
  - Produces `.pkl` artifacts under `app/models/trained/`
  - See `docs/models.md` for detailed model architecture and training information
  - Individual training scripts available in `scripts/models/` directory

2) Start API (FastAPI)
- `pip install -r requirements.txt`
- `uvicorn app.api.main:app --host 0.0.0.0 --port 8000`
- Verify: open `http://localhost:8000/health` and `http://localhost:8000/docs`

3) Start Frontend (React)
- `cd frontend`
- `npm install`
- Set API URL (one‑shot):
  - Linux/macOS: `export REACT_APP_API_URL=http://localhost:8000`
  - Windows (PowerShell): `$env:REACT_APP_API_URL = 'http://localhost:8000'`
- `npm start`
- Open `http://localhost:3000` in your browser

4) Test the flow
- Submit the survey form in the portal, or use the curl samples above.
- Check the System Status card in the portal to confirm models are loaded and health is “healthy”.

Optional: Docker
- Build: `docker build -t hseg-ai .`
- Run: `docker run -p 8000:8000 hseg-ai`
- Health: `curl http://localhost:8000/health`

# Test with coverage
pytest --cov=app --cov-report=html
```

### Integration Tests

```bash
# Test complete pipeline
python -c "
import asyncio
from app.core.ml_pipeline import HSEGMLPipeline

async def test():
    pipeline = HSEGMLPipeline()
    await pipeline.initialize_models()
    print('Pipeline test passed')

asyncio.run(test())
"
```

## 📊 Data Schema

### Survey Response Format

```json
{
  "response_id": "resp_001",
  "domain": "Healthcare|University|Business",
  "survey_responses": {
    "q1": 2.0,  // 1.0-4.0 scale
    "q2": 3.0,
    // ... Q1-Q22
  },
  "text_responses": {
    "Q23": "Change one thing response",
    "Q24": "Mental health impact",
    "Q25": "Workplace strength"
  },
  "demographics": {
    "age_range": "25-34",
    "gender_identity": "Woman",
    "tenure_range": "1-3_years",
    "position_level": "Mid",
    "department": "Engineering",
    "supervises_others": false
  }
}
```

### Risk Assessment Output

```json
{
  "overall_hseg_score": 12.3,  // 7.0-28.0 scale
  "overall_risk_tier": "Crisis|At_Risk|Mixed|Safe|Thriving",
  "category_scores": {
    "1": 8.2,  // Power Abuse
    "2": 11.4, // Discrimination
    "3": 14.8, // Manipulation
    "4": 9.7,  // Accountability
    "5": 10.1, // Mental Health
    "6": 13.6  // Voice/Autonomy
  },
  "predicted_outcomes": {
    "predicted_turnover_rate": 0.45,
    "predicted_legal_risk": 0.25,
    "predicted_productivity_impact": -0.3
  },
  "intervention_recommendations": [
    {
      "category": "Power Abuse & Suppression",
      "intervention": "Management training on psychological safety",
      "urgency": "Immediate",
      "estimated_effort": "Medium",
      "expected_impact": "High"
    }
  ]
}
```

## 🔒 Security Considerations

### Authentication

- Bearer token authentication for API endpoints
- Rate limiting implemented via Nginx
- Input validation with Pydantic models
- SQL injection protection via SQLAlchemy ORM

### Data Privacy

- All survey responses are anonymized
- No personally identifiable information stored
- Aggregation minimums enforced (minimum 5 responses)
- Secure data transmission (HTTPS required in production)
- GDPR/CCPA compliance features built-in

## 🚀 Production Deployment

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hseg-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hseg-api
  template:
    metadata:
      labels:
        app: hseg-api
    spec:
      containers:
      - name: hseg-api
        image: hseg-ai:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          value: "sqlite:///./data/hseg_database.db"
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 30
```

## 📈 Performance Monitoring

### Health Monitoring

```python
# Get pipeline performance
response = requests.get("http://localhost:8000/pipeline/status")
metrics = response.json()

print(f"Total predictions: {metrics['performance_stats']['total_predictions']}")
print(f"Success rate: {metrics['performance_stats']['successful_predictions'] / metrics['performance_stats']['total_predictions']:.2%}")
print(f"Average processing time: {metrics['performance_stats']['average_processing_time']:.2f}ms")
```

## 🛠️ Development

### Setup Development Environment

```bash
# Clone repository
git clone <repository-url>
cd ai-modeling

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black isort flake8 mypy

# Initialize database
python -c "from app.config.database_config import create_database; create_database()"
```

### Code Quality

```bash
# Format code
black app/
isort app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

## 📚 Architecture Components

### Core Components

1. **Database Layer** (`app/config/database_config.py`, `app/models/database_models.py`)
   - Serverless SQLite with BCNF normalization
   - Async database operations with connection pooling
   - Complete schema for surveys, responses, and risk assessments

2. **ML Models**
   - **Individual Risk Predictor** (`app/models/individual_risk_model.py`): XGBoost + Neural Network ensemble
   - **Text Risk Classifier** (`app/models/text_risk_classifier.py`): BERT-based crisis detection
   - **Organizational Aggregator** (`app/models/organizational_risk_model.py`): LightGBM organizational assessment

3. **ML Pipeline** (`app/core/ml_pipeline.py`)
   - Complete integration of all three models
   - Background processing and database storage
   - Performance monitoring and error handling

4. **REST API** (`app/api/main.py`)
   - FastAPI-based web server
   - Authentication and authorization
   - File upload and batch processing
   - Dashboard data endpoints

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🆘 Support

For technical support or questions:
- Create an issue in the repository
- Email: support@hseg.org
- Documentation: https://docs.hseg.org

---

**HSEG AI System** - Transforming workplace psychological safety through AI-powered culture assessment.
