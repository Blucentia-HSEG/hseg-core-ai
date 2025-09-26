# Blucentia System Architecture
## HSEG Culture Intelligence Platform Technical Design

## Executive Overview

The Blucentia Culture Intelligence Platform is a comprehensive enterprise solution operating under the HSEG (Human Sustainability Enterprise Group) framework. Built on modern microservices architecture, the system processes multi-domain survey data through advanced AI/ML pipelines to deliver actionable insights for organizational culture transformation across Healthcare, Schools, Enterprise, and Government sectors.

### Key System Capabilities
- **Multi-Domain Assessment**: Healthcare, Schools, Enterprise, Government sectors
- **HSEG Tier Classification**: Five-tier assessment model (Crisis to Thriving)
- **Social Pressure Integration**: Work War subsidiary social media intelligence
- **Real-time Risk Assessment**: Sub-second individual predictions with crisis detection
- **Enterprise Scale**: Supports 100,000+ employees per organization
- **Multi-tenancy**: Secure isolation for multiple organizations
- **Regulatory Compliance**: GDPR, HIPAA, SOX, OSHA compliant data handling
- **High Availability**: 99.9% uptime SLA with disaster recovery

### HSEG Ecosystem Integration
The Blucentia platform operates as part of the broader HSEG ecosystem:
- **Blucentia Core**: Culture intelligence and assessment platform
- **HSEG Lab**: Academic research and data processing division
- **Work War Integration**: Social media pressure and accountability tracking
- **Watch List System**: Binary partnership model with public accountability

## System Architecture Overview

### High-Level Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  React SPA  │  Survey UI  │  Dashboard  │  Admin Portal  │     │
└─────────────────────────────────────────────────────────────────┘
                                  │
                           ┌─────────────┐
                           │   API GW    │
                           │   (Nginx)   │
                           └─────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                         │
├─────────────────────────────────────────────────────────────────┤
│                       FastAPI Server                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │   Auth   │ │   API    │ │ Business │ │   ML     │          │
│  │ Service  │ │ Gateway  │ │  Logic   │ │ Pipeline │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
└─────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────┐
│                         Data Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │PostgreSQL│ │  Redis   │ │   S3     │ │   ML     │          │
│  │    DB    │ │  Cache   │ │ Storage  │ │ Models   │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## Frontend Architecture

### Technology Stack
- **Framework**: React 18.x with TypeScript
- **State Management**: Context API + useReducer
- **UI Components**: Material-UI v5
- **Charts/Visualization**: Recharts + D3.js
- **Build System**: Vite with ES modules
- **Testing**: Jest + React Testing Library

### Component Architecture
```
src/
├── components/
│   ├── common/           # Reusable UI components
│   ├── survey/           # Survey form components
│   ├── dashboard/        # Analytics dashboards
│   └── admin/           # Administrative interfaces
├── hooks/               # Custom React hooks
├── services/            # API client services
├── utils/              # Helper functions
└── types/              # TypeScript definitions
```

### Key Components
#### Survey Interface
- **Adaptive Forms**: Dynamic question rendering based on response patterns
- **Progress Tracking**: Real-time completion indicators
- **Validation**: Client-side validation with server-side verification
- **Accessibility**: WCAG 2.1 AA compliant

#### Dashboard Components
- **Risk Visualization**: Interactive heatmaps and trend charts
- **KPI Widgets**: Real-time organizational metrics
- **Drill-down Analysis**: Department/team-level insights
- **Export Functionality**: PDF/Excel report generation

#### Admin Portal
- **User Management**: Role-based access control
- **Organization Setup**: Multi-tenant configuration
- **Campaign Management**: Survey deployment and tracking
- **System Monitoring**: Health checks and performance metrics

### State Management Pattern
```javascript
// Global State Structure
interface AppState {
  auth: AuthState;
  survey: SurveyState;
  dashboard: DashboardState;
  admin: AdminState;
}

// Context-based State Management
const StateContext = React.createContext<AppState>();
const DispatchContext = React.createContext<Dispatch<Action>>();
```

### API Integration
- **HTTP Client**: Axios with request/response interceptors
- **Error Handling**: Centralized error boundary with user-friendly messages
- **Caching**: React Query for server state management
- **Real-time Updates**: WebSocket integration for live dashboard updates

## Backend Architecture

### Technology Stack
- **Framework**: FastAPI with Python 3.11
- **ASGI Server**: Uvicorn with multiprocessing
- **ORM**: SQLAlchemy 2.0 with async support
- **Task Queue**: Celery with Redis broker
- **Caching**: Redis with clustering support
- **Monitoring**: Prometheus + Grafana

### Application Structure
```
app/
├── api/                # API endpoints and routing
├── core/              # Business logic and ML pipeline
├── models/            # Data models and ML models
├── config/            # Configuration management
├── services/          # External service integrations
├── utils/             # Utility functions
└── tests/             # Test suite
```

### API Layer Architecture
#### Endpoint Categories
| Category | Purpose | Authentication | Rate Limiting |
|----------|---------|---------------|---------------|
| `/auth` | Authentication & authorization | None (for login) | 10/min |
| `/predict` | ML prediction endpoints | Required | 1000/hour |
| `/organizations` | Organization management | Admin only | 100/hour |
| `/campaigns` | Survey campaign management | Manager+ | 500/hour |
| `/analytics` | Dashboard data endpoints | Required | 2000/hour |
| `/admin` | System administration | Admin only | 50/hour |

#### Request/Response Flow
```python
# Typical API Request Flow
@app.post("/predict/individual")
async def predict_individual(
    request: SurveyResponseData,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Request validation
    validated_data = await validate_request(request)

    # 2. Business logic
    prediction = await ml_pipeline.predict_individual(validated_data)

    # 3. Database operations
    await store_prediction(db, prediction, current_user.org_id)

    # 4. Response formatting
    return format_prediction_response(prediction)
```

### Core Business Logic
#### ML Pipeline Integration
```python
class MLPipeline:
    def __init__(self):
        self.individual_model = IndividualRiskPredictor()
        self.text_classifier = TextRiskClassifier()
        self.org_aggregator = OrganizationalRiskAggregator()

    async def predict_individual(self, data: SurveyData) -> Prediction:
        # Feature engineering
        features = await self.engineer_features(data)

        # Model inference
        risk_scores = self.individual_model.predict(features)
        text_risk = self.text_classifier.predict(data.text_responses)

        # Score calculation
        culture_score = calculate_culture_score(risk_scores)

        return Prediction(
            culture_score=culture_score,
            risk_tier=determine_risk_tier(culture_score),
            category_scores=risk_scores,
            text_risk_level=text_risk,
            confidence=calculate_confidence(features)
        )
```

#### Security Implementation
- **Authentication**: JWT tokens with refresh mechanism
- **Authorization**: Role-based access control (RBAC)
- **Data Encryption**: AES-256 encryption for sensitive data
- **API Security**: OWASP Top 10 compliance
- **Audit Logging**: Comprehensive activity logging

### Database Architecture

#### Schema Design
```sql
-- Core Entities
Organizations
├── id (UUID, PK)
├── name (VARCHAR)
├── domain (ENUM: Healthcare/Education/Business/Government)
├── settings (JSONB)
└── created_at (TIMESTAMP)

SurveyCampaigns
├── id (UUID, PK)
├── organization_id (UUID, FK)
├── name (VARCHAR)
├── status (ENUM: Active/Completed/Paused)
├── target_responses (INTEGER)
└── configuration (JSONB)

SurveyResponses
├── id (UUID, PK)
├── campaign_id (UUID, FK)
├── response_data (JSONB)
├── demographics (JSONB)
├── text_responses (JSONB)
├── culture_score (DECIMAL)
├── risk_tier (VARCHAR)
└── submitted_at (TIMESTAMP)

OrganizationRiskProfiles
├── id (UUID, PK)
├── organization_id (UUID, FK)
├── assessment_date (DATE)
├── metrics (JSONB)
├── risk_distribution (JSONB)
└── recommendations (JSONB)
```

#### Data Management
- **Partitioning**: Time-based partitioning for survey responses
- **Indexing**: Optimized indexes for common query patterns
- **Archiving**: Automated data lifecycle management
- **Backup**: Point-in-time recovery with 99.99% durability
- **Privacy**: Data anonymization and right-to-deletion compliance

### Caching Strategy
#### Multi-layered Caching
```python
# Cache Configuration
CACHE_CONFIG = {
    'model_predictions': {'ttl': 3600, 'max_size': 10000},
    'dashboard_data': {'ttl': 300, 'max_size': 1000},
    'user_sessions': {'ttl': 1800, 'sliding': True},
    'organization_config': {'ttl': 86400, 'max_size': 100}
}
```

#### Cache Invalidation
- **Event-driven**: Cache invalidation on data updates
- **Time-based**: TTL-based expiration for stale data
- **Manual**: Administrative cache refresh capabilities
- **Pattern-based**: Bulk invalidation using key patterns

## ML Model Deployment Architecture

### Model Serving Infrastructure
```python
# Model Loading Strategy
class ModelManager:
    def __init__(self):
        self.models = {}
        self.load_models()

    def load_models(self):
        """Load all models into memory on startup"""
        self.models = {
            'individual': joblib.load('models/individual_risk_model.pkl'),
            'text': joblib.load('models/text_risk_classifier.pkl'),
            'organizational': joblib.load('models/organizational_risk_model.pkl')
        }

    async def predict(self, model_name: str, features: np.ndarray):
        """Thread-safe model inference"""
        model = self.models[model_name]
        return model.predict(features)
```

### Model Versioning & Deployment
- **Version Control**: Git-based model versioning with semantic versioning
- **A/B Testing**: Canary deployments for model updates
- **Rollback**: Instant rollback to previous model versions
- **Health Checks**: Model performance monitoring and alerting

### Feature Store
- **Feature Engineering**: Centralized feature computation
- **Feature Serving**: Low-latency feature retrieval
- **Feature Monitoring**: Data drift detection
- **Feature Lineage**: End-to-end feature tracking

## Security Architecture

### Authentication & Authorization
```python
# RBAC Implementation
class RolePermissions:
    ROLES = {
        'admin': ['*'],
        'manager': ['read:org', 'write:campaigns', 'read:analytics'],
        'analyst': ['read:org', 'read:analytics'],
        'user': ['read:self', 'write:responses']
    }

    def check_permission(self, user_role: str, action: str) -> bool:
        permissions = self.ROLES.get(user_role, [])
        return '*' in permissions or action in permissions
```

### Data Protection
- **Encryption at Rest**: AES-256 database encryption
- **Encryption in Transit**: TLS 1.3 for all communications
- **Key Management**: HashiCorp Vault for secret management
- **Data Masking**: PII masking in non-production environments

### Compliance Framework
- **GDPR**: Data subject rights implementation
- **HIPAA**: Healthcare data protection (when applicable)
- **SOX**: Financial controls for public companies
- **ISO 27001**: Information security management

## Deployment & Infrastructure

### Container Architecture
```dockerfile
# Multi-stage Docker Build
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: culture-score-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: culture-score-api
  template:
    spec:
      containers:
      - name: api
        image: culture-score:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

### Infrastructure Components
- **Load Balancer**: AWS ALB with SSL termination
- **Auto Scaling**: Horizontal pod autoscaling based on CPU/memory
- **Database**: Amazon RDS PostgreSQL with Multi-AZ
- **Cache**: Amazon ElastiCache Redis cluster
- **Storage**: Amazon S3 for model artifacts and exports
- **CDN**: CloudFront for static asset delivery

### Monitoring & Observability
```python
# Application Metrics
from prometheus_client import Counter, Histogram, Gauge

# Custom Metrics
prediction_requests = Counter('predictions_total', 'Total predictions', ['model_type'])
prediction_latency = Histogram('prediction_duration_seconds', 'Prediction latency')
active_users = Gauge('active_users', 'Current active users')
```

#### Monitoring Stack
- **Metrics**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: Jaeger for distributed tracing
- **Alerting**: PagerDuty integration for critical alerts

### Disaster Recovery
- **Backup Strategy**:
  - Database: Point-in-time recovery with 7-day retention
  - Model Artifacts: Cross-region replication
  - Configuration: Git-based infrastructure as code
- **RTO/RPO**:
  - Recovery Time Objective: < 4 hours
  - Recovery Point Objective: < 15 minutes
- **Failover**: Automated failover to secondary region

## Performance Optimization

### Application Performance
- **Response Times**:
  - Individual Prediction: < 200ms (p95)
  - Dashboard Load: < 500ms (p95)
  - Bulk Processing: < 5 seconds per 1000 responses
- **Throughput**: 10,000 concurrent requests
- **Resource Utilization**: < 70% CPU/Memory under normal load

### Database Optimization
- **Query Optimization**: Index optimization and query analysis
- **Connection Pooling**: PgBouncer for connection management
- **Read Replicas**: Read-only replicas for analytics queries
- **Partitioning**: Time-based partitioning for large tables

### Caching Strategies
- **Application Cache**: Redis for session and computed data
- **CDN Cache**: Static assets and public data
- **Database Cache**: Query result caching
- **Model Cache**: In-memory model serving

## API Rate Limiting & Throttling

### Rate Limiting Strategy
```python
# Rate Limiting Configuration
RATE_LIMITS = {
    'auth': '10/minute',
    'predict': '1000/hour',
    'dashboard': '2000/hour',
    'admin': '100/hour',
    'bulk': '10/hour'
}

# Implementation
@limiter.limit("1000/hour")
@app.post("/predict/individual")
async def predict_individual():
    # Endpoint implementation
    pass
```

### Circuit Breaker Pattern
- **Failure Threshold**: 50% error rate over 1 minute
- **Recovery Time**: 30 seconds before retry
- **Fallback**: Heuristic predictions when models unavailable

## Quality Assurance

### Testing Strategy
- **Unit Tests**: 90%+ code coverage
- **Integration Tests**: API endpoint testing
- **Load Tests**: Performance benchmarking
- **Security Tests**: OWASP ZAP automated scanning
- **End-to-End Tests**: Cypress for user workflows

### Code Quality
- **Static Analysis**: SonarQube for code quality metrics
- **Linting**: ESLint (Frontend), Black/Flake8 (Backend)
- **Type Checking**: TypeScript (Frontend), mypy (Backend)
- **Documentation**: Automated API documentation with OpenAPI

### Deployment Pipeline
1. **Code Commit**: Git workflow with pull request reviews
2. **CI/CD Pipeline**: GitHub Actions with automated testing
3. **Security Scanning**: Container and dependency vulnerability scanning
4. **Staging Deployment**: Automated deployment to staging environment
5. **Production Deployment**: Manual approval gate with rollback capability

This architecture provides a robust, scalable foundation for the Culture Score platform while maintaining security, compliance, and performance standards required for enterprise deployment.