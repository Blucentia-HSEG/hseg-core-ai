# HSEG Model Suite

This repository contains three core ML components used by the HSEG platform.

## Models Overview

### IndividualRiskPredictor (`app/models/individual_risk_model.py`)
- **Purpose**: Predicts six category scores (1–4) and a 28‑point overall HSEG score with a five‑tier classification
- **Features**:
  - 22 survey items (q1-q22) mapped to 6 risk categories
  - Demographics (age_range, gender_identity, tenure_range, position_level, department, supervises_others)
  - Text-derived signals from open-ended responses (q23-q25)
  - Response quality metrics
- **Architecture**: Ensemble (XGBoost + MLP + RandomForest) with K‑Fold weighted blending and 28‑point normalization per HSEG documentation
- **Risk Categories**:
  1. Category 1: q1-q4
  2. Category 2: q5-q7
  3. Category 3: q8-q10
  4. Category 4: q11-q14
  5. Category 5: q15-q18
  6. Category 6: q19-q22

### TextRiskClassifier (`app/models/text_risk_classifier.py`)
- **Purpose**: Detects risk signals in open‑ended responses with four-tier classification
- **Classes**: Crisis, High_Risk, Moderate_Risk, Low_Risk
- **Features**: Combined text from survey questions q23, q24, q25
- **Architecture**: TF-IDF + LogisticRegression pipeline with GridSearchCV optimization
- **Crisis Detection**: Rule-based keyword matching combined with HSEG score thresholds
- **Crisis Keywords**: suicide, suicidal, kill myself, end my life, want to die, panic attack, ptsd, trauma, can't sleep, anxiety attack, severe depression, breakdown, self-harm, abuse, harassment, discrimination, retaliation, gaslighting, toxic, bullying, threatened, violated, destroyed
- **Classification Logic**:
  - Crisis: ≥3 crisis keywords OR HSEG score ≤40
  - High_Risk: ≥2 crisis keywords OR HSEG score ≤50
  - Moderate_Risk: ≥1 crisis keyword OR HSEG score ≤60
  - Low_Risk: Otherwise

### OrganizationalRiskAggregator (`app/models/organizational_risk_model.py`)
- **Purpose**: Aggregates individual predictions to organizational KPIs and tier classification
- **Models**:
  - LGBMClassifier for organizational risk tier (High_Risk/Low_Risk)
  - LGBMRegressor for turnover prediction
- **Features**:
  - Statistical aggregations (mean, std) of all survey responses by organization
  - Employee count, total responses, domain encoding
  - Risk tier percentages (crisis, at_risk, safe, thriving)
  - Mean and standard deviation of HSEG scores
- **Risk Tiers**:
  - Crisis: HSEG score ≤44
  - At_Risk: HSEG score ≤55
  - Mixed: HSEG score ≤66
  - Safe: HSEG score ≤77
  - Thriving: HSEG score >77
- **Organizational Risk Logic**: High_Risk if crisis >8% OR at_risk >25% OR mean_score <62

## Training

### Unified Training
Use the unified trainer to build all artifacts from `data/hseg_final_dataset.csv`:

```bash
python scripts/train_all_from_final_dataset.py
```

**Output artifacts** (saved to `app/models/trained/`):
- `individual_risk_model.pkl` - IndividualRiskPredictor ensemble model
- `text_risk_classifier.pkl` - TF-IDF + LogisticRegression pipeline with thresholds
- `organizational_risk_model.pkl` - LightGBM models bundle with encoders
- `training_report.json` - Performance metrics summary

### Individual Component Training
Train components separately:
```bash
python scripts/models/train_individual_model.py    # Individual risk predictor
python scripts/models/train_text_classifier.py     # Text risk classifier
python scripts/models/train_organizational_model.py # Organizational models
```

### Data Requirements
- **Input**: `data/hseg_final_dataset.csv`
- **Required columns**:
  - Survey responses: q1-q22 (numeric, 1-4 scale)
  - Text responses: q23, q24, q25 (optional open-ended)
  - Demographics: age_range, gender_identity, tenure_range, position_level, department, supervises_others
  - Organization: organization_name, domain, employee_count (for org model)
- **Missing data handling**: Survey questions filled with 2.5 if missing; skip rows with >4 missing responses

## Model Training Details

### Individual Risk Model
- **Data preprocessing**:
  - Maps q1-q22 to 6 risk categories, calculates category averages (1-4 scale)
  - Processes demographics with default fallbacks
  - Combines text responses for feature extraction
- **Training approach**: Ensemble with cross-validation blending
- **Output**: Trained IndividualRiskPredictor saved as pickle

### Text Risk Classifier
- **Preprocessing**:
  - Combines q23+q24+q25, normalizes text (lowercase, regex cleaning)
  - Creates crisis labels based on keyword count + HSEG score
- **GridSearch parameters**:
  - `max_features`: [20000, 40000]
  - `ngram_range`: [(1,2), (1,3)]
  - `min_df`: [2, 5], `max_df`: [0.9, 0.95]
  - `C`: [0.5, 1.0, 2.0]
- **Validation**: 3-fold stratified CV with F1-weighted scoring
- **Calibration**: Per-class threshold optimization (30-80% range)

### Organizational Models
- **Requirements**: ≥5 responses per organization
- **Feature engineering**:
  - Statistical aggregations (mean/std) of all survey responses
  - Risk tier percentages, domain encoding
  - Total responses, employee count
- **Models**:
  - **Risk classifier**: LGBMClassifier (500 estimators, 0.05 learning rate)
  - **Turnover predictor**: LGBMRegressor (600 estimators, 0.05 learning rate)
- **Training**: Early stopping with validation set, 50-round patience

## Performance Metrics

### Training Output
All models generate performance metrics during training:
- **Individual Model**: Ensemble metrics from cross-validation
- **Text Classifier**: Accuracy, F1-weighted score, classification report
- **Organizational Models**:
  - Risk classifier accuracy
  - Turnover prediction RMSE
- **Training Report**: JSON summary saved to `app/models/trained/training_report.json`

### Model Validation
- **Text Model**: 80/20 train/test split with stratified sampling
- **Organizational Models**: 80/20 split with early stopping validation
- **Individual Model**: K-fold cross-validation within ensemble training

## Integration

### Backend Integration
- **Model Loading**: `.pkl` models loaded on FastAPI startup
- **Text Model**: Supports both `.pkl` pipeline and rule-based fallback
- **Error Handling**: Graceful fallback to heuristics if models unavailable
- **API Endpoints**: Individual and organizational prediction endpoints

### Frontend Integration
- **Survey Playground**: Individual predictions with risk visualization and executive narrative
- **JSON Tool**: Individual and organizational summaries with stakeholder-friendly outputs
- **Real-time Processing**: Live prediction updates during survey completion

### Model Artifacts Structure
```
app/models/trained/
├── individual_risk_model.pkl      # IndividualRiskPredictor ensemble
├── text_risk_classifier.pkl       # TF-IDF + LogisticRegression + thresholds
├── organizational_risk_model.pkl  # LightGBM models + encoders + features
└── training_report.json          # Performance metrics summary
```

## Scoring Methodology
- **Centralized Scoring**: `app/core/scoring.py` implements HSEG scoring standards
- **Normalization**: 28-point scale with tier classifications
- **Weights**: Per HSEG_Comprehensive_Scoring_Documentation
- **Tier Mapping**:
  - Crisis (0-44), At Risk (45-55), Mixed (56-66), Safe (67-77), Thriving (78-84)
