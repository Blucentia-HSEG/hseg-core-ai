"""
HSEG Organizational Risk Model - Enterprise-Grade Organizational Risk Assessment
LightGBM-based model for predicting organizational-level psychological safety risks
"""

import numpy as np
import pandas as pd
import joblib
import json
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import warnings
from pathlib import Path
import lightgbm as lgb
from sklearn.preprocessing import LabelEncoder, StandardScaler

class OrganizationalRiskAggregator:
    """Enterprise-grade organizational-level risk assessment aggregator"""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or "app/models/trained/organizational_risk_model.pkl"
        self.model_data = None
        self.is_loaded = False
        self.risk_model = None
        self.turnover_model = None
        self.domain_encoder = None

        # Industry baselines for psychological safety
        self.industry_baselines = {
            'Healthcare': 16.5,  # Higher baseline risk due to stress
            'University': 19.2,  # Lower baseline risk
            'Business': 18.0     # Medium baseline risk
        }

        # HSEG category weights
        self.category_weights = {
            'Power_Abuse_Suppression': 3.0,
            'Discrimination_Exclusion': 2.5,
            'Manipulative_Work_Culture': 2.0,
            'Failure_Of_Accountability': 3.0,
            'Mental_Health_Harm': 2.5,
            'Erosion_Voice_Autonomy': 2.0
        }

    def load_model(self) -> bool:
        """Load the trained organizational risk model"""
        try:
            with open(self.model_path, 'rb') as f:
                self.model_data = joblib.load(f)
            if isinstance(self.model_data, dict):
                self.risk_model = self.model_data.get('risk_model')
                self.turnover_model = self.model_data.get('turnover_model')
                self.domain_encoder = self.model_data.get('domain_encoder')
            self.is_loaded = True
            print(f"Organizational risk model loaded successfully from {self.model_path}")
            return True
        except Exception as e:
            print(f"Error loading organizational model: {e}")
            self.is_loaded = False
            return False

    def aggregate_individual_predictions(self, individual_predictions: List[Dict]) -> Dict[str, Any]:
        """Aggregate individual risk predictions into organizational metrics"""

        if not individual_predictions:
            return {}

        # Calculate overall statistics
        hseg_scores = [pred.get('overall_hseg_score', 14.0) for pred in individual_predictions]
        risk_tiers = [pred.get('overall_risk_tier', 'Mixed') for pred in individual_predictions]

        # Category-level aggregation (category scores are on 1.0-4.0 scale)
        category_aggregations = {}
        for category_id in range(1, 7):
            category_scores = []
            for pred in individual_predictions:
                category_data = pred.get('category_scores', {})
                score = category_data.get(str(category_id))
                if score is None:
                    score = category_data.get(category_id, 2.5)
                category_scores.append(float(score))

            category_aggregations[category_id] = {
                'mean': float(np.mean(category_scores)),
                'std': float(np.std(category_scores)),
                'min': float(np.min(category_scores)),
                'max': float(np.max(category_scores)),
                'p25': float(np.percentile(category_scores, 25)),
                'p75': float(np.percentile(category_scores, 75)),
                # Risk rate: proportion at or below 2.5 (At-Risk threshold on 1-4 scale)
                'risk_rate': sum(1 for s in category_scores if s <= 2.5) / max(1, len(category_scores))
            }

        # Risk tier distribution
        tier_counts = {}
        for tier in risk_tiers:
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

        tier_distribution = {tier: count / len(risk_tiers) for tier, count in tier_counts.items()}

        # Overall organizational metrics
        aggregated_stats = {
            'sample_size': len(individual_predictions),
            'overall': {
                'mean': np.mean(hseg_scores),
                'std': np.std(hseg_scores),
                'min': np.min(hseg_scores),
                'max': np.max(hseg_scores),
                'p25': np.percentile(hseg_scores, 25),
                'p75': np.percentile(hseg_scores, 75)
            },
            'categories': category_aggregations,
            'risk_distribution': tier_distribution,
            'crisis_rate': tier_distribution.get('Crisis', 0.0),
            'at_risk_rate': tier_distribution.get('At_Risk', 0.0),
            'safe_rate': tier_distribution.get('Safe', 0.0) + tier_distribution.get('Thriving', 0.0)
        }

        return aggregated_stats

    def create_organizational_features(self, aggregated_stats: Dict, organization_info: Dict) -> np.ndarray:
        """Create feature vector for organizational risk prediction"""
        features = []

        # Overall Statistics (6 features)
        overall_stats = aggregated_stats.get('overall', {})
        features.extend([
            overall_stats.get('mean', 14.0),
            overall_stats.get('std', 3.0),
            overall_stats.get('min', 7.0),
            overall_stats.get('max', 28.0),
            overall_stats.get('p25', 12.0),
            overall_stats.get('p75', 16.0)
        ])

        # Category Statistics (36 features - 6 categories × 6 stats each)
        for category_id in range(1, 7):
            cat_stats = aggregated_stats.get('categories', {}).get(category_id, {})
            features.extend([
                cat_stats.get('mean', 14.0),
                cat_stats.get('std', 3.0),
                cat_stats.get('min', 7.0),
                cat_stats.get('max', 28.0),
                cat_stats.get('p25', 12.0),
                cat_stats.get('risk_rate', 0.3)
            ])

        # Risk Distribution (5 features)
        risk_dist = aggregated_stats.get('risk_distribution', {})
        features.extend([
            risk_dist.get('Crisis', 0.0),
            risk_dist.get('At_Risk', 0.0),
            risk_dist.get('Mixed', 0.5),
            risk_dist.get('Safe', 0.3),
            risk_dist.get('Thriving', 0.0)
        ])

        # Sample Quality (3 features)
        features.extend([
            aggregated_stats.get('sample_size', 10),
            aggregated_stats.get('crisis_rate', 0.0),
            aggregated_stats.get('safe_rate', 0.3)
        ])

        # Organizational Context (11 features)
        org_info = organization_info or {}

        # Domain encoding (3 features - one-hot)
        domain = org_info.get('domain', 'Business')
        features.extend([
            1 if domain == 'Healthcare' else 0,
            1 if domain == 'University' else 0,
            1 if domain == 'Business' else 0
        ])

        # Company size (log-transformed)
        employee_count = org_info.get('employee_count', 100)
        features.append(np.log10(max(employee_count, 1)))

        # Industry risk baseline
        baseline = self.industry_baselines.get(domain, 18.0)
        features.append(baseline)

        # Company age
        founded_year = org_info.get('founded_year', 2000)
        company_age = max(1, 2024 - founded_year)
        features.append(company_age)

        # Public company indicator
        features.append(1 if org_info.get('is_public_company', False) else 0)

        # Time-based features (3 features)
        current_month = datetime.now().month
        features.extend([
            np.sin(2 * np.pi * current_month / 12),  # Seasonal pattern
            current_month / 12.0,  # Month ratio
            1 if current_month in [11, 12, 1] else 0  # End-of-year indicator
        ])

        return np.array(features)

    def calculate_intervention_priorities(self, aggregated_stats: Dict, predicted_outcomes: Dict) -> List[Dict]:
        """Calculate intervention priorities based on risk assessment"""
        priorities = []

        categories = {
            1: 'Power_Abuse_Suppression',
            2: 'Discrimination_Exclusion',
            3: 'Manipulative_Work_Culture',
            4: 'Failure_Of_Accountability',
            5: 'Mental_Health_Harm',
            6: 'Erosion_Voice_Autonomy'
        }

        category_stats = aggregated_stats.get('categories', {})

        for cat_id, cat_name in categories.items():
            stats = category_stats.get(cat_id, {})
            risk_rate = stats.get('risk_rate', 0.0)
            mean_score = stats.get('mean', 14.0)
            weight = self.category_weights.get(cat_name, 2.0)

            # Calculate urgency based on risk rate, mean score, and category weight
            urgency_score = (risk_rate * 0.4 + (1 - mean_score/28.0) * 0.4 + weight/3.0 * 0.2)

            if urgency_score > 0.7:
                urgency = 'Immediate'
            elif urgency_score > 0.5:
                urgency = 'High'
            elif urgency_score > 0.3:
                urgency = 'Medium'
            else:
                urgency = 'Low'

            # Determine intervention strategy
            if risk_rate > 0.5:
                intervention = f"Immediate systemic intervention required for {cat_name.replace('_', ' ').lower()}"
                effort = 'High'
                impact = 'High'
            elif risk_rate > 0.3:
                intervention = f"Targeted improvements needed in {cat_name.replace('_', ' ').lower()}"
                effort = 'Medium'
                impact = 'High'
            else:
                intervention = f"Monitor and maintain current practices for {cat_name.replace('_', ' ').lower()}"
                effort = 'Low'
                impact = 'Medium'

            priorities.append({
                'category': cat_name,
                'category_id': cat_id,
                'risk_rate': risk_rate,
                'mean_score': mean_score,
                'urgency': urgency,
                'urgency_score': urgency_score,
                'intervention': intervention,
                'estimated_effort': effort,
                'expected_impact': impact
            })

        # Sort by urgency score (highest first)
        priorities.sort(key=lambda x: x['urgency_score'], reverse=True)

        return priorities

    def predict_organizational_risk(self, individual_predictions: List[Dict], organization_info: Dict = None) -> Dict[str, Any]:
        """Predict organizational risk from individual predictions"""

        if len(individual_predictions) < 5:
            raise ValueError("Minimum 5 individual predictions required for organizational assessment")

        # Aggregate individual predictions
        aggregated_stats = self.aggregate_individual_predictions(individual_predictions)

        # Calculate overall HSEG score (weighted average)
        overall_hseg_score = aggregated_stats['overall']['mean']

        # Optional ML-based predictions for risk tier and turnover
        overall_risk_tier = None
        ml_turnover = None
        try:
            features = self.create_organizational_features(aggregated_stats, organization_info or {})
            X = features.reshape(1, -1)
            if self.risk_model is not None:
                pred = self.risk_model.predict(X)
                overall_risk_tier = str(pred[0])
            if self.turnover_model is not None:
                ml_turnover = float(self.turnover_model.predict(X)[0])
        except Exception:
            pass

        # Heuristic fallback for risk tier
        if overall_risk_tier is None:
            crisis_rate = aggregated_stats.get('crisis_rate', 0.0)
            at_risk_rate = aggregated_stats.get('at_risk_rate', 0.0)
            safe_rate = aggregated_stats.get('safe_rate', 0.0)
            if crisis_rate > 0.3 or overall_hseg_score <= 12.0:
                overall_risk_tier = 'Crisis'
            elif crisis_rate > 0.15 or at_risk_rate > 0.4 or overall_hseg_score <= 16.0:
                overall_risk_tier = 'At_Risk'
            elif overall_hseg_score <= 20.0:
                overall_risk_tier = 'Mixed'
            elif overall_hseg_score <= 24.0:
                overall_risk_tier = 'Safe'
            else:
                overall_risk_tier = 'Thriving'

        # Predict organizational outcomes
        sample_size = len(individual_predictions)
        confidence_level = min(0.95, 0.5 + (sample_size - 5) * 0.02)  # Increase confidence with sample size

        # Predict turnover rate (inverse relationship with psychological safety)
        if ml_turnover is not None:
            predicted_turnover_rate = ml_turnover
        else:
            base_turnover = 0.15
            score_factor = max(0, (18.0 - overall_hseg_score) / 11.0)  # 0 to 1 scale
            predicted_turnover_rate = base_turnover + (score_factor * 0.35)  # Max 50% turnover

        # Predict legal risk
        crisis_factor = crisis_rate * 2.0
        predicted_legal_risk = min(0.8, crisis_factor + (1 - overall_hseg_score/28.0) * 0.3)

        # Predict productivity impact
        productivity_factor = (overall_hseg_score - 14.0) / 14.0  # Normalized around midpoint
        predicted_productivity_impact = productivity_factor * 0.4  # -40% to +40% range

        predicted_outcomes = {
            'predicted_turnover_rate': predicted_turnover_rate,
            'predicted_legal_risk': predicted_legal_risk,
            'predicted_productivity_impact': predicted_productivity_impact,
            'predicted_engagement_score': max(0.1, min(1.0, overall_hseg_score / 25.0)),
            'predicted_retention_rate': 1.0 - predicted_turnover_rate
        }

        # Calculate intervention priorities
        intervention_priorities = self.calculate_intervention_priorities(aggregated_stats, predicted_outcomes)

        # Category-level scores for dashboard
        category_scores = {}
        for cat_id in range(1, 7):
            cat_stats = aggregated_stats.get('categories', {}).get(cat_id, {})
            category_scores[str(cat_id)] = cat_stats.get('mean', 14.0)

        # Calculate statistical significance
        statistical_significance = sample_size >= 30 and aggregated_stats['overall']['std'] > 0

        # Benchmark percentile (mock - would compare against industry database)
        domain = organization_info.get('domain', 'Business') if organization_info else 'Business'
        baseline = self.industry_baselines.get(domain, 18.0)
        benchmark_percentile = max(5, min(95, ((overall_hseg_score - baseline + 5) / 10) * 100))

        # Industry comparison
        industry_comparison = overall_hseg_score - baseline

        return {
            'overall_hseg_score': round(overall_hseg_score, 2),
            'overall_risk_tier': overall_risk_tier,
            'sample_size': sample_size,
            'confidence_level': round(confidence_level, 3),
            'statistical_significance': statistical_significance,
            'category_scores': {k: round(v, 2) for k, v in category_scores.items()},
            'predicted_outcomes': {k: round(v, 3) for k, v in predicted_outcomes.items()},
            'intervention_priorities': intervention_priorities[:3],  # Top 3 priorities
            'benchmark_percentile': round(benchmark_percentile, 1),
            'industry_comparison': round(industry_comparison, 2),
            'aggregated_statistics': aggregated_stats,
            'model_version': 'v1.0.0',
            'calculated_at': datetime.now().isoformat()
        }

    # Backward-compatible alias expected by older pipeline code
    def predict(self, individual_predictions: List[Dict], organization_info: Dict = None) -> Dict[str, Any]:
        return self.predict_organizational_risk(individual_predictions, organization_info)

    def get_model_info(self) -> Dict[str, Any]:
        """Basic model info for status endpoints"""
        return {
            'is_loaded': self.is_loaded,
            'model_path': self.model_path
        }

    def generate_dashboard_data(self, organizational_assessment: Dict) -> Dict[str, Any]:
        """Generate data specifically formatted for enterprise dashboard visualization"""

        # Risk level color coding
        risk_colors = {
            'Crisis': '#dc3545',      # Red
            'At_Risk': '#fd7e14',     # Orange
            'Mixed': '#ffc107',       # Yellow
            'Safe': '#198754',        # Green
            'Thriving': '#20c997'     # Teal
        }

        # Category names for display
        category_names = {
            '1': 'Power Abuse & Suppression',
            '2': 'Discrimination & Exclusion',
            '3': 'Manipulative Work Culture',
            '4': 'Failure of Accountability',
            '5': 'Mental Health Harm',
            '6': 'Erosion of Voice & Autonomy'
        }

        # Main KPI metrics
        kpi_metrics = {
            'overall_risk_score': {
                'value': organizational_assessment['overall_hseg_score'],
                'max_value': 28.0,
                'unit': 'points',
                'trend': 'higher_better',
                'color': risk_colors[organizational_assessment['overall_risk_tier']],
                'description': 'Overall Psychological Safety Score'
            },
            'risk_tier': {
                'value': organizational_assessment['overall_risk_tier'],
                'color': risk_colors[organizational_assessment['overall_risk_tier']],
                'description': 'Current Risk Classification'
            },
            'turnover_risk': {
                'value': organizational_assessment['predicted_outcomes']['predicted_turnover_rate'] * 100,
                'unit': '%',
                'trend': 'lower_better',
                'color': '#dc3545' if organizational_assessment['predicted_outcomes']['predicted_turnover_rate'] > 0.3 else '#198754',
                'description': 'Predicted Annual Turnover Rate'
            },
            'sample_size': {
                'value': organizational_assessment['sample_size'],
                'unit': 'responses',
                'description': 'Survey Sample Size'
            }
        }

        # Category breakdown for radar chart (category scores are 1-4)
        category_radar_data = []
        for cat_id, score in organizational_assessment['category_scores'].items():
            category_radar_data.append({
                'category': category_names[cat_id],
                'score': score,
                'max_score': 4.0,
                'normalized_score': score / 4.0 * 100
            })

        # Risk distribution for pie chart
        risk_distribution = organizational_assessment['aggregated_statistics']['risk_distribution']
        risk_distribution_chart = [
            {'tier': tier, 'percentage': round(percentage * 100, 1), 'color': risk_colors.get(tier, '#6c757d')}
            for tier, percentage in risk_distribution.items()
            if percentage > 0
        ]

        # Intervention priorities for action items
        priority_actions = []
        for priority in organizational_assessment['intervention_priorities']:
            priority_actions.append({
                'category': priority['category'].replace('_', ' '),
                'urgency': priority['urgency'],
                'risk_rate': round(priority['risk_rate'] * 100, 1),
                'intervention': priority['intervention'],
                'effort': priority['estimated_effort'],
                'impact': priority['expected_impact'],
                'urgency_color': {
                    'Immediate': '#dc3545',
                    'High': '#fd7e14',
                    'Medium': '#ffc107',
                    'Low': '#198754'
                }.get(priority['urgency'], '#6c757d')
            })

        # Trend data (mock - would be historical data in real implementation)
        trend_data = []
        for i in range(6):
            month_offset = i - 5
            trend_data.append({
                'month': (datetime.now().month + month_offset) % 12 + 1,
                'score': organizational_assessment['overall_hseg_score'] + np.random.normal(0, 1),
                'month_name': datetime(2024, (datetime.now().month + month_offset) % 12 + 1, 1).strftime('%b')
            })

        # Benchmark comparison
        benchmark_data = {
            'current_score': organizational_assessment['overall_hseg_score'],
            'industry_average': organizational_assessment['overall_hseg_score'] - organizational_assessment['industry_comparison'],
            'percentile': organizational_assessment['benchmark_percentile'],
            'comparison_text': f"{'Above' if organizational_assessment['industry_comparison'] > 0 else 'Below'} industry average"
        }

        return {
            'kpi_metrics': kpi_metrics,
            'category_radar_data': category_radar_data,
            'risk_distribution_chart': risk_distribution_chart,
            'priority_actions': priority_actions,
            'trend_data': trend_data,
            'benchmark_data': benchmark_data,
            'confidence_indicators': {
                'sample_size_adequate': organizational_assessment['sample_size'] >= 30,
                'statistical_significance': organizational_assessment['statistical_significance'],
                'confidence_level': organizational_assessment['confidence_level']
            },
            'export_timestamp': datetime.now().isoformat(),
            'data_freshness': 'Current'
        }
