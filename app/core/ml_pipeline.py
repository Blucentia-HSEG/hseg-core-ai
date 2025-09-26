"""
HSEG ML Pipeline - Integrates Individual, Text, and Organizational Models
Complete prediction pipeline with database integration and error handling
"""

import asyncio
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
from pathlib import Path
import traceback

# Database imports
from sqlalchemy.orm import Session
from sqlalchemy import text as sa_text
from app.config.database_config import SessionLocal, async_db, engine, health_check as db_health_check
from app.models.database_models import (
    Organization, SurveyResponse, OrganizationRiskProfile,
    AIRiskScore, ModelPrediction, HSEGCategory, DatabaseUtils
)

# Model imports
from app.models.individual_risk_model import IndividualRiskPredictor
from app.models.text_risk_classifier import TextRiskClassifier
from app.models.organizational_risk_model import OrganizationalRiskAggregator
from transformers import pipeline as hf_pipeline
import torch

# --- Singleton for Hugging Face Zero-Shot Pipeline ---

class ZeroShotClassifierSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            logger.info("Initializing Zero-Shot Classifier for the first time...")
            device = 0 if torch.cuda.is_available() else -1
            cls._instance = hf_pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=device
            )
            logger.info(f"Zero-Shot Classifier Initialized on device: {'cuda' if device == 0 else 'cpu'}")
        return cls._instance

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HSEGMLPipeline:
    """
    Complete HSEG ML Pipeline integrating all three models
    Handles end-to-end prediction from survey data to organizational assessment
    """
    
    def __init__(self, model_version: str = "v1.0.0"):
        self.model_version = model_version
        
        # Initialize models
        self.individual_model = IndividualRiskPredictor(model_version)
        self.text_classifier = TextRiskClassifier(model_version=model_version)
        # Organizational model expects an optional model_path, not a version
        self.org_model = OrganizationalRiskAggregator()
        
        # Model paths
        # Use versioned trained models if present
        version_dir = Path(f"app/models/trained/{self.model_version}")
        base_dir = version_dir if version_dir.exists() else Path("app/models/trained")
        self.model_paths = {
            'individual': str(base_dir / 'individual_risk_model.pkl'),
            # Text model: prefer .pt (torch checkpoint). If missing, fallback to rule-based.
            'text_pt': str(base_dir / 'text_risk_classifier.pt'),
            'text_pkl': str(base_dir / 'text_risk_classifier.pkl'),
            'organizational': str(base_dir / 'organizational_risk_model.pkl')
        }
        
        # Pipeline status
        self.models_loaded = False
        self.pipeline_ready = False
        
        # Performance tracking
        self.prediction_stats = {
            'total_predictions': 0,
            'successful_predictions': 0,
            'failed_predictions': 0,
            'average_processing_time': 0.0
        }
    
    async def initialize_pipeline(self, train_if_missing: bool = True) -> bool:
        """
        Initialize the complete ML pipeline
        """
        try:
            logger.info("Initializing HSEG ML Pipeline...")
            
            # Create model directories
            Path('models').mkdir(exist_ok=True)
            
            # Try to load existing models
            models_loaded = await self._load_existing_models()
            
            if not models_loaded and train_if_missing:
                logger.info("No trained models found, training new models...")
                await self._train_all_models()
                models_loaded = True
            
            self.models_loaded = models_loaded
            self.pipeline_ready = models_loaded
            
            if self.pipeline_ready:
                logger.info("HSEG ML Pipeline initialized successfully")
            else:
                logger.warning("Pipeline initialization incomplete - some models missing")
            
            return self.pipeline_ready
            
        except Exception as e:
            logger.error(f"Pipeline initialization failed: {e}")
            traceback.print_exc()
            return False

    async def reload_models(self) -> bool:
        """Reload models from disk without training (for API reload)."""
        try:
            logger.info("Reloading HSEG models from disk...")
            # Recompute versioned paths in case version changed externally
            version_dir = Path(f"app/models/trained/{self.model_version}")
            base_dir = version_dir if version_dir.exists() else Path("app/models/trained")
            self.model_paths.update({
                'individual': str(base_dir / 'individual_risk_model.pkl'),
                'text_pt': str(base_dir / 'text_risk_classifier.pt'),
                'text_pkl': str(base_dir / 'text_risk_classifier.pkl'),
                'organizational': str(base_dir / 'organizational_risk_model.pkl')
            })

            loaded = await self._load_existing_models()
            self.models_loaded = loaded
            self.pipeline_ready = loaded
            return loaded
        except Exception as e:
            logger.error(f"Reload failed: {e}")
            return False
    
    async def _load_existing_models(self) -> bool:
        """Load existing trained models"""
        models_loaded = 0
        
        try:
            # Load individual model
            if Path(self.model_paths['individual']).exists():
                self.individual_model.load_model(self.model_paths['individual'])
                models_loaded += 1
                logger.info("Individual risk model loaded")
            
            # Load text classifier (optional)
            if Path(self.model_paths['text_pt']).exists():
                self.text_classifier.load_model(self.model_paths['text_pt'])
                models_loaded += 1
                logger.info("Text risk classifier loaded (.pt)")
            elif Path(self.model_paths['text_pkl']).exists():
                # Attempt to load legacy .pkl if present
                try:
                    self.text_classifier.load_model(self.model_paths['text_pkl'])
                    models_loaded += 1
                    logger.info("Text risk classifier loaded (.pkl)")
                except Exception as e:
                    logger.warning(f"Failed to load text classifier checkpoint: {e}. Will use rule-based fallback.")
            
            # Load organizational model
            if Path(self.model_paths['organizational']).exists():
                # Organizational model manages its own path
                self.org_model.model_path = self.model_paths['organizational']
                if self.org_model.load_model():
                    models_loaded += 1
                    logger.info("Organizational risk model loaded")
            
            return models_loaded >= 2  # At least 2 models needed for basic functionality
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return False
    
    async def _train_all_models(self):
        """Train all models with sample data"""
        try:
            # Generate sample training data
            logger.info("Generating sample training data...")
            
            # Individual model training data
            individual_training_data = self._generate_individual_training_data(500)
            
            # Text classification training data
            text_training_data = self._generate_text_training_data(200)
            
            # Organizational training data
            org_training_data = self._generate_organizational_training_data(50)
            
            # Train individual model
            logger.info("Training individual risk model...")
            individual_metrics = self.individual_model.train(individual_training_data)
            self.individual_model.save_model(self.model_paths['individual'])
            
            # Train text classifier
            logger.info("Training text risk classifier...")
            text_metrics = self.text_classifier.train(text_training_data, epochs=2)
            # Save torch checkpoint under trained path
            self.text_classifier.save_model(self.model_paths['text_pt'])
            
            # Organizational model in this codebase loads from a pre-trained artifact.
            # Skipping training here as there is no training method implemented.
            
            logger.info("All models trained successfully")
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            raise
    
    def _generate_individual_training_data(self, num_samples: int) -> List[Dict]:
        """Generate synthetic individual training data"""
        training_data = []
        
        for i in range(num_samples):
            # Generate varied risk profiles
            risk_level = np.random.choice(['low', 'medium', 'high', 'crisis'], p=[0.3, 0.4, 0.2, 0.1])
            
            if risk_level == 'crisis':
                base_scores = np.random.uniform(1.0, 2.0, 6)
            elif risk_level == 'high':
                base_scores = np.random.uniform(1.5, 2.5, 6)
            elif risk_level == 'medium':
                base_scores = np.random.uniform(2.0, 3.0, 6)
            else:
                base_scores = np.random.uniform(2.5, 4.0, 6)
            
            # Add some noise
            base_scores += np.random.normal(0, 0.2, 6)
            base_scores = np.clip(base_scores, 1.0, 4.0)
            
            data = {
                'response_id': f'train_{i}',
                'domain': np.random.choice(['Healthcare', 'University', 'Business']),
                'survey_responses': {f'q{j}': score for j, score in enumerate(base_scores[:22], 1)},
                'demographics': {
                    'age_range': np.random.choice(['18-24', '25-34', '35-44', '45-54', '55+']),
                    'gender_identity': np.random.choice(['Man', 'Woman', 'Non-binary']),
                    'tenure_range': np.random.choice(['<1_year', '1-3_years', '4-7_years', '8+_years']),
                    'position_level': np.random.choice(['Entry', 'Mid', 'Senior', 'Executive']),
                    'department': np.random.choice(['Engineering', 'Sales', 'HR', 'Operations']),
                    'supervises_others': np.random.choice([True, False]),
                    'work_location': np.random.choice(['On_Site', 'Remote', 'Hybrid']),
                    'employment_status': 'Full_Time',
                    'education_level': np.random.choice(['High_School', 'Bachelors', 'Graduate']),
                    'ethnicity_group': np.random.choice(['White', 'Hispanic', 'Asian', 'Black', 'Mixed'])
                },
                'response_quality': {
                    'completion_time_seconds': np.random.randint(120, 600),
                    'response_quality_score': np.random.uniform(0.6, 1.0),
                    'attention_check_passed': np.random.choice([True, False], p=[0.9, 0.1]),
                    'straight_line_response': np.random.choice([True, False], p=[0.1, 0.9]),
                    'text_response_quality': np.random.uniform(0.5, 1.0)
                },
                'text_analysis': {
                    'sentiment_mean': np.random.uniform(-0.5, 0.5),
                    'sentiment_variance': np.random.uniform(0.1, 0.4),
                    'risk_keyword_count': np.random.randint(0, 5),
                    'crisis_language_present': risk_level == 'crisis',
                    'specific_incident_described': np.random.choice([True, False]),
                    'emotional_intensity_score': np.random.uniform(0.0, 1.0),
                    'category_signals': {str(j): np.random.uniform(0.0, 1.0) for j in range(1, 7)}
                },
                'risk_scores': {str(j): float(score) for j, score in enumerate(base_scores, 1)}
            }
            
            training_data.append(data)
        
        return training_data
    
    def _generate_text_training_data(self, num_samples: int) -> List[Dict]:
        """Generate synthetic text training data"""
        
        # Sample texts for different risk levels
        sample_texts = {
            'crisis': [
                "My manager threatens to fire me daily and screams at everyone. I'm having panic attacks and considering suicide.",
                "Workplace harassment is destroying my mental health. HR protects abusers and silences victims.",
                "Discriminated against constantly because of my race. Management does nothing when I report it."
            ],
            'high': [
                "Management is very aggressive and creates a hostile environment for many employees.",
                "Feel excluded from important meetings and decisions because of my background.",
                "Work stress is affecting my mental health significantly."
            ],
            'medium': [
                "Sometimes management is difficult to work with but generally okay.",
                "Occasional issues with fairness but nothing too serious.",
                "Work can be stressful but manageable most days."
            ],
            'low': [
                "Great workplace with supportive management and excellent colleagues.",
                "Feel valued and respected here with good work-life balance.",
                "Management is transparent and treats everyone fairly."
            ]
        }
        
        training_data = []
        
        for i in range(num_samples):
            risk_level = np.random.choice(['crisis', 'high', 'medium', 'low'], p=[0.1, 0.2, 0.4, 0.3])
            text = np.random.choice(sample_texts[risk_level])
            
            # Generate category labels based on risk level
            if risk_level == 'crisis':
                labels = np.random.choice([0, 1], size=6, p=[0.3, 0.7])
            elif risk_level == 'high':
                labels = np.random.choice([0, 1], size=6, p=[0.6, 0.4])
            elif risk_level == 'medium':
                labels = np.random.choice([0, 1], size=6, p=[0.8, 0.2])
            else:
                labels = np.random.choice([0, 1], size=6, p=[0.9, 0.1])
            
            training_data.append({
                'text': text,
                'category_labels': labels.tolist()
            })
        
        return training_data
    
    def _generate_organizational_training_data(self, num_orgs: int) -> List[Dict]:
        """Generate synthetic organizational training data"""
        training_data = []
        
        for i in range(num_orgs):
            # Generate organization info
            domain = np.random.choice(['Healthcare', 'University', 'Business'])
            employee_count = np.random.randint(50, 2000)
            
            # Generate individual predictions for this org
            num_responses = np.random.randint(20, 100)
            individual_preds = []
            
            # Set org risk level
            org_risk = np.random.choice(['crisis', 'at_risk', 'mixed', 'safe'], p=[0.2, 0.3, 0.3, 0.2])
            
            for j in range(num_responses):
                if org_risk == 'crisis':
                    overall_score = np.random.uniform(7, 12)
                elif org_risk == 'at_risk':
                    overall_score = np.random.uniform(13, 16)
                elif org_risk == 'mixed':
                    overall_score = np.random.uniform(17, 20)
                else:
                    overall_score = np.random.uniform(21, 28)
                
                individual_pred = {
                    'response_id': f'org_{i}_resp_{j}',
                    'overall_hseg_score': overall_score,
                    'overall_risk_tier': org_risk.replace('_', ' ').title(),
                    'category_scores': {
                        k: max(1.0, min(4.0, overall_score/7 + np.random.normal(0, 0.3)))
                        for k in range(1, 7)
                    },
                    'confidence_score': np.random.uniform(0.7, 0.95),
                    'demographics': {
                        'age_range': np.random.choice(['25-34', '35-44', '45-54']),
                        'gender_identity': np.random.choice(['Man', 'Woman']),
                        'tenure_range': np.random.choice(['1-3_years', '4-7_years']),
                        'position_level': np.random.choice(['Entry', 'Mid', 'Senior']),
                        'department': np.random.choice(['Dept_A', 'Dept_B', 'Dept_C'])
                    }
                }
                individual_preds.append(individual_pred)
            
            # Generate targets
            overall_score_mean = np.mean([p['overall_hseg_score'] for p in individual_preds])
            
            org_data = {
                'organization_info': {
                    'org_id': f'org_{i:03d}',
                    'org_name': f'Organization {i+1}',
                    'domain': domain,
                    'employee_count': employee_count,
                    'founded_year': np.random.randint(1990, 2020),
                    'is_public_company': np.random.choice([True, False])
                },
                'individual_predictions': individual_preds,
                'targets': {
                    'overall_hseg_score': overall_score_mean,
                    'risk_tier': org_risk.replace('_', ' ').title(),
                    'predicted_turnover_rate': max(0.0, min(1.0, 
                        0.5 - (overall_score_mean - 17.5) / 35 + np.random.normal(0, 0.1))),
                    'predicted_legal_risk': max(0.0, min(1.0,
                        0.3 - (overall_score_mean - 17.5) / 50 + np.random.normal(0, 0.05)))
                }
            }
            
            training_data.append(org_data)
        
        return training_data
    
    async def predict_individual_risk(self, response_data: Dict) -> Dict[str, Any]:
        """
        Predict individual psychological risk with text analysis
        """
        start_time = datetime.now()
        
        try:
            # Extract text responses if available
            text_responses = response_data.get('text_responses', {})
            
            # Analyze text if present
            text_analysis = {}
            if text_responses:
                combined_text = ' '.join([
                    str(text) for text in text_responses.values() if text
                ])
                
                if combined_text.strip():
                    text_analysis = self.text_classifier.predict_text_risk(combined_text)
            
            # Add text analysis to response data
            response_data['text_analysis'] = text_analysis
            
            # Predict individual risk
            individual_prediction = self.individual_model.predict(response_data)
            
            # Combine predictions
            combined_prediction = {
                **individual_prediction,
                'text_risk_analysis': text_analysis,
                'processing_time_ms': (datetime.now() - start_time).total_seconds() * 1000
            }
            # Ensure response_id is a valid non-empty string for API schema
            if not combined_prediction.get('response_id'):
                combined_prediction['response_id'] = response_data.get('response_id') or 'unknown'
            
            # Update stats
            self.prediction_stats['total_predictions'] += 1
            self.prediction_stats['successful_predictions'] += 1
            
            return combined_prediction
            
        except Exception as e:
            logger.error(f"Individual prediction failed: {e}")
            self.prediction_stats['failed_predictions'] += 1
            
            return {
                'error': str(e),
                'response_id': response_data.get('response_id', 'unknown'),
                'prediction_timestamp': datetime.now().isoformat(),
                'processing_time_ms': (datetime.now() - start_time).total_seconds() * 1000
            }
    
    async def predict_organizational_risk(self, org_id: str, 
                                        individual_predictions: List[Dict],
                                        organization_info: Dict) -> Dict[str, Any]:
        """
        Predict organizational risk from aggregated individual predictions
        """
        start_time = datetime.now()
        
        try:
            # Predict organizational risk
            org_prediction = self.org_model.predict_organizational_risk(individual_predictions, organization_info)
            
            # Add processing metadata
            org_prediction['processing_time_ms'] = (datetime.now() - start_time).total_seconds() * 1000
            org_prediction['pipeline_version'] = self.model_version
            
            return org_prediction
            
        except Exception as e:
            logger.error(f"Organizational prediction failed: {e}")
            
            return {
                'error': str(e),
                'organization_id': org_id,
                'prediction_timestamp': datetime.now().isoformat(),
                'processing_time_ms': (datetime.now() - start_time).total_seconds() * 1000
            }
    
    async def process_survey_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Process complete survey campaign from database
        """
        start_time = datetime.now()
        
        try:
            # Get data from database
            async with SessionLocal() as db:
                # Get campaign and organization info
                campaign = db.query(SurveyCampaign).filter(
                    SurveyCampaign.campaign_id == campaign_id
                ).first()
                
                if not campaign:
                    raise ValueError(f"Campaign {campaign_id} not found")
                
                organization = campaign.organization
                responses = campaign.responses
                
                if len(responses) < 5:
                    raise ValueError(f"Insufficient responses: {len(responses)} (minimum 5 required)")
                
                # Prepare organization info
                org_info = {
                    'org_id': organization.org_id,
                    'org_name': organization.org_name,
                    'domain': organization.domain.value,
                    'employee_count': organization.employee_count,
                    'founded_year': organization.founded_year,
                    'is_public_company': organization.is_public_company
                }
                
                # Process individual responses
                individual_predictions = []
                
                for response in responses:
                    # Prepare response data
                    response_data = self._prepare_response_data(response, db)
                    
                    # Predict individual risk
                    individual_pred = await self.predict_individual_risk(response_data)
                    
                    if 'error' not in individual_pred:
                        individual_predictions.append(individual_pred)
                        
                        # Store individual prediction in database
                        await self._store_individual_prediction(response.response_id, individual_pred, db)
                
                # Predict organizational risk
                org_prediction = await self.predict_organizational_risk(
                    organization.org_id, individual_predictions, org_info
                )
                
                # Store organizational prediction
                if 'error' not in org_prediction:
                    await self._store_organizational_prediction(
                        organization.org_id, campaign_id, org_prediction, db
                    )
                
                # Compile final result
                result = {
                    'campaign_id': campaign_id,
                    'organization_info': org_info,
                    'individual_predictions_count': len(individual_predictions),
                    'organizational_prediction': org_prediction,
                    'processing_summary': {
                        'total_responses': len(responses),
                        'successful_predictions': len(individual_predictions),
                        'processing_time_ms': (datetime.now() - start_time).total_seconds() * 1000,
                        'pipeline_version': self.model_version
                    }
                }
                
                return result
                
        except Exception as e:
            logger.error(f"Campaign processing failed: {e}")
            traceback.print_exc()
            
            return {
                'error': str(e),
                'campaign_id': campaign_id,
                'processing_time_ms': (datetime.now() - start_time).total_seconds() * 1000
            }
    
    def _prepare_response_data(self, response: SurveyResponse, db: Session) -> Dict:
        """Prepare response data for ML prediction"""
        
        # Get question responses
        question_responses = {}
        for qr in response.question_responses:
            question_responses[f'q{qr.question_id}'] = qr.normalized_score
        
        # Get text responses
        text_responses = {}
        for tr in response.text_responses:
            text_responses[tr.question_code] = tr.response_text
        
        # Get demographics
        demographics = {}
        if response.demographics:
            demo = response.demographics
            demographics = {
                'age_range': demo.age_range,
                'gender_identity': demo.gender_identity,
                'tenure_range': demo.tenure_range,
                'position_level': demo.position_level,
                'department': demo.department,
                'supervises_others': demo.supervises_others,
                'work_location': demo.work_location,
                'employment_status': demo.employment_status,
                'education_level': demo.education_level,
                'ethnicity_group': demo.ethnicity_group
            }
        
        # Prepare response quality data
        response_quality = {
            'completion_time_seconds': response.completion_time_seconds or 300,
            'response_quality_score': response.response_quality_score or 0.8,
            'attention_check_passed': response.attention_check_passed,
            'straight_line_response': response.straight_line_response,
            'text_response_quality': 0.8  # Default value
        }
        
        return {
            'response_id': response.response_id,
            'domain': response.campaign.organization.domain.value,
            'survey_responses': question_responses,
            'text_responses': text_responses,
            'demographics': demographics,
            'response_quality': response_quality
        }
    
    async def _store_individual_prediction(self, response_id: str, 
                                         prediction: Dict, db: Session):
        """Store individual prediction in database"""
        try:
            # Store AI risk scores for each category
            if 'category_scores' in prediction:
                for cat_id, score in prediction['category_scores'].items():
                    risk_score = AIRiskScore(
                        response_id=response_id,
                        category_id=int(cat_id),
                        calculated_score=score,
                        weighted_score=score * self.individual_model.category_weights[int(cat_id)],
                        risk_tier=prediction.get('category_risk_levels', {}).get(cat_id, 'Mixed'),
                        contributing_factors=json.dumps(prediction.get('contributing_factors', [])),
                        model_version=self.model_version
                    )
                    db.add(risk_score)
            
            # Store model prediction
            model_prediction = ModelPrediction(
                org_id=prediction.get('organization_id', 'unknown'),
                campaign_id=prediction.get('campaign_id', 'unknown'),
                model_type='individual',
                model_version=self.model_version,
                input_features=json.dumps({}),  # Could store feature vector if needed
                prediction_results=json.dumps(prediction),
                confidence_score=prediction.get('confidence_score', 0.5),
                processing_time_ms=int(prediction.get('processing_time_ms', 0))
            )
            db.add(model_prediction)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error storing individual prediction: {e}")
            db.rollback()
    
    async def _store_organizational_prediction(self, org_id: str, campaign_id: str,
                                             prediction: Dict, db: Session):
        """Store organizational prediction in database"""
        try:
            overall_assessment = prediction.get('overall_assessment', {})
            
            # Create or update organizational risk profile
            risk_profile = OrganizationRiskProfile(
                org_id=org_id,
                campaign_id=campaign_id,
                overall_hseg_score=overall_assessment.get('overall_hseg_score', 0.0),
                overall_risk_tier=overall_assessment.get('overall_risk_tier', 'Mixed'),
                sample_size=prediction.get('processing_metadata', {}).get('individual_predictions_processed', 0),
                confidence_level=prediction.get('benchmarking', {}).get('confidence_score', 0.8),
                statistical_significance=True,  # Would calculate based on sample size
                category_scores=json.dumps(prediction.get('category_breakdown', {})),
                predicted_outcomes=json.dumps(overall_assessment),
                intervention_priorities=json.dumps(prediction.get('intervention_recommendations', [])),
                benchmark_percentile=prediction.get('benchmarking', {}).get('benchmark_percentile', 50.0),
                industry_comparison=prediction.get('benchmarking', {}).get('industry_comparison', 0.0),
                model_version=self.model_version
            )
            
            db.merge(risk_profile)  # Use merge to handle updates
            
            # Store model prediction
            model_prediction = ModelPrediction(
                org_id=org_id,
                campaign_id=campaign_id,
                model_type='organizational',
                model_version=self.model_version,
                input_features=json.dumps({}),
                prediction_results=json.dumps(prediction),
                confidence_score=prediction.get('benchmarking', {}).get('confidence_score', 0.8),
                processing_time_ms=int(prediction.get('processing_time_ms', 0))
            )
            db.add(model_prediction)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error storing organizational prediction: {e}")
            db.rollback()
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get pipeline status and performance metrics"""
        return {
            'pipeline_ready': self.pipeline_ready,
            'models_loaded': self.models_loaded,
            'model_version': self.model_version,
            'individual_model_trained': self.individual_model.is_trained,
            'text_classifier_trained': self.text_classifier.is_trained,
            'organizational_model_loaded': getattr(self.org_model, 'is_loaded', False),
            'performance_stats': self.prediction_stats,
            'model_info': {
                'individual': self.individual_model.get_model_info(),
                'text': self.text_classifier.get_model_info(),
                'organizational': {
                    'is_loaded': getattr(self.org_model, 'is_loaded', False),
                    'model_path': getattr(self.org_model, 'model_path', None)
                }
            }
        }

    async def analyze_communication_risk(self, text: str) -> Dict[str, Any]:
        """
        Analyze unstructured text for psychological safety risks using a 
        two-step zero-shot classification pipeline.
        """
        start_time = datetime.now()

        try:
            classifier = ZeroShotClassifierSingleton.get_instance()

            # --- Step 1: HSEG Risk Analysis ---
            hseg_labels = [
                "Power Abuse & Suppression",
                "Failure of Accountability",
                "Discrimination & Exclusion",
                "Mental Health Harm",
                "Manipulative Work Culture",
                "Erosion of Voice & Autonomy"
            ]
            hseg_results = classifier(text, hseg_labels, multi_label=True)

            # --- Step 2: Individual Distress Analysis ---
            distress_labels = [
                "Expressing severe personal distress, anxiety, or depression",
                "Mentioning self-harm or suicidal thoughts",
                "Neutral or positive sentiment"
            ]
            distress_results = classifier(text, distress_labels, multi_label=True)

            # --- Structure the output ---
            def structure_results(results):
                return sorted(
                    [{'label': label, 'score': score} for label, score in zip(results['labels'], results['scores'])],
                    key=lambda x: x['score'],
                    reverse=True
                )

            output = {
                "hseg_risk_analysis": structure_results(hseg_results),
                "individual_distress_analysis": structure_results(distress_results),
                "processing_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
                "model_name": classifier.model.name_or_path
            }
            
            return output

        except Exception as e:
            logger.error(f"Communication risk analysis failed: {e}")
            return {
                "error": str(e),
                "prediction_timestamp": datetime.now().isoformat(),
                "processing_time_ms": (datetime.now() - start_time).total_seconds() * 1000
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the entire pipeline"""
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        try:
            # Check model availability
            health_status['checks']['models_loaded'] = self.models_loaded
            health_status['checks']['pipeline_ready'] = self.pipeline_ready
            
            # Use the same DB health check as the API top-level to keep results consistent
            try:
                db_ok = db_health_check().get('status') == 'healthy'
                health_status['checks']['database'] = db_ok
                if not db_ok:
                    health_status['status'] = 'degraded'
            except Exception as e:
                health_status['checks']['database'] = False
                health_status['status'] = 'degraded'
            
            # Test prediction capability with sample data
            try:
                # Correct package import path
                from app.models.individual_risk_model import create_sample_response_data
                sample_data = create_sample_response_data()
                test_prediction = await self.predict_individual_risk(sample_data)
                health_status['checks']['prediction_capability'] = 'error' not in test_prediction
            except Exception as e:
                health_status['checks']['prediction_capability'] = False
                health_status['status'] = 'degraded'
            
            # Overall status
            if not all(health_status['checks'].values()):
                health_status['status'] = 'unhealthy' if health_status['status'] != 'degraded' else 'degraded'
            
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['error'] = str(e)
        
        return health_status

# Global pipeline instance
pipeline = HSEGMLPipeline()

# Convenience functions for API
async def initialize_ml_pipeline() -> bool:
    """Initialize the global ML pipeline"""
    return await pipeline.initialize_pipeline()

async def predict_individual(response_data: Dict) -> Dict[str, Any]:
    """Predict individual risk using global pipeline"""
    return await pipeline.predict_individual_risk(response_data)

async def predict_organization(org_id: str, individual_predictions: List[Dict], 
                             organization_info: Dict) -> Dict[str, Any]:
    """Predict organizational risk using global pipeline"""
    return await pipeline.predict_organizational_risk(org_id, individual_predictions, organization_info)

async def process_campaign(campaign_id: str) -> Dict[str, Any]:
    """Process survey campaign using global pipeline"""
    return await pipeline.process_survey_campaign(campaign_id)

def get_pipeline_status() -> Dict[str, Any]:
    """Get global pipeline status"""
    return pipeline.get_pipeline_status()

async def health_check() -> Dict[str, Any]:
    """Perform health check of global pipeline"""
    return await pipeline.health_check()

async def reload_models() -> Dict[str, Any]:
    """Reload models without training and return status."""
    status = await pipeline.reload_models()
    return {
        'reloaded': status,
        'model_paths': pipeline.model_paths,
        'pipeline_ready': pipeline.pipeline_ready,
        'models_loaded': pipeline.models_loaded,
        'model_version': pipeline.model_version
    }

async def analyze_text_risk(text: str) -> Dict[str, Any]:
    """Analyze text for communication risk using global pipeline"""
    return await pipeline.analyze_communication_risk(text)

# Export main components
__all__ = [
    'HSEGMLPipeline',
    'pipeline',
    'initialize_ml_pipeline',
    'predict_individual',
    'predict_organization', 
    'process_campaign',
    'get_pipeline_status',
    'health_check',
    'reload_models',
    'analyze_text_risk'
]
    
