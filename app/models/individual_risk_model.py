"""
HSEG Individual Risk Model - Psychological Risk Prediction for Individual Employees
Ensemble model combining XGBoost, Neural Networks, and Random Forest
"""

import numpy as np
import pandas as pd
import joblib
import json
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import warnings
from pathlib import Path
from app.core import scoring as HSEG_SCORING

# ML Libraries
from sklearn.ensemble import RandomForestRegressor, VotingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import xgboost as xgb

# Data Processing
from scipy import stats
import pickle

# Suppress warnings
warnings.filterwarnings('ignore')

class IndividualRiskPredictor:
    """
    Predicts individual psychological risk scores across 6 HSEG categories
    Uses ensemble of XGBoost + Neural Network + Random Forest
    """
    
    def __init__(self, model_version: str = "v1.0.0"):
        self.model_version = model_version
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_names = []
        # HSEG scoring configuration (centralized)
        self.category_config = HSEG_SCORING.CATEGORY_CONFIG
        self.category_weights = HSEG_SCORING.CATEGORY_WEIGHTS
        self.risk_thresholds_28 = HSEG_SCORING.THRESHOLDS_28
        self.is_trained = False
    
    def extract_features(self, response_data: Dict) -> np.ndarray:
        """
        Extract features from survey response data
        Returns: Feature vector for ML prediction
        """
        features = []
        
        # Quantitative Survey Responses (22 features)
        survey_responses = response_data.get('survey_responses', {})
        for q_num in range(1, 23):  # Q1 through Q22
            q_key = f'q{q_num}'
            score = survey_responses.get(q_key, 2.5)  # Default to neutral
            features.append(float(score))
        
        # Demographic Features (11 features)
        demographics = response_data.get('demographics', {})
        
        # Age range encoding (0-5)
        age_mapping = {'18-24': 0, '25-34': 1, '35-44': 2, '45-54': 3, '55-64': 4, '65+': 5}
        age_encoded = age_mapping.get(demographics.get('age_range', '25-34'), 1)
        features.append(age_encoded)
        
        # Gender encoding (0-3)
        gender_mapping = {'Man': 0, 'Woman': 1, 'Non-binary': 2, 'Prefer_not_to_say': 3}
        gender_encoded = gender_mapping.get(demographics.get('gender_identity', 'Prefer_not_to_say'), 3)
        features.append(gender_encoded)
        
        # Tenure encoding (0-3)
        tenure_mapping = {'<1_year': 0, '1-3_years': 1, '4-7_years': 2, '8+_years': 3}
        tenure_encoded = tenure_mapping.get(demographics.get('tenure_range', '1-3_years'), 1)
        features.append(tenure_encoded)
        
        # Position level encoding (0-3)
        position_mapping = {'Entry': 0, 'Mid': 1, 'Senior': 2, 'Executive': 3}
        position_encoded = position_mapping.get(demographics.get('position_level', 'Mid'), 1)
        features.append(position_encoded)
        
        # Department encoding (0-10, domain-specific)
        department = demographics.get('department', 'Other')
        dept_encoded = hash(department) % 10  # Simple hash-based encoding
        features.append(dept_encoded)
        
        # Supervises others (0 or 1)
        supervises = 1 if demographics.get('supervises_others', False) else 0
        features.append(supervises)
        
        # Work location encoding (0-2)
        location_mapping = {'On_Site': 0, 'Remote': 1, 'Hybrid': 2}
        location_encoded = location_mapping.get(demographics.get('work_location', 'On_Site'), 0)
        features.append(location_encoded)
        
        # Employment status encoding (0-3)
        status_mapping = {'Full_Time': 0, 'Part_Time': 1, 'Contract': 2, 'Intern': 3}
        status_encoded = status_mapping.get(demographics.get('employment_status', 'Full_Time'), 0)
        features.append(status_encoded)
        
        # Education level encoding (0-3)
        education_mapping = {'High_School': 0, 'Some_College': 1, 'Bachelors': 2, 'Graduate': 3}
        education_encoded = education_mapping.get(demographics.get('education_level', 'Bachelors'), 2)
        features.append(education_encoded)
        
        # Ethnicity diversity flag (0 or 1)
        ethnicity = demographics.get('ethnicity_group', '')
        is_diverse = 1 if ',' in ethnicity or 'Multiracial' in ethnicity else 0
        features.append(is_diverse)
        
        # Domain encoding (0-2)
        domain_mapping = {'Healthcare': 0, 'University': 1, 'Business': 2}
        domain_encoded = domain_mapping.get(response_data.get('domain', 'Business'), 2)
        features.append(domain_encoded)
        
        # Response Quality Features (5 features)
        quality_data = response_data.get('response_quality', {})
        
        # Completion time normalized (0.0-1.0)
        completion_time = quality_data.get('completion_time_seconds', 300)
        completion_normalized = min(max((completion_time - 120) / 600, 0.0), 1.0)  # 2-10 minutes
        features.append(completion_normalized)
        
        # Response quality score (0.0-1.0)
        quality_score = quality_data.get('response_quality_score', 0.8)
        features.append(quality_score)
        
        # Attention check passed (0 or 1)
        attention_passed = 1 if quality_data.get('attention_check_passed', True) else 0
        features.append(attention_passed)
        
        # Straight line response flag (0 or 1)
        straight_line = 1 if quality_data.get('straight_line_response', False) else 0
        features.append(straight_line)
        
        # Text response quality (0.0-1.0)
        text_quality = quality_data.get('text_response_quality', 0.5)
        features.append(text_quality)
        
        # Text-Derived Features (12 features)
        text_analysis = response_data.get('text_analysis', {})
        
        # Sentiment features
        features.append(text_analysis.get('sentiment_mean', 0.0))  # -1.0 to 1.0
        features.append(text_analysis.get('sentiment_variance', 0.1))  # 0.0 to 1.0
        
        # Risk indicators
        features.append(text_analysis.get('risk_keyword_count', 0))  # 0-N
        features.append(1 if text_analysis.get('crisis_language_present', False) else 0)  # 0 or 1
        features.append(1 if text_analysis.get('specific_incident_described', False) else 0)  # 0 or 1
        features.append(text_analysis.get('emotional_intensity_score', 0.0))  # 0.0-1.0
        
        # Category-specific text signals (6 features)
        text_categories = text_analysis.get('category_signals', {})
        for cat_id in range(1, 7):
            cat_signal = text_categories.get(str(cat_id), 0.0)
            features.append(cat_signal)
        
        return np.array(features).reshape(1, -1)
    
    def create_ensemble_model(self, weights: Optional[List[float]] = None) -> VotingRegressor:
        """Create ensemble model with XGBoost, Neural Network, and Random Forest"""
        
        # XGBoost with tuned parameters (better generalization)
        xgb_model = xgb.XGBRegressor(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            reg_alpha=0.0,
            reg_lambda=1.0,
            random_state=42,
            objective='reg:squarederror'
        )
        
        # Neural Network with psychological risk-optimized architecture
        nn_model = MLPRegressor(
            hidden_layer_sizes=(128, 64, 32),
            activation='relu',
            solver='adam',
            alpha=0.0005,
            learning_rate='adaptive',
            learning_rate_init=0.001,
            early_stopping=True,
            n_iter_no_change=20,
            max_iter=800,
            random_state=42
        )
        
        # Random Forest for interpretability
        rf_model = RandomForestRegressor(
            n_estimators=300,
            max_depth=None,
            min_samples_split=4,
            min_samples_leaf=1,
            random_state=42
        )
        
        # Ensemble with equal weighting (weights can be tuned later if needed)
        ensemble = VotingRegressor([
            ('xgb', xgb_model),
            ('nn', nn_model), 
            ('rf', rf_model)
        ], weights=weights)

        return ensemble

    def _estimate_ensemble_weights(self, X: np.ndarray, y: np.ndarray, n_splits: int = 3) -> List[float]:
        """Estimate per-estimator weights via KFold CV using inverse MSE."""
        from sklearn.model_selection import KFold
        from sklearn.base import clone
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
        mse_sums = {'xgb': 0.0, 'nn': 0.0, 'rf': 0.0}
        eps = 1e-6
        for train_idx, val_idx in kf.split(X):
            Xtr, Xval = X[train_idx], X[val_idx]
            ytr, yval = y[train_idx], y[val_idx]
            # Create fresh estimators
            ens = self.create_ensemble_model()
            base_map = {name: est for name, est in ens.estimators}
            xgb_est = clone(base_map['xgb'])
            nn_est = clone(base_map['nn'])
            rf_est = clone(base_map['rf'])
            xgb_est.fit(Xtr, ytr)
            nn_est.fit(Xtr, ytr)
            rf_est.fit(Xtr, ytr)
            from sklearn.metrics import mean_squared_error
            mse_sums['xgb'] += mean_squared_error(yval, xgb_est.predict(Xval))
            mse_sums['nn'] += mean_squared_error(yval, nn_est.predict(Xval))
            mse_sums['rf'] += mean_squared_error(yval, rf_est.predict(Xval))
        inv = {k: 1.0 / (v / n_splits + eps) for k, v in mse_sums.items()}
        weights = [inv['xgb'], inv['nn'], inv['rf']]
        total = sum(weights)
        return [w / total for w in weights]
    
    def prepare_training_data(self, training_responses: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare training data from survey responses
        Returns: (X features, y targets)
        """
        X_list = []
        y_list = []
        
        for response in training_responses:
            try:
                # Extract features
                features = self.extract_features(response)
                X_list.append(features.flatten())
                
                # Extract target scores (6 category scores)
                targets = []
                risk_scores = response.get('risk_scores', {})
                for cat_id in range(1, 7):
                    score = risk_scores.get(str(cat_id), 2.5)
                    targets.append(float(score))
                
                y_list.append(targets)
                
            except Exception as e:
                print(f"Warning: Skipping response due to error: {e}")
                continue
        
        X = np.array(X_list)
        y = np.array(y_list)
        
        print(f"Prepared training data: {X.shape[0]} samples, {X.shape[1]} features, {y.shape[1]} targets")
        return X, y
    
    def train(self, training_responses: List[Dict], validation_split: float = 0.2) -> Dict[str, float]:
        """
        Train the individual risk prediction model
        Returns: Training metrics
        """
        print("Starting individual risk model training...")
        
        # Prepare data
        X, y = self.prepare_training_data(training_responses)
        
        if X.shape[0] < 10:
            raise ValueError("Insufficient training data. Need at least 10 samples.")
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42
        )
        
        # Scale features
        self.scalers['features'] = StandardScaler()
        X_train_scaled = self.scalers['features'].fit_transform(X_train)
        X_val_scaled = self.scalers['features'].transform(X_val)
        
        # Train models for each category
        metrics = {}
        
        for cat_id in range(6):  # 6 categories
            print(f"Training model for category {cat_id + 1}...")
            
            # Estimate ensemble weights via KFold on training fold
            weights = self._estimate_ensemble_weights(X_train_scaled, y_train[:, cat_id])
            # Create and train ensemble with weights
            model = self.create_ensemble_model(weights=weights)
            model.fit(X_train_scaled, y_train[:, cat_id])
            
            # Validate
            y_pred = model.predict(X_val_scaled)
            mse = mean_squared_error(y_val[:, cat_id], y_pred)
            r2 = r2_score(y_val[:, cat_id], y_pred)
            mae = mean_absolute_error(y_val[:, cat_id], y_pred)
            
            # Store model and metrics
            self.models[f'category_{cat_id + 1}'] = model
            metrics[f'category_{cat_id + 1}'] = {
                'mse': mse,
                'r2': r2,
                'mae': mae
            }
            
            print(f"Category {cat_id + 1} - MSE: {mse:.3f}, R²: {r2:.3f}, MAE: {mae:.3f}")
        
        # Calculate overall metrics
        overall_mse = np.mean([metrics[f'category_{i}']['mse'] for i in range(1, 7)])
        overall_r2 = np.mean([metrics[f'category_{i}']['r2'] for i in range(1, 7)])
        overall_mae = np.mean([metrics[f'category_{i}']['mae'] for i in range(1, 7)])
        
        metrics['overall'] = {
            'mse': overall_mse,
            'r2': overall_r2,
            'mae': overall_mae
        }
        
        self.is_trained = True
        print(f"Training completed - Overall R²: {overall_r2:.3f}")
        
        return metrics
    
    def predict(self, response_data: Dict) -> Dict[str, Any]:
        """
        Predict individual psychological risk scores
        Returns: Complete risk assessment
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        try:
            # Extract features
            features = self.extract_features(response_data)
            features_scaled = self.scalers['features'].transform(features)
            
            # Predict category scores
            category_scores = {}
            category_risks = {}
            
            for cat_id in range(1, 7):
                model = self.models[f'category_{cat_id}']
                score = model.predict(features_scaled)[0]
                
                # Ensure score is in valid range (1.0-4.0)
                score = max(1.0, min(4.0, score))
                category_scores[cat_id] = round(score, 2)
                
                # Determine risk level for category
                if score < 1.5:
                    risk_level = "Crisis"
                elif score < 2.5:
                    risk_level = "At Risk"
                elif score < 3.0:
                    risk_level = "Mixed"
                elif score < 3.5:
                    risk_level = "Safe"
                else:
                    risk_level = "Thriving"
                
                category_risks[cat_id] = risk_level
            
            # HSEG Comprehensive Scoring (Normalized to 28-point scale)
            # For each category: contribution = (avg_score/4) * (num_questions * weight)
            # Total max = 55.5; Normalized score = (total/55.5)*28
            category_weighted_points = {}
            total_weighted_points = 0.0
            for cat_id, score in category_scores.items():
                cfg = self.category_config.get(cat_id, {'weight': 2.0, 'num_questions': 3})
                cat_max_points = cfg['num_questions'] * cfg['weight']
                contribution = (score / 4.0) * cat_max_points
                category_weighted_points[cat_id] = round(contribution, 3)
                total_weighted_points += contribution

            overall_score_28 = HSEG_SCORING.normalize_points_to_28(total_weighted_points)
            
            # Determine overall risk tier
            if overall_score_28 <= self.risk_thresholds_28['crisis_max']:
                overall_tier = "Crisis"
            elif overall_score_28 <= self.risk_thresholds_28['at_risk_max']:
                overall_tier = "At Risk"
            elif overall_score_28 <= self.risk_thresholds_28['mixed_max']:
                overall_tier = "Mixed"
            elif overall_score_28 <= self.risk_thresholds_28['safe_max']:
                overall_tier = "Safe"
            else:
                overall_tier = "Thriving"
            
            # Generate prediction confidence
            confidence = self._calculate_confidence(features_scaled, category_scores)
            
            # Identify contributing factors
            contributing_factors = self._identify_risk_factors(response_data, category_scores)
            
            # Generate interventions
            interventions = self._generate_interventions(category_scores, overall_tier)
            
            return {
                'response_id': response_data.get('response_id') or 'unknown',
                'prediction_timestamp': datetime.now().isoformat(),
                'model_version': self.model_version,
                'overall_hseg_score': round(overall_score_28, 2),
                'overall_risk_tier': overall_tier,
                'category_scores': category_scores,
                'category_risk_levels': category_risks,
                'confidence_score': confidence,
                'contributing_factors': contributing_factors,
                'recommended_interventions': interventions,
                'scoring_breakdown': {
                    'category_weighted_points': category_weighted_points,
                    'total_weighted_points_55_5': round(total_weighted_points, 3),
                    'normalized_28_point_score': round(overall_score_28, 3)
                },
                'feature_importance': self._get_feature_importance(),
                'processing_metadata': {
                    'features_extracted': len(features.flatten()),
                    'models_used': len(self.models),
                    'prediction_quality': 'High' if confidence > 0.8 else 'Medium' if confidence > 0.6 else 'Low'
                }
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'response_id': response_data.get('response_id', 'unknown'),
                'prediction_timestamp': datetime.now().isoformat()
            }
    
    def _calculate_confidence(self, features_scaled: np.ndarray, category_scores: Dict) -> float:
        """Calculate prediction confidence based on model agreement and feature quality"""
        
        # Base confidence from feature quality
        base_confidence = 0.7
        
        # Adjust for response quality
        if len(features_scaled[0]) >= 50:  # Full feature set
            base_confidence += 0.1
        
        # Adjust for score consistency (less variance = higher confidence)
        scores = list(category_scores.values())
        score_variance = np.var(scores)
        if score_variance < 0.5:
            base_confidence += 0.1
        elif score_variance > 1.5:
            base_confidence -= 0.1
        
        # Ensure confidence is in valid range
        return max(0.5, min(0.99, base_confidence))
    
    def _identify_risk_factors(self, response_data: Dict, category_scores: Dict) -> List[str]:
        """Identify key contributing risk factors"""
        factors = []
        
        # Check for high-risk categories
        for cat_id, score in category_scores.items():
            if score < 2.0:
                category_names = {
                    1: "Authority abuse and retaliation fears",
                    2: "Discrimination and exclusion experiences", 
                    3: "Emotional manipulation and boundary violations",
                    4: "System accountability failures",
                    5: "Work-related mental health harm",
                    6: "Voice suppression and disempowerment"
                }
                factors.append(category_names.get(cat_id, f"Category {cat_id} risk"))
        
        # Check text analysis for specific risks
        text_analysis = response_data.get('text_analysis', {})
        if text_analysis.get('crisis_language_present', False):
            factors.append("Crisis-level language in responses")
        
        if text_analysis.get('specific_incident_described', False):
            factors.append("Specific harmful incidents reported")
        
        # Check demographic risk patterns
        demographics = response_data.get('demographics', {})
        if demographics.get('tenure_range') == '<1_year':
            factors.append("New employee vulnerability")
        
        return factors[:5]  # Return top 5 factors
    
    def _generate_interventions(self, category_scores: Dict, overall_tier: str) -> List[Dict]:
        """Generate targeted intervention recommendations"""
        interventions = []
        
        if overall_tier in ["Crisis", "At Risk"]:
            # Identify worst-performing categories
            worst_categories = sorted(category_scores.items(), key=lambda x: x[1])[:3]
            
            for cat_id, score in worst_categories:
                if score < 2.5:
                    intervention_mapping = {
                        1: {
                            'category': 'Power Abuse & Suppression',
                            'intervention': 'Management training on psychological safety',
                            'urgency': 'Immediate',
                            'effort': 'Medium',
                            'impact': 'High'
                        },
                        2: {
                            'category': 'Discrimination & Exclusion', 
                            'intervention': 'DEI training and policy enforcement',
                            'urgency': 'High',
                            'effort': 'Medium',
                            'impact': 'High'
                        },
                        3: {
                            'category': 'Manipulative Work Culture',
                            'intervention': 'Culture alignment and values training',
                            'urgency': 'Medium',
                            'effort': 'Low',
                            'impact': 'Medium'
                        },
                        4: {
                            'category': 'Failure of Accountability',
                            'intervention': 'Investigation process overhaul',
                            'urgency': 'Immediate',
                            'effort': 'High',
                            'impact': 'High'
                        },
                        5: {
                            'category': 'Mental Health Harm',
                            'intervention': 'Employee assistance program expansion',
                            'urgency': 'Immediate',
                            'effort': 'Low',
                            'impact': 'High'
                        },
                        6: {
                            'category': 'Erosion of Voice & Autonomy',
                            'intervention': 'Employee empowerment initiatives',
                            'urgency': 'Medium',
                            'effort': 'Medium',
                            'impact': 'Medium'
                        }
                    }
                    
                    intervention = intervention_mapping.get(cat_id)
                    if intervention:
                        interventions.append(intervention)
        
        return interventions
    
    def _get_feature_importance(self) -> Dict:
        """Get feature importance from random forest models"""
        importance_dict = {}
        
        try:
            # Get importance from first category's random forest model
            if 'category_1' in self.models:
                rf_model = self.models['category_1'].named_estimators_['rf']
                importance = rf_model.feature_importances_
                
                feature_names = [
                    'Q1_Safe_Speaking', 'Q2_Leadership_Silencing', 'Q3_Fear_Consequences',
                    'Q4_Domain_Specific', 'Q5_Fair_Treatment', 'Q6_Equal_Access',
                    # ... (would include all 50+ feature names)
                ]
                
                # Get top 10 most important features
                top_indices = np.argsort(importance)[-10:][::-1]
                for i, idx in enumerate(top_indices):
                    if idx < len(feature_names):
                        importance_dict[f'feature_{i+1}'] = {
                            'name': feature_names[idx],
                            'importance': float(importance[idx])
                        }
        except Exception as e:
            importance_dict['error'] = str(e)
        
        return importance_dict
    
    def save_model(self, filepath: str):
        """Save trained model to disk"""
        model_data = {
            'models': self.models,
            'scalers': self.scalers,
            'encoders': self.encoders,
            'category_weights': self.category_weights,
            'risk_thresholds_28': self.risk_thresholds_28,
            'model_version': self.model_version,
            'is_trained': self.is_trained,
            'feature_names': self.feature_names
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load trained model from disk"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.models = model_data['models']
        self.scalers = model_data['scalers']
        self.encoders = model_data['encoders']
        self.category_weights = model_data['category_weights']
        # Backward-compat: accept either key
        self.risk_thresholds_28 = model_data.get('risk_thresholds_28', model_data.get('risk_thresholds', self.risk_thresholds_28))
        self.model_version = model_data['model_version']
        self.is_trained = model_data['is_trained']
        self.feature_names = model_data.get('feature_names', [])
        
        print(f"Model loaded from {filepath}")
    
    def get_model_info(self) -> Dict:
        """Get model information and status"""
        return {
            'model_version': self.model_version,
            'is_trained': self.is_trained,
            'num_categories': len(self.models),
            'category_weights': self.category_weights,
            'risk_thresholds_28': self.risk_thresholds_28,
            'feature_count': len(self.feature_names) if self.feature_names else 'Unknown'
        }

# Example usage and testing functions
def create_sample_response_data() -> Dict:
    """Create sample response data for testing"""
    return {
        'response_id': 'test_001',
        'domain': 'Business',
        'survey_responses': {
            'q1': 2.0, 'q2': 3.0, 'q3': 3.0, 'q4': 2.0,
            'q5': 3.0, 'q6': 2.0, 'q7': 2.0, 'q8': 3.0,
            'q9': 3.0, 'q10': 2.0, 'q11': 2.0, 'q12': 2.0,
            'q13': 2.0, 'q14': 2.0, 'q15': 2.0, 'q16': 2.0,
            'q17': 3.0, 'q18': 2.0, 'q19': 2.0, 'q20': 3.0,
            'q21': 2.0, 'q22': 2.0
        },
        'demographics': {
            'age_range': '35-44',
            'gender_identity': 'Woman', 
            'tenure_range': '1-3_years',
            'position_level': 'Mid',
            'department': 'Engineering',
            'supervises_others': False,
            'work_location': 'Hybrid',
            'employment_status': 'Full_Time',
            'education_level': 'Bachelors',
            'ethnicity_group': 'Hispanic'
        },
        'response_quality': {
            'completion_time_seconds': 240,
            'response_quality_score': 0.85,
            'attention_check_passed': True,
            'straight_line_response': False,
            'text_response_quality': 0.9
        },
        'text_analysis': {
            'sentiment_mean': -0.2,
            'sentiment_variance': 0.3,
            'risk_keyword_count': 2,
            'crisis_language_present': False,
            'specific_incident_described': True,
            'emotional_intensity_score': 0.6,
            'category_signals': {'1': 0.7, '2': 0.3, '3': 0.4, '4': 0.6, '5': 0.5, '6': 0.4}
        },
        'risk_scores': {'1': 2.1, '2': 2.8, '3': 2.5, '4': 2.2, '5': 2.3, '6': 2.6}
    }

if __name__ == "__main__":
    # Test the individual risk model
    model = IndividualRiskPredictor()
    
    # Create sample training data
    training_data = [create_sample_response_data() for _ in range(100)]
    for i, data in enumerate(training_data):
        data['response_id'] = f'training_{i}'
        # Add some variation to the risk scores
        for cat in data['risk_scores']:
            data['risk_scores'][cat] += np.random.normal(0, 0.5)
            data['risk_scores'][cat] = max(1.0, min(4.0, data['risk_scores'][cat]))
    
    # Train model
    try:
        metrics = model.train(training_data)
        print("Training metrics:", metrics)
        
        # Test prediction
        test_data = create_sample_response_data()
        test_data['response_id'] = 'test_prediction'
        
        prediction = model.predict(test_data)
        print("\nPrediction result:", json.dumps(prediction, indent=2))
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
            
