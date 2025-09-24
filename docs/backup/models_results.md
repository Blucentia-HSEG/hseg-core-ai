# HSEG Model Training Results

Date: 2025-09-24T12:46:15

## Individual Model (Category Regression)
- Overall R2: 1
- Overall MAE: 0.000184
- Per-Category (MSE, R2, MAE):
  - Category 1: MSE=4.03E-08 R2=1 MAE=0.000155
  - Category 2: MSE=9.59E-08 R2=1 MAE=0.000245
  - Category 3: MSE=6.55E-08 R2=1 MAE=0.000199
  - Category 4: MSE=4.1E-08 R2=1 MAE=0.000161
  - Category 5: MSE=4.67E-08 R2=1 MAE=0.000163
  - Category 6: MSE=5.41E-08 R2=1 MAE=0.000183

## Text Risk Classifier
- Accuracy: 0.959031

## Organizational Models
- Risk Classification Accuracy: 1
- Turnover RMSE: 0.020607

### Notes
- Individual model uses K-Fold weighted ensembling (XGB/MLP/RF) aligned to HSEG 28-point scoring.
- Text model uses TF-IDF + LogisticRegression with GridSearchCV and calibrated thresholds.
- Organizational model uses LightGBM (if present), with fallback heuristics in the aggregator.
- Metrics reflect training/validation on data/hseg_final_dataset.csv.
