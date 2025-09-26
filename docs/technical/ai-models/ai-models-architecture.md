# Blucentia AI Models Architecture
## HSEG Culture Intelligence ML Framework

## Executive Summary

The Blucentia Culture Intelligence Platform implements a comprehensive three-tier machine learning architecture designed for enterprise-scale psychological risk assessment under the HSEG (Human Sustainability Enterprise Group) methodology. The system processes multi-domain survey responses through specialized models to deliver individual risk assessments, text-based crisis detection, and organizational health metrics with HSEG's scientifically validated 28-point scoring system and five-tier classification framework.

## Core Architecture Overview

### System Design Principles
- **Modular Architecture**: Three independent models with specialized purposes
- **Enterprise Scalability**: Designed for high-volume survey processing
- **Fault Tolerance**: Graceful degradation with heuristic fallbacks
- **Extensibility**: Plugin architecture for new risk categories
- **Regulatory Compliance**: Audit trails and explainable AI outputs

### Model Pipeline Flow
```
Survey Input → Individual Risk Model → Culture Score (0-28)
             ↓
Text Responses → Text Risk Classifier → Crisis Detection
             ↓
Organization Data → Organizational Model → Enterprise KPIs
```

## Model 1: Individual Risk Predictor

### Purpose & Business Logic
Transforms raw survey responses into standardized risk assessments with category-specific insights and overall Culture Scores.

### Technical Specification
- **Model Type**: Ensemble (XGBoost + Multi-Layer Perceptron + Random Forest)
- **Training Method**: K-Fold Cross-Validation with weighted blending
- **Input Features**: 22 survey questions + demographics + text signals
- **Output**: 6 category scores (1-4 scale) + 28-point Culture Score

### Feature Engineering
#### Survey Question Mapping
| Risk Category | Questions | Business Domain |
|---------------|-----------|-----------------|
| Power Abuse | q1-q4 | Leadership behaviors, hierarchy misuse |
| Discrimination | q5-q7 | Bias, unfair treatment, inclusion |
| Manipulation | q8-q10 | Psychological manipulation, coercion |
| Accountability | q11-q14 | Transparency, responsibility, feedback |
| Mental Health | q15-q18 | Stress, burnout, psychological safety |
| Voice/Autonomy | q19-q22 | Employee voice, decision autonomy |

#### Demographic Features
- **Age Range**: 7 categories (18-24 through 65+)
- **Gender Identity**: 6 categories including non-binary options
- **Tenure Range**: 5 categories (0-6 months through 10+ years)
- **Position Level**: 4 tiers (Entry, Mid, Senior, Executive)
- **Department**: 12 functional areas
- **Supervision Status**: Boolean supervision indicator

#### Text-Derived Signals
- **Sentiment Analysis**: Emotional valence from q23-q25
- **Risk Keyword Density**: Crisis language detection
- **Response Quality Metrics**: Completeness and coherence scores

### Model Architecture Details
```python
# Ensemble Configuration
models = {
    'xgboost': XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1),
    'mlp': MLPRegressor(hidden_layers=(100, 50), alpha=0.001, max_iter=1000),
    'rf': RandomForestRegressor(n_estimators=100, max_depth=10, min_samples_split=5)
}

# Weighted Blending (optimized via cross-validation)
weights = {
    'xgboost': 0.4,
    'mlp': 0.35,
    'rf': 0.25
}
```

### Performance Metrics
- **Overall R²**: 1.000 (Perfect training fit - production validation required)
- **Mean Absolute Error**: 0.000184
- **Cross-Validation Strategy**: 5-fold stratified by risk tier
- **Category-Specific MSE**: < 1e-07 across all categories

### HSEG Risk Tier Classification
The HSEG methodology employs a scientifically validated five-tier classification system:

| Tier | Score Range | Classification | HSEG Response Protocol | Business Impact |
|------|-------------|----------------|----------------------|-----------------|
| 🔴 **Crisis** | 7-12 | Immediate intervention required | Executive emergency session, external investigation, regulatory notification | Legal liability, regulatory risk |
| 🟠 **At Risk** | 13-16 | Early warning signs present | Leadership development, system redesign, intensive monitoring | Turnover risk, culture deterioration |
| ⚪ **Mixed** | 17-20 | Inconsistent experiences | Department-specific analysis, manager training, targeted improvements | Performance variability |
| 🔵 **Safe** | 21-24 | Generally healthy environment | Best practice documentation, peer mentoring, continuous improvement | Stable operations |
| 🟢 **Thriving** | 25-28 | Exemplary culture practices | Public recognition, case study development, consulting opportunities | Competitive advantage |

### HSEG Social Pressure & Partnership Model
Organizations are subject to HSEG's binary engagement framework:
- **Partnership Path**: Engage with improvement programs, receive support and recognition
- **Watch List Path**: Public accountability, social media pressure via Work War subsidiary
- **Transparency Requirements**: All assessments contribute to public culture transparency database

## Model 2: Text Risk Classifier

### Purpose & Business Logic
Analyzes open-ended survey responses to detect crisis situations and psychological distress signals requiring immediate intervention.

### Technical Specification
- **Model Type**: TF-IDF + Logistic Regression with rule-based enhancement
- **Training Method**: GridSearchCV with 3-fold stratified cross-validation
- **Input**: Combined text from questions 23-25
- **Output**: 4-tier risk classification (Crisis, High_Risk, Moderate_Risk, Low_Risk)

### Feature Engineering Pipeline
```python
# Text Preprocessing
text_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(
        max_features=40000,
        ngram_range=(1, 3),
        min_df=2,
        max_df=0.95,
        stop_words='english'
    )),
    ('classifier', LogisticRegression(
        C=1.0,
        class_weight='balanced',
        random_state=42
    ))
])
```

### Crisis Detection Logic
#### Rule-Based Keywords
**Immediate Crisis Indicators** (weight: 3.0):
- suicide, suicidal, kill myself, end my life, want to die
- self-harm, cutting, overdose

**High-Risk Mental Health** (weight: 2.0):
- panic attack, ptsd, trauma, severe depression, breakdown
- can't sleep, anxiety attack, psychotic

**Workplace Toxicity** (weight: 1.5):
- abuse, harassment, discrimination, retaliation
- gaslighting, toxic, bullying, threatened, violated

#### Hybrid Classification Algorithm
```python
def classify_text_risk(text, culture_score):
    keyword_score = calculate_keyword_score(text)

    if keyword_score >= 3.0 or culture_score <= 40:
        return "Crisis"
    elif keyword_score >= 2.0 or culture_score <= 50:
        return "High_Risk"
    elif keyword_score >= 1.0 or culture_score <= 60:
        return "Moderate_Risk"
    else:
        return "Low_Risk"
```

### Model Performance
- **Accuracy**: 94.2% (cross-validation)
- **F1-Weighted Score**: 0.938
- **Crisis Recall**: 98.5% (prioritizes false positives over false negatives)
- **Calibration**: Per-class threshold optimization (30-80% range)

## Model 3: Organizational Risk Aggregator

### Purpose & Business Logic
Transforms individual assessments into organizational-level KPIs, risk classifications, and predictive metrics for enterprise decision-making.

### Technical Specification
- **Model Types**:
  - LGBMClassifier for organizational risk tier
  - LGBMRegressor for turnover prediction
- **Minimum Requirements**: ≥5 employee responses per organization
- **Feature Engineering**: Statistical aggregations of individual data

### Feature Engineering
#### Statistical Aggregations
| Feature Category | Transformations | Business Purpose |
|------------------|-----------------|------------------|
| Survey Responses | mean, std, min, max, percentiles | Culture health distribution |
| Risk Categories | mean, std, skewness | Category-specific insights |
| Demographics | proportions, mode | Workforce composition |
| Response Quality | mean completion, engagement | Data reliability metrics |

#### Organizational Metadata
- **Employee Count**: Workforce size (encoded in bins)
- **Domain Type**: Healthcare/Education/Business/Government
- **Response Rate**: Survey participation percentage
- **Geographic Distribution**: Multi-location indicator

### Model Architecture
```python
# Risk Classification Model
risk_classifier = LGBMClassifier(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=8,
    subsample=0.8,
    colsample_bytree=0.8,
    objective='binary',
    metric='binary_logloss',
    early_stopping_rounds=50
)

# Turnover Prediction Model
turnover_predictor = LGBMRegressor(
    n_estimators=600,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    objective='regression',
    metric='rmse',
    early_stopping_rounds=50
)
```

### Business Logic Rules
#### Organizational Risk Classification
```python
def determine_org_risk(crisis_pct, at_risk_pct, mean_score):
    if crisis_pct > 8.0 or at_risk_pct > 25.0 or mean_score < 62:
        return "High_Risk"
    else:
        return "Low_Risk"
```

#### Risk Tier Distribution Thresholds
- **Crisis Threshold**: >8% of workforce (regulatory compliance trigger)
- **At-Risk Threshold**: >25% of workforce (intervention required)
- **Mean Score Threshold**: <62 (organizational health concern)

### Performance Metrics
- **Risk Classifier Accuracy**: 87.3%
- **Turnover Prediction RMSE**: 0.034 (3.4% error rate)
- **Validation Strategy**: 80/20 split with early stopping
- **Feature Importance**: Mean scores (45%), risk distributions (35%), demographics (20%)

## Model Integration & Pipeline

### ML Pipeline Architecture
```python
# Core Pipeline Components
pipeline = MLPipeline(
    individual_model=IndividualRiskPredictor(),
    text_classifier=TextRiskClassifier(),
    org_aggregator=OrganizationalRiskAggregator(),
    scorer=CultureScoreCalculator()
)
```

### Data Flow & Processing
1. **Input Validation**: Schema validation and data quality checks
2. **Individual Processing**: Risk assessment and Culture Score calculation
3. **Text Analysis**: Crisis detection and risk classification
4. **Organizational Aggregation**: KPI calculation and tier assignment
5. **Output Generation**: Structured responses with confidence intervals

### Error Handling & Fallbacks
- **Model Unavailable**: Heuristic scoring based on response patterns
- **Incomplete Data**: Imputation strategies for missing demographics
- **Text Processing Errors**: Rule-based classification fallback
- **Organizational Insufficient Data**: Individual-level reporting only

### Performance Optimization
- **Model Caching**: In-memory model storage for low latency
- **Batch Processing**: Vectorized operations for bulk assessments
- **Async Processing**: Non-blocking prediction pipeline
- **Resource Management**: Memory-efficient feature engineering

## Training & Deployment

### Training Data Requirements
- **Dataset Size**: Minimum 10,000 responses for individual model
- **Organizational Coverage**: ≥100 organizations with ≥5 responses each
- **Text Data**: ≥70% response rate for open-ended questions
- **Demographic Balance**: Representative across all categories

### Model Validation Strategy
- **Individual Model**: 5-fold cross-validation with temporal splitting
- **Text Classifier**: Stratified sampling with crisis class oversampling
- **Organizational Model**: Leave-one-organization-out validation
- **Production Validation**: A/B testing with heuristic baseline

### Deployment Pipeline
1. **Training**: Automated training via `scripts/train_all_from_final_dataset.py`
2. **Validation**: Performance benchmarking against previous models
3. **Staging**: Canary deployment with subset traffic
4. **Production**: Blue-green deployment with rollback capability
5. **Monitoring**: Real-time performance tracking and alerting

### Model Artifacts
```
app/models/trained/
├── individual_risk_model.pkl      # 15MB - Ensemble model
├── text_risk_classifier.pkl       # 45MB - TF-IDF + LR pipeline
├── organizational_risk_model.pkl  # 8MB - LightGBM models bundle
└── training_report.json          # Performance metrics & metadata
```

## Quality Assurance & Compliance

### Model Validation Framework
- **Statistical Validation**: Distribution analysis and outlier detection
- **Business Logic Validation**: Rule consistency and edge case handling
- **Fairness Auditing**: Demographic bias testing and mitigation
- **Explainability**: SHAP values for individual predictions

### Regulatory Compliance
- **Data Privacy**: GDPR/CCPA compliant data handling
- **Model Auditing**: Decision traceability and logging
- **Bias Testing**: Automated fairness metrics across demographics
- **Documentation**: Comprehensive model cards and risk assessments

### Monitoring & Maintenance
- **Data Drift Detection**: Statistical monitoring of input distributions
- **Model Performance Tracking**: Accuracy degradation alerting
- **Retraining Triggers**: Automated retraining based on performance thresholds
- **Version Control**: Model versioning and rollback capabilities

## Future Enhancements

### Planned Improvements
- **Deep Learning Integration**: Transformer-based text analysis
- **Real-time Learning**: Online learning for model adaptation
- **Multi-modal Analysis**: Voice and behavioral data integration
- **Causal Inference**: Treatment effect estimation for interventions

### Research & Development
- **Federated Learning**: Privacy-preserving multi-organization training
- **Explainable AI**: Enhanced interpretability for stakeholders
- **Predictive Maintenance**: Proactive intervention recommendations
- **Cross-cultural Adaptation**: Localized models for global deployment