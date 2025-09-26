# Blucentia REST API Reference

## API Overview

The Blucentia Culture Intelligence Platform REST API provides comprehensive endpoints for psychological risk assessment, organizational health monitoring, and survey data management. Built with FastAPI, the API delivers high-performance, scalable solutions for enterprise culture assessment under the HSEG framework.

### Base Information
- **Base URL**: `https://api.blucentia.com/v1` (Production)
- **Base URL**: `https://staging-api.blucentia.com/v1` (Staging)
- **Protocol**: HTTPS only (TLS 1.3+)
- **Authentication**: Bearer Token (JWT)
- **API Version**: 1.0.0
- **Content-Type**: `application/json`

### Rate Limiting
| Endpoint Category | Limit | Window | Burst |
|-------------------|--------|---------|-------|
| Authentication | 10 requests | 1 minute | 20 |
| Predictions | 1,000 requests | 1 hour | 100 |
| Dashboard | 2,000 requests | 1 hour | 200 |
| Administration | 100 requests | 1 hour | 20 |
| Bulk Operations | 10 requests | 1 hour | 5 |

## Authentication

### JWT Token Authentication
All API endpoints (except login) require JWT authentication via the `Authorization` header.

```http
Authorization: Bearer <jwt_token>
```

### Login Endpoint
**POST** `/auth/login`

Authenticate user and receive JWT tokens.

#### Request Body
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "organization_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Response
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "role": "manager",
    "organization_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

#### Error Responses
```json
{
  "detail": "Invalid credentials",
  "status_code": 401,
  "error_code": "INVALID_CREDENTIALS"
}
```

## Health Check Endpoints

### System Health
**GET** `/health`

Check overall system health and dependencies.

#### Response
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "ml_pipeline": "healthy"
  },
  "response_time_ms": 45
}
```

### ML Pipeline Status
**GET** `/pipeline/status`

Check ML models and pipeline status.

#### Response
```json
{
  "status": "operational",
  "models": {
    "individual_risk_model": {
      "status": "loaded",
      "version": "2.1.0",
      "last_trained": "2025-01-10T08:00:00Z"
    },
    "text_risk_classifier": {
      "status": "loaded",
      "version": "1.8.5",
      "last_trained": "2025-01-12T14:30:00Z"
    },
    "organizational_model": {
      "status": "loaded",
      "version": "1.5.2",
      "last_trained": "2025-01-08T12:15:00Z"
    }
  }
}
```

## Prediction Endpoints

### Individual Risk Prediction
**POST** `/predict/individual`

Predict individual risk assessment and Culture Score.

#### Request Body
```json
{
  "response_id": "resp_001",
  "domain": "Business",
  "survey_responses": {
    "q1": 3.0, "q2": 2.5, "q3": 3.0, "q4": 2.0,
    "q5": 3.0, "q6": 3.0, "q7": 2.5,
    "q8": 3.0, "q9": 2.5, "q10": 3.0,
    "q11": 3.0, "q12": 2.5, "q13": 3.0, "q14": 2.5,
    "q15": 2.5, "q16": 2.5, "q17": 3.0, "q18": 3.0,
    "q19": 3.0, "q20": 3.0, "q21": 2.5, "q22": 3.0
  },
  "text_responses": {
    "q23": "Need more transparent communication from leadership",
    "q24": "Occasional stress during peak periods",
    "q25": "Good team collaboration and support"
  },
  "demographics": {
    "age_range": "25-34",
    "gender_identity": "Female",
    "tenure_range": "1-3_years",
    "position_level": "Mid",
    "department": "Engineering",
    "supervises_others": false,
    "work_location": "Hybrid",
    "employment_status": "Full_Time",
    "education_level": "Bachelors"
  },
  "response_quality": {
    "completion_rate": 0.95,
    "response_time_seconds": 420,
    "text_length_avg": 45
  }
}
```

#### Response
```json
{
  "response_id": "resp_001",
  "prediction_id": "pred_456789",
  "overall_culture_score": 68,
  "overall_risk_tier": "Safe",
  "confidence_score": 0.87,
  "category_scores": {
    "power_abuse": 2.8,
    "discrimination": 3.1,
    "manipulation": 2.9,
    "accountability": 2.6,
    "mental_health": 2.4,
    "voice_autonomy": 2.9
  },
  "text_risk_assessment": {
    "risk_level": "Low_Risk",
    "crisis_keywords_found": 0,
    "sentiment_score": 0.3,
    "intervention_required": false
  },
  "recommendations": [
    {
      "category": "accountability",
      "priority": "medium",
      "intervention": "Enhance transparency in decision-making processes",
      "expected_impact": 0.15
    }
  ],
  "metadata": {
    "prediction_timestamp": "2025-01-15T10:30:00Z",
    "model_version": "2.1.0",
    "processing_time_ms": 156
  }
}
```

### Batch Individual Predictions
**POST** `/predict/batch/individual`

Process multiple individual predictions in a single request.

#### Request Body
```json
{
  "batch_id": "batch_001",
  "responses": [
    {
      "response_id": "resp_001",
      "survey_responses": { /* survey data */ },
      "demographics": { /* demographic data */ }
    }
    // ... up to 1000 responses
  ]
}
```

#### Response
```json
{
  "batch_id": "batch_001",
  "total_responses": 250,
  "successful_predictions": 248,
  "failed_predictions": 2,
  "processing_time_ms": 3420,
  "results": [
    {
      "response_id": "resp_001",
      "culture_score": 68,
      "risk_tier": "Safe",
      "confidence": 0.87
    }
    // ... all predictions
  ],
  "errors": [
    {
      "response_id": "resp_099",
      "error": "Invalid survey response format",
      "error_code": "INVALID_FORMAT"
    }
  ]
}
```

### Organizational Risk Assessment
**POST** `/predict/organizational`

Generate organizational-level risk assessment and KPIs.

#### Request Body
```json
{
  "organization_id": "550e8400-e29b-41d4-a716-446655440000",
  "assessment_date": "2025-01-15",
  "filters": {
    "departments": ["Engineering", "Sales"],
    "tenure_range": ["1-3_years", "3-5_years"],
    "min_responses": 5
  }
}
```

#### Response
```json
{
  "organization_id": "550e8400-e29b-41d4-a716-446655440000",
  "assessment_id": "assess_789",
  "overall_assessment": {
    "average_culture_score": 64.5,
    "overall_risk_tier": "Safe",
    "total_responses": 1247,
    "response_rate": 0.78,
    "predicted_turnover_rate": 0.12
  },
  "risk_distribution": {
    "crisis": 0.03,
    "at_risk": 0.15,
    "mixed": 0.35,
    "safe": 0.32,
    "thriving": 0.15
  },
  "category_analysis": {
    "power_abuse": {
      "average_score": 2.8,
      "risk_level": "moderate",
      "trend": "improving"
    },
    "discrimination": {
      "average_score": 3.1,
      "risk_level": "low",
      "trend": "stable"
    }
    // ... other categories
  },
  "department_breakdown": [
    {
      "department": "Engineering",
      "culture_score": 67.2,
      "risk_tier": "Safe",
      "response_count": 234
    }
    // ... other departments
  ],
  "intervention_recommendations": [
    {
      "category": "mental_health",
      "priority": "high",
      "intervention": "Implement stress management programs",
      "affected_percentage": 0.28,
      "expected_improvement": 0.22
    }
  ],
  "metadata": {
    "assessment_timestamp": "2025-01-15T10:30:00Z",
    "model_version": "1.5.2",
    "processing_time_ms": 892
  }
}
```

## Organization Management

### List Organizations
**GET** `/organizations`

Retrieve paginated list of organizations (admin only).

#### Query Parameters
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `domain`: Filter by domain type
- `search`: Search by organization name

#### Response
```json
{
  "organizations": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "TechCorp Inc",
      "domain": "Business",
      "employee_count": 1500,
      "active_campaigns": 2,
      "last_assessment": "2025-01-10T00:00:00Z",
      "subscription_tier": "Enterprise"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3
  }
}
```

### Organization Risk Profile
**GET** `/organizations/{org_id}/risk-profile`

Get detailed risk profile for an organization.

#### Path Parameters
- `org_id`: Organization UUID

#### Query Parameters
- `date_range`: Date range (30d, 90d, 1y)
- `include_trends`: Include historical trends (default: true)

#### Response
```json
{
  "organization": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "TechCorp Inc",
    "domain": "Business"
  },
  "current_profile": {
    "culture_score": 64.5,
    "risk_tier": "Safe",
    "assessment_date": "2025-01-15",
    "total_responses": 1247
  },
  "historical_trends": {
    "culture_score_trend": [
      {"date": "2024-10-15", "score": 61.2},
      {"date": "2024-11-15", "score": 63.1},
      {"date": "2024-12-15", "score": 64.5}
    ],
    "risk_distribution_trend": [
      {
        "date": "2024-12-15",
        "distribution": {
          "crisis": 0.03,
          "at_risk": 0.15,
          "safe": 0.47,
          "thriving": 0.35
        }
      }
    ]
  },
  "benchmarks": {
    "industry_average": 62.1,
    "percentile_rank": 68,
    "similar_organizations": [
      {
        "name": "Anonymous Org A",
        "score": 66.2,
        "industry": "Technology"
      }
    ]
  }
}
```

## Campaign Management

### Process Campaign Data
**POST** `/campaigns/{campaign_id}/process`

Process survey responses for a campaign.

#### Path Parameters
- `campaign_id`: Campaign UUID

#### Request Body
```json
{
  "processing_mode": "full", // or "incremental"
  "notification_settings": {
    "email_on_completion": true,
    "webhook_url": "https://yourapp.com/webhook"
  }
}
```

#### Response
```json
{
  "campaign_id": "camp_123",
  "processing_job_id": "job_456",
  "status": "started",
  "estimated_completion": "2025-01-15T11:00:00Z",
  "response_count": 1247,
  "progress_url": "/campaigns/camp_123/status"
}
```

## Data Upload & Export

### Upload Survey Data
**POST** `/upload/survey-data`

Upload survey response data via CSV/Excel file.

#### Request (Multipart Form)
```http
Content-Type: multipart/form-data

campaign_id=camp_123
file=@survey_responses.csv
format=csv
validate_only=false
```

#### Response
```json
{
  "upload_id": "upload_789",
  "status": "processing",
  "total_rows": 1500,
  "valid_rows": 1487,
  "invalid_rows": 13,
  "errors": [
    {
      "row": 45,
      "error": "Missing required field: q1",
      "severity": "error"
    }
  ],
  "processing_url": "/upload/upload_789/status"
}
```

## Analytics Dashboard

### Dashboard Data
**GET** `/analytics/dashboard/{org_id}`

Get dashboard data for organization analytics.

#### Path Parameters
- `org_id`: Organization UUID

#### Query Parameters
- `date_range`: Date range (7d, 30d, 90d, 1y)
- `departments`: Comma-separated department list
- `metrics`: Requested metrics (culture_score,risk_distribution,trends)

#### Response
```json
{
  "organization_id": "550e8400-e29b-41d4-a716-446655440000",
  "date_range": "30d",
  "summary": {
    "culture_score": 64.5,
    "score_change": +2.3,
    "risk_tier": "Safe",
    "total_responses": 1247,
    "response_rate": 0.78,
    "predicted_turnover": 0.12
  },
  "kpis": [
    {
      "name": "Culture Score",
      "value": 64.5,
      "change": +2.3,
      "trend": "improving",
      "target": 70.0
    },
    {
      "name": "Employee Engagement",
      "value": 0.72,
      "change": +0.05,
      "trend": "improving",
      "target": 0.80
    }
  ],
  "charts": {
    "culture_score_trend": [
      {"date": "2024-12-16", "score": 62.2},
      {"date": "2024-12-23", "score": 63.1},
      {"date": "2024-12-30", "score": 64.5}
    ],
    "risk_distribution": {
      "crisis": 37,
      "at_risk": 187,
      "mixed": 436,
      "safe": 399,
      "thriving": 188
    },
    "department_comparison": [
      {
        "department": "Engineering",
        "culture_score": 67.2,
        "response_count": 234
      },
      {
        "department": "Sales",
        "culture_score": 61.8,
        "response_count": 189
      }
    ]
  }
}
```

## Error Handling

### Standard Error Response
All API errors follow a consistent format:

```json
{
  "detail": "Detailed error message",
  "status_code": 400,
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-01-15T10:30:00Z",
  "path": "/predict/individual",
  "request_id": "req_123456",
  "errors": [
    {
      "field": "survey_responses.q1",
      "message": "Value must be between 1 and 4",
      "code": "VALUE_OUT_OF_RANGE"
    }
  ]
}
```

### HTTP Status Codes
| Code | Description | Usage |
|------|-------------|--------|
| 200 | OK | Successful request |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request format/data |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Temporary service outage |

### Error Codes Reference
| Error Code | Description | Resolution |
|------------|-------------|-----------|
| `INVALID_CREDENTIALS` | Authentication failed | Check email/password |
| `VALIDATION_ERROR` | Request validation failed | Fix request format |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Retry after rate limit window |
| `MODEL_UNAVAILABLE` | ML model not loaded | Contact system administrator |
| `INSUFFICIENT_DATA` | Not enough data for prediction | Provide more responses |
| `ORGANIZATION_NOT_FOUND` | Organization doesn't exist | Verify organization ID |
| `CAMPAIGN_NOT_ACTIVE` | Campaign is not active | Check campaign status |

## SDK & Integration Examples

### Python SDK Example
```python
import requests
from typing import Dict, Any

class BlucentiaAPI:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    def predict_individual(self, survey_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get individual risk prediction"""
        response = requests.post(
            f"{self.base_url}/predict/individual",
            json=survey_data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_org_dashboard(self, org_id: str, date_range: str = "30d") -> Dict[str, Any]:
        """Get organization dashboard data"""
        params = {'date_range': date_range}
        response = requests.get(
            f"{self.base_url}/analytics/dashboard/{org_id}",
            params=params,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

# Usage
api = BlucentiaAPI("https://api.blucentia.com/v1", "your-api-key")

# Individual prediction
survey_data = {
    "response_id": "resp_001",
    "survey_responses": {"q1": 3.0, "q2": 2.5, ...},
    "demographics": {"age_range": "25-34", ...}
}
prediction = api.predict_individual(survey_data)
print(f"Culture Score: {prediction['overall_culture_score']}")
```

### cURL Examples
```bash
# Individual Prediction
curl -X POST "https://api.blucentia.com/v1/predict/individual" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "response_id": "resp_001",
       "survey_responses": {
         "q1": 3.0, "q2": 2.5, "q3": 3.0
       },
       "demographics": {
         "age_range": "25-34",
         "department": "Engineering"
       }
     }'

# Get Organization Dashboard
curl -X GET "https://api.blucentia.com/v1/analytics/dashboard/550e8400-e29b-41d4-a716-446655440000?date_range=30d" \
     -H "Authorization: Bearer YOUR_API_KEY"

# Health Check
curl -X GET "https://api.blucentia.com/v1/health"
```

### JavaScript/Node.js Example
```javascript
const axios = require('axios');

class BlucentiaClient {
    constructor(baseURL, apiKey) {
        this.client = axios.create({
            baseURL,
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            }
        });
    }

    async predictIndividual(surveyData) {
        try {
            const response = await this.client.post('/predict/individual', surveyData);
            return response.data;
        } catch (error) {
            console.error('Prediction error:', error.response?.data);
            throw error;
        }
    }

    async getOrganizationProfile(orgId) {
        try {
            const response = await this.client.get(`/organizations/${orgId}/risk-profile`);
            return response.data;
        } catch (error) {
            console.error('Profile error:', error.response?.data);
            throw error;
        }
    }
}

// Usage
const client = new BlucentiaClient(
    'https://api.blucentia.com/v1',
    'your-api-key'
);

// Async/await usage
(async () => {
    try {
        const prediction = await client.predictIndividual({
            response_id: 'resp_001',
            survey_responses: { q1: 3.0, q2: 2.5 },
            demographics: { age_range: '25-34' }
        });

        console.log('Culture Score:', prediction.overall_culture_score);
        console.log('Risk Tier:', prediction.overall_risk_tier);
    } catch (error) {
        console.error('API Error:', error.message);
    }
})();
```

## Webhook Integration

### Webhook Events
The API can send webhook notifications for various events:

| Event | Description | Payload |
|-------|-------------|---------|
| `prediction.completed` | Individual prediction finished | `{type, prediction_id, culture_score}` |
| `campaign.processed` | Campaign processing finished | `{type, campaign_id, total_responses}` |
| `organization.alert` | Risk threshold exceeded | `{type, org_id, risk_level, threshold}` |

### Webhook Configuration
```json
{
  "webhook_url": "https://yourapp.com/webhooks/blucentia",
  "events": ["prediction.completed", "campaign.processed"],
  "secret": "your-webhook-secret",
  "retry_policy": {
    "max_attempts": 3,
    "backoff_multiplier": 2
  }
}
```

### Webhook Security
Webhooks include HMAC signature for verification:

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

## Rate Limiting & Quotas

### Rate Limit Headers
All responses include rate limiting information:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248000
X-RateLimit-Window: 3600
```

### Quota Management
Enterprise customers have additional quotas:

| Resource | Free Tier | Professional | Enterprise |
|----------|-----------|--------------|------------|
| Predictions/month | 1,000 | 50,000 | Unlimited |
| Organizations | 1 | 10 | Unlimited |
| API Requests/hour | 1,000 | 10,000 | Custom |
| Webhook Events | 100/day | 10,000/day | Unlimited |

## API Versioning

### Version Strategy
- **URL Versioning**: Version in URL path (`/v1/`, `/v2/`)
- **Backward Compatibility**: Maintained for 12 months
- **Deprecation Notice**: 90-day notice for breaking changes

### Version Migration
```json
{
  "current_version": "1.0.0",
  "supported_versions": ["1.0.0"],
  "deprecated_versions": [],
  "migration_guide": "https://docs.blucentia.com/migration/v1-to-v2"
}
```

This comprehensive API reference provides all necessary information for integrating with the Blucentia Culture Intelligence Platform, including detailed examples, error handling, and best practices for enterprise implementation.