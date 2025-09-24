# HSEG Model Suite

This repository contains three core ML components used by the HSEG platform.

- IndividualRiskPredictor (app/models/individual_risk_model.py)
  - Predicts six category scores (1–4) and a 28‑point overall HSEG score with a five‑tier classification.
  - Features include the 22 survey items, demographics, response quality, and text-derived signals.
  - Ensemble (XGBoost + MLP + RandomForest) with K‑Fold weighted blending and 28‑point normalization per HSEG documentation.

- TextRiskClassifier (app/models/text_risk_classifier.py)
  - Detects risk signals in open‑ended responses (crisis/High/Moderate/Low).
  - Defaults to rule‑based signals; supports TF‑IDF + LogisticRegression (.pkl) or transformer checkpoint (.pt).
  - Provides crisis detection, sentiment, and emotional intensity features used by the individual model.

- OrganizationalRiskAggregator (app/models/organizational_risk_model.py)
  - Aggregates individual predictions to organizational KPIs and tier.
  - Uses learned models (if available) to classify org tier and predict turnover; falls back to heuristics otherwise.
  - Generates category‑level stats, intervention priorities, and benchmarking indicators.

## Training

Use the unified trainer to build all artifacts from `data/hseg_final_dataset.csv`:

```bash
python scripts/train_all_from_final_dataset.py
```

Artifacts are saved to `app/models/trained/`:
- `individual_risk_model.pkl`
- `text_risk_classifier.pkl`
- `organizational_risk_model.pkl`

To train individual components only:
```bash
python scripts/models/train_individual_model.py
python scripts/models/train_text_classifier.py
python scripts/models/train_organizational_model.py
```

## Hyperparameters and Tuning
- Individual: tuned XGB/MLP/RF with CV‑derived ensemble weights.
- Text: GridSearchCV over TF‑IDF + LogisticRegression with per‑class threshold calibration.
- Org: LightGBM classifier/regressor with early stopping; used if present by the aggregator.

## Integration
- Backend loads `.pkl` models on startup (FastAPI). Text model supports `.pkl` pipeline.
- Frontend surfaces:
  - Survey Playground → individual predictions with chart and executive narrative
  - JSON Tool → individual and org summaries with stakeholder‑friendly outputs

## Scoring Methodology
- Centralized in `app/core/scoring.py` per HSEG_Comprehensive_Scoring_Documentation (weights, normalization, tiers).
