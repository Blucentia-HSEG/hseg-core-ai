# HSEG Model Training Results

Last Updated: 2025-09-24T12:46:15

## Training Overview

This document contains the latest performance metrics from training all HSEG models using the unified training script (`scripts/train_all_from_final_dataset.py`) on the final dataset.

**Training Command**: `python scripts/train_all_from_final_dataset.py`

**Data Source**: `data/hseg_final_dataset.csv`

**Model Artifacts Generated**:
- `app/models/trained/individual_risk_model.pkl`
- `app/models/trained/text_risk_classifier.pkl`
- `app/models/trained/organizational_risk_model.pkl`
- `app/models/trained/training_report.json`

---

## Individual Risk Model (Category Regression)

**Architecture**: Ensemble (XGBoost + MLP + RandomForest) with K-Fold weighted blending

**Target**: 6 risk categories (1-4 scale) mapped from survey questions q1-q22
- Category 1 (Power Abuse): q1-q4
- Category 2 (Discrimination): q5-q7
- Category 3 (Manipulation): q8-q10
- Category 4 (Accountability): q11-q14
- Category 5 (Mental Health): q15-q18
- Category 6 (Voice/Autonomy): q19-q22

### Performance Metrics
- **Overall R²**: 1.000 (Perfect fit on training data)
- **Overall MAE**: 0.000184 (Mean Absolute Error)

### Per-Category Performance (MSE, R², MAE):
- **Category 1**: MSE=4.03E-08, R²=1.000, MAE=0.000155
- **Category 2**: MSE=9.59E-08, R²=1.000, MAE=0.000245
- **Category 3**: MSE=6.55E-08, R²=1.000, MAE=0.000199
- **Category 4**: MSE=4.1E-08, R²=1.000, MAE=0.000161
- **Category 5**: MSE=4.67E-08, R²=1.000, MAE=0.000163
- **Category 6**: MSE=5.41E-08, R²=1.000, MAE=0.000183

---

## Text Risk Classifier

**Architecture**: TF-IDF + LogisticRegression with GridSearchCV optimization

**Target Classes**: Crisis, High_Risk, Moderate_Risk, Low_Risk

**Features**: Combined text from q23, q24, q25 with preprocessing and crisis keyword detection

**Classification Logic**:
- Crisis: ≥3 crisis keywords OR HSEG score ≤40
- High_Risk: ≥2 crisis keywords OR HSEG score ≤50
- Moderate_Risk: ≥1 crisis keyword OR HSEG score ≤60
- Low_Risk: Otherwise

### Performance Metrics
- **Test Accuracy**: 95.90% (0.959031)
- **Validation**: 3-fold stratified cross-validation
- **Scoring**: F1-weighted optimization
- **Calibration**: Per-class threshold optimization (30-80% range)

### GridSearch Best Parameters
Optimized across TF-IDF parameters (max_features, ngram_range, min/max_df) and LogisticRegression regularization.

---

## Organizational Risk Models

**Architecture**: LightGBM Classifier + LightGBM Regressor

**Requirements**: Minimum 5 responses per organization

**Features**:
- Statistical aggregations (mean, std) of all survey responses
- Risk tier percentages, domain encoding
- Employee count, total responses

### Performance Metrics
- **Risk Classification Accuracy**: 100.0% (1.000)
- **Turnover Prediction RMSE**: 0.020607

### Model Configuration
- **Risk Classifier**: LGBMClassifier (500 estimators, 0.05 learning rate)
- **Turnover Predictor**: LGBMRegressor (600 estimators, 0.05 learning rate)
- **Training**: Early stopping with 50-round patience
- **Validation**: 80/20 train/test split

---

## Training Environment

### Data Processing
- **Missing Data Handling**: Survey questions filled with 2.5 if missing
- **Data Filtering**: Skip rows with >4 missing responses
- **Text Preprocessing**: Lowercase, regex cleaning, whitespace normalization
- **Feature Engineering**: Demographic encoding, risk tier calculations

### Model Validation
- **Individual Model**: K-fold cross-validation within ensemble training
- **Text Model**: Stratified 80/20 train/test split
- **Organizational Models**: 80/20 split with early stopping validation

### Notes
- Perfect scores (R²=1.0, Accuracy=100%) may indicate potential overfitting on training data
- Consider evaluating on held-out test set for production validation
- Models trained on synthetic data from `hseg_final_dataset.csv`
- Performance metrics reflect training/validation performance, not generalization to new data

### Recommendations
1. **Cross-validation**: Implement proper cross-validation for individual model generalization assessment
2. **Regularization**: Consider stronger regularization if overfitting is confirmed on test data
3. **Feature Engineering**: Explore additional text features for improved text classifier robustness
4. **Organizational Data**: Collect more organizational samples to improve generalization

For detailed model architecture and implementation details, see `docs/models.md`.
