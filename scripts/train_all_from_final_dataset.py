#!/usr/bin/env python3
"""
Train all HSEG models from data/hseg_final_dataset.csv and save .pkl artifacts under app/models/trained

Outputs:
 - app/models/trained/individual_risk_model.pkl (IndividualRiskPredictor artifact)
 - app/models/trained/text_risk_classifier.pkl (TF-IDF + LogisticRegression pipeline)
 - app/models/trained/organizational_risk_model.pkl (LightGBM models bundle)
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List

from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error, f1_score
from sklearn.preprocessing import LabelEncoder
import lightgbm as lgb

from app.models.individual_risk_model import IndividualRiskPredictor\nimport glob\n\n
DATA_PATH = 'data/hseg_final_dataset.csv'
OUT_DIR = 'app/models/trained'


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Coerce numeric survey columns
    for i in range(1, 23):
        col = f'q{i}'
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def build_individual_training(df: pd.DataFrame) -> List[Dict]:
    # Map questions to categories
    categories = {
        1: ['q1', 'q2', 'q3', 'q4'],
        2: ['q5', 'q6', 'q7'],
        3: ['q8', 'q9', 'q10'],
        4: ['q11', 'q12', 'q13', 'q14'],
        5: ['q15', 'q16', 'q17', 'q18'],
        6: ['q19', 'q20', 'q21', 'q22'],
    }
    training = []
    for _, row in df.iterrows():
        # Skip if many missing
        if row[[f'q{i}' for i in range(1, 23)]].isna().sum() > 4:
            continue
        # Survey responses dict (fill missing with 2.5)
        survey_responses = {f'q{i}': float(row.get(f'q{i}', 2.5)) if pd.notna(row.get(f'q{i}', np.nan)) else 2.5
                            for i in range(1, 23)}
        # Targets: category averages on 1-4 scale
        risk_scores = {}
        for cid, qs in categories.items():
            vals = [float(row.get(q, 2.5)) for q in qs if pd.notna(row.get(q, np.nan))]
            if not vals:
                vals = [2.5]
            risk_scores[str(cid)] = float(np.clip(np.mean(vals), 1.0, 4.0))
        # Minimal demographics
        demographics = {
            'age_range': str(row.get('age_range', '25-34')),
            'gender_identity': str(row.get('gender_identity', 'Prefer_not_to_say')),
            'tenure_range': str(row.get('tenure_range', '1-3_years')),
            'position_level': str(row.get('position_level', 'Mid')),
            'department': str(row.get('department', 'Other')),
            'supervises_others': bool(str(row.get('supervises_others', 'False')).strip().lower() in ['1','true','yes'])
        }
        # Text
        text_responses = {
            'q23': str(row.get('q23', '')),
            'q24': str(row.get('q24', '')),
            'q25': str(row.get('q25', '')),
        }
        training.append({
            'response_id': str(row.get('response_id', 'unknown')),
            'domain': str(row.get('domain', 'Business')),
            'survey_responses': survey_responses,
            'demographics': demographics,
            'text_responses': text_responses,
            'risk_scores': risk_scores
        })
    return training


def train_individual(df: pd.DataFrame):
    training = build_individual_training(df)
    model = IndividualRiskPredictor()
    metrics = model.train(training)
    os.makedirs(OUT_DIR, exist_ok=True)
    model.save_model(os.path.join(OUT_DIR, 'individual_risk_model.pkl'))
    return metrics


def preprocess_text(text: str) -> str:
    if pd.isna(text):
        return ''
    import re
    text = str(text).lower()
    text = re.sub(r'[^\w\s\.\!\?]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def create_crisis_label(row, survey_cols):
    text = row['combined_text']
    score = row['hseg_score']
    crisis_keywords = ['suicide','suicidal','kill myself','end my life','want to die','panic attack','ptsd','trauma','can\'t sleep','anxiety attack','severe depression','breakdown','self-harm','self harm','abuse','harassment','discrimination','retaliation','gaslighting','toxic','bullying','threatened','violated','destroyed']
    crisis_count = sum(1 for kw in crisis_keywords if kw in text)
    if crisis_count >= 3 or score <= 40:
        return 'Crisis'
    elif crisis_count >= 2 or score <= 50:
        return 'High_Risk'
    elif crisis_count >= 1 or score <= 60:
        return 'Moderate_Risk'
    else:
        return 'Low_Risk'


def train_text(df: pd.DataFrame):
    # Combine text
    df = df.copy()
    df['combined_text'] = (df.get('q23','').fillna('') + ' ' + df.get('q24','').fillna('') + ' ' + df.get('q25','').fillna('')).apply(preprocess_text)
    survey_cols = [f'q{i}' for i in range(1,23) if f'q{i}' in df.columns]
    df['hseg_score'] = df[survey_cols].sum(axis=1)
    df['crisis_label'] = df.apply(lambda r: create_crisis_label(r, survey_cols), axis=1)
    X = df['combined_text']
    y = df['crisis_label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    base_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english')),
        ('clf', LogisticRegression(random_state=42, max_iter=2000, class_weight='balanced', n_jobs=1))
    ])
    param_grid = {
        'tfidf__max_features': [20000, 40000],
        'tfidf__ngram_range': [(1,2), (1,3)],
        'tfidf__min_df': [2, 5],
        'tfidf__max_df': [0.9, 0.95],
        'clf__C': [0.5, 1.0, 2.0]
    }
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    search = GridSearchCV(base_pipeline, param_grid, cv=cv, scoring='f1_weighted', n_jobs=-1, verbose=0)
    search.fit(X_train, y_train)
    pipeline = search.best_estimator_
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print('Text classifier accuracy:', acc)
    print(classification_report(y_test, y_pred))

    # Calibrate per-class thresholds for sklearn classifier (optional)
    thresholds = {}
    if hasattr(pipeline, 'predict_proba'):
        proba = pipeline.predict_proba(X_test)
        classes = list(getattr(pipeline, 'classes_', []))
        for i, cls in enumerate(classes):
            best_thr, best_f1 = 0.5, 0.0
            for thr in [x/100 for x in range(30, 81, 5)]:
                y_pred_cls = np.where(proba[:, i] >= thr, cls, 'other')
                y_true_cls = np.where(y_test == cls, cls, 'other')
                f1 = f1_score(y_true_cls, y_pred_cls, average='weighted')
                if f1 > best_f1:
                    best_f1, best_thr = f1, thr
            thresholds[cls] = best_thr

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, 'text_risk_classifier.pkl'), 'wb') as f:
        pickle.dump({'model': pipeline, 'labels': sorted(y.unique()), 'best_params': getattr(search, 'best_params_', {}), 'thresholds': thresholds}, f)
    return acc


def create_org_features(df: pd.DataFrame) -> pd.DataFrame:
    org_rows = []
    if 'organization_name' not in df.columns:
        df['organization_name'] = 'Org'
    for org, group in df.groupby('organization_name'):
        if len(group) < 5:
            continue
        rec: Dict = {
            'organization_name': org,
            'domain': group['domain'].iloc[0] if 'domain' in group.columns else 'Business',
            'employee_count': pd.to_numeric(group.get('employee_count', pd.Series([100])), errors='coerce').fillna(100).iloc[0],
            'total_responses': len(group)
        }
        survey_cols = [f'q{i}' for i in range(1,23) if f'q{i}' in group.columns]
        # Aggregations
        for col in survey_cols:
            rec[f'{col}_mean'] = group[col].mean()
            rec[f'{col}_std'] = group[col].std()
        # Simple org indicators
        scores = group[survey_cols].sum(axis=1)
        rec['hseg_score_mean'] = scores.mean()
        rec['hseg_score_std'] = scores.std()
        # Tier proxies
        def tier(score):
            if score <= 44: return 'Crisis'
            if score <= 55: return 'At_Risk'
            if score <= 66: return 'Mixed'
            if score <= 77: return 'Safe'
            return 'Thriving'
        tiers = scores.apply(tier)
        rec['pct_crisis'] = (tiers=='Crisis').mean()
        rec['pct_at_risk'] = (tiers=='At_Risk').mean()
        rec['pct_safe'] = (tiers=='Safe').mean()
        rec['pct_thriving'] = (tiers=='Thriving').mean()
        org_rows.append(rec)
    return pd.DataFrame(org_rows)


def train_organizational(df: pd.DataFrame):
    org_df = create_org_features(df)
    if org_df.empty:
        print('Warning: No organizations with >=5 responses found. Skipping org model.')
        return None, None
    feature_cols = [c for c in org_df.columns if c not in ['organization_name']]
    le_domain = LabelEncoder()
    if 'domain' in org_df.columns:
        org_df['domain_encoded'] = le_domain.fit_transform(org_df['domain'])
        feature_cols = [c for c in feature_cols if c != 'domain'] + ['domain_encoded']
    X = org_df[feature_cols]
    # Risk label proxy
    # Create a more balanced binary label for organizational risk
    crisis = org_df.get('pct_crisis', 0).fillna(0)
    at_risk = org_df.get('pct_at_risk', 0).fillna(0)
    mean_score = org_df.get('hseg_score_mean', 60).fillna(60)
    y_risk = np.where((crisis > 0.08) | (at_risk > 0.25) | (mean_score < 62), 'High_Risk', 'Low_Risk')
    y_turnover = np.clip(org_df.get('pct_crisis',0)*2 + org_df.get('pct_at_risk',0)*0.5, 0, 0.8)
    X_train, X_test, y_risk_train, y_risk_test, y_turn_train, y_turn_test = train_test_split(
        X, y_risk, y_turnover, test_size=0.2, random_state=42, stratify=y_risk
    )
    risk_model = lgb.LGBMClassifier(
        n_estimators=500,
        learning_rate=0.05,
        num_leaves=31,
        max_depth=-1,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_alpha=0.0,
        reg_lambda=0.0,
        random_state=42
    )
    # Early stopping if possible
    try:
        risk_model.fit(X_train, y_risk_train, eval_set=[(X_test, y_risk_test)], eval_metric='logloss', early_stopping_rounds=50, verbose=False)
    except Exception:
        risk_model.fit(X_train, y_risk_train)
    turn_model = lgb.LGBMRegressor(
        n_estimators=600,
        learning_rate=0.05,
        num_leaves=31,
        max_depth=-1,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_alpha=0.0,
        reg_lambda=0.0,
        random_state=42
    )
    try:
        turn_model.fit(X_train, y_turn_train, eval_set=[(X_test, y_turn_test)], eval_metric='rmse', early_stopping_rounds=50, verbose=False)
    except Exception:
        turn_model.fit(X_train, y_turn_train)
    y_risk_pred = risk_model.predict(X_test)
    acc = accuracy_score(y_risk_test, y_risk_pred)
    y_turn_pred = turn_model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_turn_test, y_turn_pred))
    print('Org risk acc:', acc, 'Turnover RMSE:', rmse)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, 'organizational_risk_model.pkl'), 'wb') as f:
        pickle.dump({
            'risk_model': risk_model,
            'turnover_model': turn_model,
            'domain_encoder': le_domain,
            'feature_columns': feature_cols
        }, f)
    return acc, rmse


def main():
    print('Loading dataset:', DATA_PATH)
    df = load_data(DATA_PATH)
    print('Training IndividualRiskPredictor from final dataset...')
    ind_metrics = train_individual(df)
    print('Individual metrics:', ind_metrics)
    print('Training Text Risk Classifier (sklearn) from final dataset...')
    txt_acc = train_text(df)
    print('Text classifier accuracy:', txt_acc)
    print('Training Organizational risk models from final dataset...')
    org_acc, org_rmse = train_organizational(df)
    # Write a simple training report
    report = {
        'individual': ind_metrics,
        'text': {'accuracy': txt_acc},
        'organizational': {'accuracy': org_acc, 'turnover_rmse': org_rmse}
    }
    with open(os.path.join(OUT_DIR, 'training_report.json'), 'w') as fp:
        json.dump(report, fp, indent=2)
    print('Done. Artifacts saved under', OUT_DIR)


if __name__ == '__main__':
    main()




import glob


def load_data_json_first(data_dir: str) -> pd.DataFrame:
    """Load dataset from JSON chunks in data_dir if present, else CSV fallback."""
    parts = sorted(glob.glob(os.path.join(data_dir, 'hseg_data_part_*.json')))
    metadata_path = os.path.join(data_dir, 'metadata.json')
    if parts and os.path.exists(metadata_path):
        frames = []
        for p in parts:
            with open(p, 'r', encoding='utf-8') as f:
                chunk = json.load(f)
            if isinstance(chunk, list):
                frames.append(pd.DataFrame(chunk))
            elif isinstance(chunk, dict):
                frames.append(pd.DataFrame([chunk]))
        if frames:
            df = pd.concat(frames, ignore_index=True)
            for i in range(1, 23):
                col = f'q{i}'
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            return df
    return load_data(os.path.join(data_dir, 'hseg_final_dataset.csv'))
