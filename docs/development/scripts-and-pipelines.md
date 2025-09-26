# Scripts and ML Pipeline Documentation

## Overview

The Culture Score platform includes a comprehensive suite of Python scripts for data generation, model training, validation, and deployment automation. This documentation provides detailed information about each script, their dependencies, usage patterns, and integration with the ML pipeline.

## Script Categories

### 1. Model Training Scripts
| Script | Purpose | Input | Output |
|--------|---------|--------|--------|
| `train_all_from_final_dataset.py` | Unified training for all three models | `data/hseg_final_dataset.csv` | Trained model artifacts |
| `scripts/models/train_individual_model.py` | Individual risk model training | Survey data CSV | `individual_risk_model.pkl` |
| `scripts/models/train_text_classifier.py` | Text risk classifier training | Text responses | `text_risk_classifier.pkl` |
| `scripts/models/train_organizational_model.py` | Organizational model training | Aggregated org data | `organizational_risk_model.pkl` |

### 2. Data Generation Scripts
| Script | Purpose | Output Volume | Features |
|--------|---------|---------------|----------|
| `hseg_ultimate_generator.py` | Primary synthetic data generation | 50K+ responses | AI-powered narratives |
| `hseg_codex_cli_generator.py` | CLI-based data generation | Configurable | Interactive prompts |
| `expanded_companies_55.py` | Company profile definitions | 55 organizations | Realistic org structures |
| `dataset_validator.py` | Data quality validation | Validation reports | Statistical analysis |

### 3. AI Narrative Engines
| Script | Purpose | Technology | Use Case |
|--------|---------|------------|----------|
| `gen_ai_narrative_engine.py` | AI-powered text generation | GPT-based | Realistic survey responses |
| `ai_narrative_prompt_engine.py` | Advanced prompt engineering | Template system | Trauma-aware narratives |
| `local_narrative_engine.py` | Local text generation | Rule-based | Offline development |
| `codex_cli_narrative_engine.py` | CLI narrative interface | Interactive | Manual data creation |

### 4. Utility Scripts
| Script | Purpose | Usage | Dependencies |
|--------|---------|--------|-------------|
| `train.py` | Model training | Core ML training pipeline | Pandas, scikit-learn |
| `reorganize_repo.py` | Repository restructuring | Project maintenance | Git operations |
| `generate_50k_dataset.bat` | Batch data generation | Windows automation | Python scripts |
| `generate_codex_cli_dataset.bat` | CLI batch processing | Interactive generation | Multiple generators |

## Core Training Pipeline

### Unified Training Script
**File**: `scripts/train_all_from_final_dataset.py`

This is the primary training entry point that orchestrates the complete model training pipeline.

#### Architecture
```python
def main():
    """Main training pipeline orchestration"""

    # 1. Data Loading & Validation
    df = load_data(DATA_PATH)
    validate_data_quality(df)

    # 2. Individual Risk Model Training
    individual_model = train_individual_model(df)

    # 3. Text Risk Classifier Training
    text_classifier = train_text_classifier(df)

    # 4. Organizational Model Training
    org_model = train_organizational_model(df)

    # 5. Model Serialization
    save_models(individual_model, text_classifier, org_model)

    # 6. Performance Reporting
    generate_training_report()
```

#### Data Processing Pipeline
```python
def build_individual_training(df: pd.DataFrame) -> List[Dict]:
    """Transform raw survey data for individual model training"""

    # Category mapping for risk assessment
    categories = {
        1: ['q1', 'q2', 'q3', 'q4'],        # Power Abuse
        2: ['q5', 'q6', 'q7'],              # Discrimination
        3: ['q8', 'q9', 'q10'],             # Manipulation
        4: ['q11', 'q12', 'q13', 'q14'],    # Accountability
        5: ['q15', 'q16', 'q17', 'q18'],    # Mental Health
        6: ['q19', 'q20', 'q21', 'q22'],    # Voice/Autonomy
    }

    training_data = []

    for _, row in df.iterrows():
        # Calculate category averages
        category_scores = {}
        for cat_id, questions in categories.items():
            scores = [row.get(q, 2.5) for q in questions if pd.notna(row.get(q))]
            category_scores[f'category_{cat_id}'] = np.mean(scores) if scores else 2.5

        # Prepare training sample
        sample = {
            'features': extract_features(row),
            'targets': category_scores,
            'demographics': extract_demographics(row),
            'text_features': extract_text_features(row)
        }

        training_data.append(sample)

    return training_data
```

#### Feature Engineering
```python
def extract_features(row: pd.Series) -> Dict:
    """Extract and engineer features for model training"""

    features = {}

    # Survey response features
    for i in range(1, 23):
        features[f'q{i}'] = row.get(f'q{i}', 2.5)

    # Demographic encoding
    features.update(encode_demographics(row))

    # Response quality metrics
    features.update(calculate_response_quality(row))

    # Text-derived features
    features.update(extract_text_signals(row))

    return features

def encode_demographics(row: pd.Series) -> Dict:
    """Encode demographic variables for ML models"""

    # Age range encoding
    age_mapping = {
        '18-24': 1, '25-34': 2, '35-44': 3,
        '45-54': 4, '55-64': 5, '65+': 6
    }

    # Position level encoding
    position_mapping = {
        'Entry': 1, 'Mid': 2, 'Senior': 3, 'Executive': 4
    }

    return {
        'age_encoded': age_mapping.get(row.get('age_range'), 2),
        'position_encoded': position_mapping.get(row.get('position_level'), 2),
        'supervises_others': 1 if row.get('supervises_others') else 0,
        # Additional demographic encodings...
    }
```

#### Model Training Functions
```python
def train_individual_model(df: pd.DataFrame) -> IndividualRiskPredictor:
    """Train the individual risk prediction ensemble model"""

    # Prepare training data
    training_data = build_individual_training(df)
    X, y = prepare_features_targets(training_data)

    # Initialize and train ensemble
    model = IndividualRiskPredictor()
    model.fit(X, y)

    # Cross-validation evaluation
    cv_scores = cross_validate_model(model, X, y)
    logger.info(f"Individual model CV scores: {cv_scores}")

    return model

def train_text_classifier(df: pd.DataFrame) -> Pipeline:
    """Train the text risk classification pipeline"""

    # Prepare text data
    texts, labels = prepare_text_data(df)

    # Grid search for optimal hyperparameters
    param_grid = {
        'tfidf__max_features': [20000, 40000],
        'tfidf__ngram_range': [(1, 2), (1, 3)],
        'tfidf__min_df': [2, 5],
        'tfidf__max_df': [0.9, 0.95],
        'classifier__C': [0.5, 1.0, 2.0]
    }

    # Create pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english')),
        ('classifier', LogisticRegression(class_weight='balanced'))
    ])

    # Grid search with cross-validation
    grid_search = GridSearchCV(
        pipeline, param_grid,
        cv=3, scoring='f1_weighted',
        n_jobs=-1, verbose=1
    )

    grid_search.fit(texts, labels)

    logger.info(f"Best text classifier params: {grid_search.best_params_}")
    logger.info(f"Best CV score: {grid_search.best_score_:.4f}")

    return grid_search.best_estimator_

def train_organizational_model(df: pd.DataFrame) -> Dict:
    """Train organizational risk and turnover prediction models"""

    # Aggregate data by organization
    org_data = aggregate_organizational_data(df)

    # Prepare features and targets
    X, y_risk, y_turnover = prepare_org_features(org_data)

    # Train risk classifier
    risk_classifier = lgb.LGBMClassifier(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=8,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='binary',
        metric='binary_logloss',
        random_state=42
    )

    # Train turnover predictor
    turnover_predictor = lgb.LGBMRegressor(
        n_estimators=600,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='regression',
        metric='rmse',
        random_state=42
    )

    # Train with early stopping
    X_train, X_val, y_risk_train, y_risk_val, y_turn_train, y_turn_val = train_test_split(
        X, y_risk, y_turnover, test_size=0.2, random_state=42, stratify=y_risk
    )

    risk_classifier.fit(
        X_train, y_risk_train,
        eval_set=[(X_val, y_risk_val)],
        early_stopping_rounds=50,
        verbose=False
    )

    turnover_predictor.fit(
        X_train, y_turn_train,
        eval_set=[(X_val, y_turn_val)],
        early_stopping_rounds=50,
        verbose=False
    )

    return {
        'risk_classifier': risk_classifier,
        'turnover_predictor': turnover_predictor,
        'feature_names': list(X.columns),
        'encoders': prepare_encoders(org_data)
    }
```

#### Usage Example
```bash
# Full pipeline training
python scripts/train_all_from_final_dataset.py

# Expected output structure:
# app/models/trained/
# ├── individual_risk_model.pkl      (15MB)
# ├── text_risk_classifier.pkl       (45MB)
# ├── organizational_risk_model.pkl  (8MB)
# └── training_report.json          (Performance metrics)

# Training logs show:
# [INFO] Loading data from data/hseg_final_dataset.csv
# [INFO] Data shape: (50847, 45)
# [INFO] Training individual risk model...
# [INFO] Individual model CV scores: {'mae': 0.000184, 'r2': 1.000}
# [INFO] Training text risk classifier...
# [INFO] Best CV score: 0.9380
# [INFO] Training organizational models...
# [INFO] Risk classifier accuracy: 87.3%
# [INFO] Turnover predictor RMSE: 0.034
# [INFO] All models saved successfully
```

## Data Generation Pipeline

### Primary Data Generator
**File**: `scripts/hseg_ultimate_generator.py`

Advanced synthetic data generation with AI-powered narrative creation for realistic survey responses.

#### Key Features
- **Realistic Organizations**: 55 predefined company profiles with authentic characteristics
- **AI-Powered Narratives**: GPT-based text generation for trauma-aware responses
- **Statistical Distribution**: Maintains proper demographic and response distributions
- **Scalable Output**: Generates 50K+ responses with configurable parameters

#### Architecture
```python
@dataclass
class SyntheticEmployee:
    """Synthetic employee profile for data generation"""
    employee_id: str
    organization: Dict
    demographics: Dict
    psychological_profile: Dict
    response_patterns: Dict
    trauma_indicators: List[str]

class HSEGUltimateGenerator:
    """Main data generation orchestrator"""

    def __init__(self, config: Dict):
        self.config = config
        self.narrative_engine = GenerativeAINarrativeEngine()
        self.companies = EXPANDED_COMPANIES

    def generate_dataset(self, target_responses: int) -> pd.DataFrame:
        """Generate complete synthetic dataset"""

        # Initialize generation context
        generation_context = self.setup_generation_context()

        # Generate employee profiles
        employees = self.generate_employee_profiles(target_responses)

        # Generate survey responses
        responses = []
        for employee in employees:
            response = self.generate_employee_response(employee)
            responses.append(response)

        return pd.DataFrame(responses)

    def generate_employee_response(self, employee: SyntheticEmployee) -> Dict:
        """Generate complete survey response for employee"""

        # Generate survey question responses
        survey_responses = self.generate_survey_responses(employee)

        # Generate text responses with AI
        text_responses = self.generate_text_responses(employee)

        # Compile complete response
        return {
            'response_id': employee.employee_id,
            'organization_name': employee.organization['name'],
            'domain': employee.organization['domain'],
            **survey_responses,
            **text_responses,
            **employee.demographics,
            'response_timestamp': datetime.now().isoformat()
        }
```

#### Psychological Profiling
```python
def generate_psychological_profile(self, demographics: Dict) -> Dict:
    """Generate psychological profile affecting survey responses"""

    # Base psychological traits
    traits = {
        'neuroticism': np.random.normal(0.5, 0.2),
        'extraversion': np.random.normal(0.5, 0.2),
        'openness': np.random.normal(0.5, 0.2),
        'agreeableness': np.random.normal(0.5, 0.2),
        'conscientiousness': np.random.normal(0.5, 0.2)
    }

    # Demographic influences on traits
    if demographics.get('position_level') == 'Executive':
        traits['extraversion'] += 0.1
        traits['conscientiousness'] += 0.15

    if demographics.get('age_range') in ['18-24', '25-34']:
        traits['neuroticism'] += 0.05

    # Risk factors
    risk_factors = self.calculate_risk_factors(traits, demographics)

    return {
        'personality_traits': traits,
        'risk_factors': risk_factors,
        'stress_level': self.calculate_stress_level(traits),
        'resilience_score': self.calculate_resilience(traits)
    }

def generate_survey_responses(self, employee: SyntheticEmployee) -> Dict:
    """Generate 22 survey question responses based on profile"""

    responses = {}
    psychological_profile = employee.psychological_profile

    # Question-specific response generation
    for q_num in range(1, 23):
        base_response = self.get_base_response(q_num, psychological_profile)

        # Add noise and individual variation
        response = self.add_response_variation(
            base_response,
            employee.response_patterns,
            psychological_profile
        )

        # Ensure valid range [1, 4]
        responses[f'q{q_num}'] = np.clip(response, 1, 4)

    return responses
```

#### AI-Powered Text Generation
```python
class GenerativeAINarrativeEngine:
    """AI-powered narrative generation for survey text responses"""

    def __init__(self):
        self.trauma_contexts = self.load_trauma_contexts()
        self.prompt_templates = self.load_prompt_templates()

    def generate_text_response(self, question: str, employee: SyntheticEmployee) -> str:
        """Generate contextually appropriate text response"""

        # Select appropriate trauma context
        trauma_context = self.select_trauma_context(
            employee.psychological_profile,
            employee.trauma_indicators
        )

        # Build prompt with context
        prompt = self.build_contextual_prompt(
            question, employee, trauma_context
        )

        # Generate response with AI
        response = self.generate_with_ai(prompt)

        # Post-process for appropriateness
        return self.filter_and_validate_response(response, trauma_context)

    def build_contextual_prompt(self, question: str, employee: SyntheticEmployee,
                              trauma_context: TraumaContext) -> str:
        """Build contextually rich prompt for AI generation"""

        template = self.prompt_templates[trauma_context.category]

        context_vars = {
            'organization_type': employee.organization['domain'],
            'position_level': employee.demographics['position_level'],
            'department': employee.demographics['department'],
            'stress_level': employee.psychological_profile['stress_level'],
            'trauma_indicators': ', '.join(employee.trauma_indicators),
            'question': question
        }

        return template.format(**context_vars)

# Example trauma-aware prompt templates
PROMPT_TEMPLATES = {
    'workplace_harassment': """
    You are a {position_level} employee in {department} at a {organization_type} organization.
    Your stress level is {stress_level}/10. You have experienced: {trauma_indicators}.

    Respond to this workplace survey question in 2-3 sentences, reflecting your experience:
    "{question}"

    Be authentic but professional. Show subtle signs of the workplace issues you've faced.
    """,

    'burnout_mental_health': """
    You work as {position_level} in {department}. Your current stress level is {stress_level}/10.
    You've been dealing with: {trauma_indicators}.

    Answer this survey question honestly, showing signs of burnout/mental health struggles:
    "{question}"

    Express fatigue, overwhelm, or mental health impacts subtly but clearly.
    """,

    'discrimination_bias': """
    As a {position_level} in {department}, you've experienced: {trauma_indicators}.
    Your stress about workplace fairness is {stress_level}/10.

    Respond to this question, hinting at discrimination/bias experiences:
    "{question}"

    Show awareness of unfair treatment while maintaining professional tone.
    """
}
```

#### Usage Examples
```bash
# Generate 50K response dataset
python scripts/hseg_ultimate_generator.py --responses 50000 --output data/generated_dataset.csv

# Generate with specific company focus
python scripts/hseg_ultimate_generator.py --companies "TechCorp,HealthSystem" --responses 10000

# Interactive CLI generation
python scripts/hseg_codex_cli_generator.py

# Batch generation (Windows)
generate_50k_dataset.bat
```

## Data Validation Pipeline

### Dataset Validator
**File**: `scripts/dataset_validator.py`

Comprehensive data quality validation for generated and real datasets.

#### Validation Categories
```python
class DatasetValidator:
    """Comprehensive dataset validation and quality assessment"""

    def validate_dataset(self, df: pd.DataFrame) -> ValidationReport:
        """Run complete validation pipeline"""

        report = ValidationReport()

        # 1. Schema Validation
        report.schema_validation = self.validate_schema(df)

        # 2. Data Quality Checks
        report.quality_checks = self.validate_data_quality(df)

        # 3. Statistical Validation
        report.statistical_validation = self.validate_distributions(df)

        # 4. Business Logic Validation
        report.business_validation = self.validate_business_rules(df)

        # 5. AI Detection (for synthetic data)
        report.ai_detection = self.detect_ai_patterns(df)

        return report

    def validate_schema(self, df: pd.DataFrame) -> Dict:
        """Validate dataset schema and required columns"""

        required_columns = {
            'survey_questions': [f'q{i}' for i in range(1, 23)],
            'text_responses': ['q23', 'q24', 'q25'],
            'demographics': [
                'age_range', 'gender_identity', 'tenure_range',
                'position_level', 'department', 'supervises_others'
            ],
            'metadata': [
                'response_id', 'organization_name', 'domain',
                'response_timestamp'
            ]
        }

        validation_results = {}

        for category, columns in required_columns.items():
            missing_columns = [col for col in columns if col not in df.columns]
            validation_results[category] = {
                'required': len(columns),
                'present': len(columns) - len(missing_columns),
                'missing': missing_columns,
                'coverage': (len(columns) - len(missing_columns)) / len(columns)
            }

        return validation_results

    def validate_data_quality(self, df: pd.DataFrame) -> Dict:
        """Validate data quality metrics"""

        quality_metrics = {}

        # Survey response quality
        survey_cols = [f'q{i}' for i in range(1, 23)]
        quality_metrics['survey_responses'] = {
            'completeness': df[survey_cols].notna().mean().mean(),
            'valid_range': ((df[survey_cols] >= 1) & (df[survey_cols] <= 4)).mean().mean(),
            'response_variance': df[survey_cols].var().mean(),
            'extreme_responses': (
                (df[survey_cols] == 1).sum().sum() +
                (df[survey_cols] == 4).sum().sum()
            ) / (len(df) * len(survey_cols))
        }

        # Text response quality
        text_cols = ['q23', 'q24', 'q25']
        text_lengths = df[text_cols].fillna('').applymap(len)
        quality_metrics['text_responses'] = {
            'completeness': df[text_cols].notna().mean().mean(),
            'avg_length': text_lengths.mean().mean(),
            'min_length': text_lengths.min().min(),
            'max_length': text_lengths.max().max(),
            'empty_responses': (text_lengths == 0).sum().sum()
        }

        # Demographic completeness
        demo_cols = ['age_range', 'gender_identity', 'department']
        quality_metrics['demographics'] = {
            'completeness': df[demo_cols].notna().mean().mean(),
            'unique_combinations': len(df[demo_cols].drop_duplicates()),
            'diversity_index': self.calculate_diversity_index(df[demo_cols])
        }

        return quality_metrics

    def validate_distributions(self, df: pd.DataFrame) -> Dict:
        """Validate statistical distributions match expected patterns"""

        # Expected distributions based on research
        expected_distributions = {
            'age_range': {
                '18-24': 0.15, '25-34': 0.30, '35-44': 0.25,
                '45-54': 0.20, '55-64': 0.08, '65+': 0.02
            },
            'position_level': {
                'Entry': 0.35, 'Mid': 0.40, 'Senior': 0.20, 'Executive': 0.05
            },
            'domain': {
                'Business': 0.45, 'Healthcare': 0.25,
                'Education': 0.20, 'Government': 0.10
            }
        }

        distribution_analysis = {}

        for column, expected in expected_distributions.items():
            if column in df.columns:
                observed = df[column].value_counts(normalize=True).to_dict()

                # Calculate distribution similarity (KL divergence)
                kl_divergence = self.calculate_kl_divergence(expected, observed)

                distribution_analysis[column] = {
                    'expected': expected,
                    'observed': observed,
                    'kl_divergence': kl_divergence,
                    'similarity_score': 1 / (1 + kl_divergence)
                }

        return distribution_analysis
```

#### Usage Example
```python
# Validate generated dataset
validator = DatasetValidator()
df = pd.read_csv('data/generated_dataset.csv')

validation_report = validator.validate_dataset(df)

print(f"Schema Coverage: {validation_report.schema_validation}")
print(f"Data Quality Score: {validation_report.quality_score:.3f}")
print(f"Distribution Similarity: {validation_report.distribution_similarity:.3f}")

# Generate validation report
validator.generate_report(validation_report, 'validation_report.html')
```

## Deployment Pipeline Scripts

### Model Deployment Automation
```python
#!/usr/bin/env python3
"""
Production model deployment pipeline
Handles model validation, versioning, and deployment
"""

import os
import json
import pickle
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class ModelDeploymentPipeline:
    """Automated model deployment and versioning pipeline"""

    def __init__(self, config_path: str = 'deployment_config.json'):
        self.config = self.load_config(config_path)
        self.models_dir = Path('app/models/trained')
        self.versions_dir = Path('app/models/versions')
        self.staging_dir = Path('app/models/staging')

    def deploy_models(self, version: str = None) -> Dict:
        """Deploy trained models to production"""

        deployment_id = version or f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 1. Validate models
        validation_results = self.validate_models()
        if not validation_results['all_valid']:
            raise ValueError(f"Model validation failed: {validation_results['errors']}")

        # 2. Create version backup
        self.create_version_backup(deployment_id)

        # 3. Performance benchmark
        benchmark_results = self.benchmark_models()

        # 4. Deploy to staging
        staging_results = self.deploy_to_staging(deployment_id)

        # 5. Run integration tests
        test_results = self.run_integration_tests()

        # 6. Deploy to production (if tests pass)
        if test_results['all_passed']:
            production_results = self.deploy_to_production(deployment_id)
        else:
            raise ValueError(f"Integration tests failed: {test_results['failures']}")

        # 7. Update deployment metadata
        deployment_metadata = {
            'deployment_id': deployment_id,
            'timestamp': datetime.now().isoformat(),
            'validation_results': validation_results,
            'benchmark_results': benchmark_results,
            'test_results': test_results,
            'status': 'deployed'
        }

        self.save_deployment_metadata(deployment_metadata)

        return deployment_metadata

    def validate_models(self) -> Dict:
        """Validate all trained models before deployment"""

        required_models = [
            'individual_risk_model.pkl',
            'text_risk_classifier.pkl',
            'organizational_risk_model.pkl'
        ]

        validation_results = {
            'all_valid': True,
            'models': {},
            'errors': []
        }

        for model_file in required_models:
            model_path = self.models_dir / model_file

            if not model_path.exists():
                validation_results['all_valid'] = False
                validation_results['errors'].append(f"Missing model: {model_file}")
                continue

            try:
                # Load and validate model
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)

                # Model-specific validation
                if 'individual' in model_file:
                    model_validation = self.validate_individual_model(model)
                elif 'text' in model_file:
                    model_validation = self.validate_text_model(model)
                elif 'organizational' in model_file:
                    model_validation = self.validate_org_model(model)

                validation_results['models'][model_file] = model_validation

                if not model_validation['valid']:
                    validation_results['all_valid'] = False
                    validation_results['errors'].extend(model_validation['errors'])

            except Exception as e:
                validation_results['all_valid'] = False
                validation_results['errors'].append(f"Failed to load {model_file}: {str(e)}")

        return validation_results

    def benchmark_models(self) -> Dict:
        """Benchmark model performance against test dataset"""

        # Load test dataset
        test_data = self.load_test_dataset()

        benchmark_results = {}

        # Individual model benchmarking
        individual_metrics = self.benchmark_individual_model(test_data)
        benchmark_results['individual_model'] = individual_metrics

        # Text classifier benchmarking
        text_metrics = self.benchmark_text_classifier(test_data)
        benchmark_results['text_classifier'] = text_metrics

        # Organizational model benchmarking
        org_metrics = self.benchmark_organizational_model(test_data)
        benchmark_results['organizational_model'] = org_metrics

        # Overall performance score
        benchmark_results['overall_score'] = self.calculate_overall_score(
            individual_metrics, text_metrics, org_metrics
        )

        return benchmark_results

# Usage example
if __name__ == "__main__":
    pipeline = ModelDeploymentPipeline()

    try:
        deployment_results = pipeline.deploy_models()
        print(f"✅ Deployment successful: {deployment_results['deployment_id']}")
        print(f"Overall performance score: {deployment_results['benchmark_results']['overall_score']:.3f}")
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        # Rollback to previous version
        pipeline.rollback_deployment()
```

## Script Usage Guidelines

### Development Workflow
```bash
# 1. Data Generation
python scripts/hseg_ultimate_generator.py --responses 50000

# 2. Data Validation
python scripts/dataset_validator.py --input data/generated_dataset.csv --output validation_report.html

# 3. Model Training
python scripts/train_all_from_final_dataset.py

# 4. Model Validation
python scripts/validate_trained_models.py

# 5. Deployment (Staging)
python scripts/deploy_models.py --environment staging

# 6. Integration Testing
python scripts/run_integration_tests.py

# 7. Production Deployment
python scripts/deploy_models.py --environment production
```

### Environment Configuration
```bash
# Development Environment
export ENVIRONMENT=development
export DATA_PATH=data/dev_dataset.csv
export MODEL_PATH=app/models/dev/

# Staging Environment
export ENVIRONMENT=staging
export DATA_PATH=data/staging_dataset.csv
export MODEL_PATH=app/models/staging/

# Production Environment
export ENVIRONMENT=production
export DATA_PATH=data/production_dataset.csv
export MODEL_PATH=app/models/production/
```

### Monitoring and Logging
```python
# Script execution monitoring
import logging
import time
from functools import wraps

def monitor_execution(func):
    """Decorator to monitor script execution"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"Starting {func.__name__}")

        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"✅ {func.__name__} completed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ {func.__name__} failed after {execution_time:.2f}s: {str(e)}")
            raise

    return wrapper

# Usage
@monitor_execution
def train_models():
    """Monitored model training function"""
    # Training logic here
    pass
```

## Best Practices

### Error Handling
- **Comprehensive Logging**: All scripts include detailed logging with levels (INFO, WARNING, ERROR)
- **Graceful Failures**: Scripts handle errors gracefully and provide meaningful error messages
- **Resource Cleanup**: Proper cleanup of temporary files and memory usage
- **Retry Mechanisms**: Automatic retry for transient failures (network, file I/O)

### Performance Optimization
- **Memory Management**: Large datasets processed in chunks to prevent memory overflow
- **Parallel Processing**: Multi-processing for CPU-intensive operations
- **Progress Tracking**: Progress bars for long-running operations
- **Resource Monitoring**: Memory and CPU usage monitoring with warnings

### Security Considerations
- **Input Validation**: All user inputs validated and sanitized
- **File System Security**: Proper file permissions and path validation
- **Credential Management**: No hardcoded credentials; use environment variables
- **Data Anonymization**: PII removal in synthetic data generation

This comprehensive script documentation provides the foundation for maintaining, extending, and troubleshooting the Culture Score platform's data and model pipeline infrastructure.