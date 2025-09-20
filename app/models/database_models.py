"""
HSEG Database Models - SQLAlchemy ORM Models
Complete BCNF normalized schema for psychological risk assessment
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from app.config.database_config import Base
import enum
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

# Enum Definitions
class DomainType(enum.Enum):
    HEALTHCARE = "Healthcare"
    UNIVERSITY = "University" 
    BUSINESS = "Business"

class RiskTier(enum.Enum):
    CRISIS = "Crisis"
    AT_RISK = "At_Risk"
    MIXED = "Mixed"
    SAFE = "Safe"
    THRIVING = "Thriving"

class PriorityLevel(enum.Enum):
    CRITICAL = "Critical"
    SEVERE = "Severe"
    MODERATE = "Moderate"

class SurveyType(enum.Enum):
    FULL_ASSESSMENT = "Full_Assessment"
    PULSE_SURVEY = "Pulse_Survey"
    FOLLOW_UP = "Follow_Up"

class CampaignStatus(enum.Enum):
    PLANNING = "Planning"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

# Core Models
class Organization(Base):
    __tablename__ = "organizations"
    
    org_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_name = Column(String(255), nullable=False, index=True)
    domain = Column(Enum(DomainType), nullable=False, index=True)
    industry_code = Column(String(10), index=True)
    employee_count = Column(Integer, index=True)
    headquarters_location = Column(String(255))
    founded_year = Column(Integer)
    is_public_company = Column(Boolean, default=False)
    stock_ticker = Column(String(10))
    website_url = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    campaigns = relationship("SurveyCampaign", back_populates="organization")
    risk_profiles = relationship("OrganizationRiskProfile", back_populates="organization")
    
    def __repr__(self):
        return f"<Organization(id={self.org_id}, name={self.org_name}, domain={self.domain.value})>"

class SurveyCampaign(Base):
    __tablename__ = "survey_campaigns"
    
    campaign_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.org_id"), nullable=False, index=True)
    campaign_name = Column(String(255))
    survey_type = Column(Enum(SurveyType), default=SurveyType.FULL_ASSESSMENT)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    target_sample_size = Column(Integer)
    incentive_offered = Column(String(255))
    survey_method = Column(String(50), default="Anonymous")
    status = Column(Enum(CampaignStatus), default=CampaignStatus.PLANNING, index=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="campaigns")
    responses = relationship("SurveyResponse", back_populates="campaign")
    
    def __repr__(self):
        return f"<SurveyCampaign(id={self.campaign_id}, org={self.org_id}, status={self.status.value})>"

class SurveyResponse(Base):
    __tablename__ = "survey_responses"
    
    response_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String(36), ForeignKey("survey_campaigns.campaign_id"), nullable=False, index=True)
    org_id = Column(String(36), ForeignKey("organizations.org_id"), nullable=False, index=True)
    response_timestamp = Column(DateTime, nullable=False, default=func.now())
    completion_time_seconds = Column(Integer)
    response_quality_score = Column(Float)  # 0.00 to 1.00
    attention_check_passed = Column(Boolean, default=True)
    straight_line_response = Column(Boolean, default=False)
    ip_address_hash = Column(String(64))  # Anonymized for duplicate detection
    user_agent_hash = Column(String(64))
    survey_version = Column(String(10), default="v1.0")
    
    # Relationships
    campaign = relationship("SurveyCampaign", back_populates="responses")
    demographics = relationship("RespondentDemographic", uselist=False, back_populates="response")
    question_responses = relationship("QuestionResponse", back_populates="response")
    text_responses = relationship("OpenTextResponse", back_populates="response")
    risk_scores = relationship("AIRiskScore", back_populates="response")
    
    def __repr__(self):
        return f"<SurveyResponse(id={self.response_id}, campaign={self.campaign_id})>"

class RespondentDemographic(Base):
    __tablename__ = "respondent_demographics"
    
    response_id = Column(String(36), ForeignKey("survey_responses.response_id"), primary_key=True)
    age_range = Column(String(10))  # "18-24", "25-34", etc.
    gender_identity = Column(String(50))
    ethnicity_group = Column(String(200))  # Multiple values comma-separated
    education_level = Column(String(50))
    tenure_range = Column(String(20))
    position_level = Column(String(20))
    department = Column(String(100), index=True)
    role_type = Column(String(100))
    supervises_others = Column(Boolean)
    employment_status = Column(String(20))
    work_location = Column(String(20))
    
    # Relationships
    response = relationship("SurveyResponse", back_populates="demographics")
    
    def __repr__(self):
        return f"<RespondentDemographic(response_id={self.response_id}, dept={self.department})>"

class HSEGCategory(Base):
    __tablename__ = "hseg_categories"
    
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(100), nullable=False, unique=True)
    category_weight = Column(Float, nullable=False, index=True)  # 2.0, 2.5, 3.0
    priority_level = Column(Enum(PriorityLevel), nullable=False)
    description = Column(Text)
    psychological_focus = Column(String(255))
    
    # Relationships
    questions = relationship("SurveyQuestion", back_populates="category")
    risk_scores = relationship("AIRiskScore", back_populates="category")
    
    def __repr__(self):
        return f"<HSEGCategory(id={self.category_id}, name={self.category_name}, weight={self.category_weight})>"

class SurveyQuestion(Base):
    __tablename__ = "survey_questions"
    
    question_id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("hseg_categories.category_id"), nullable=False, index=True)
    question_code = Column(String(10), nullable=False, unique=True, index=True)  # Q1, Q2, etc.
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20), nullable=False)  # Likert_4, Frequency_Count, etc.
    response_scale = Column(JSON)  # Scale definitions
    is_reverse_scored = Column(Boolean, default=False)
    domain_specific = Column(Boolean, default=False)
    healthcare_text = Column(Text)
    university_text = Column(Text)
    business_text = Column(Text)
    weight_in_category = Column(Float, default=1.00)
    
    # Relationships
    category = relationship("HSEGCategory", back_populates="questions")
    responses = relationship("QuestionResponse", back_populates="question")
    
    def __repr__(self):
        return f"<SurveyQuestion(id={self.question_id}, code={self.question_code})>"

class QuestionResponse(Base):
    __tablename__ = "question_responses"
    
    response_id = Column(String(36), ForeignKey("survey_responses.response_id"), primary_key=True)
    question_id = Column(Integer, ForeignKey("survey_questions.question_id"), primary_key=True)
    raw_response = Column(String(10))  # "1", "2", "3", "4"
    normalized_score = Column(Float)  # 1.00 to 4.00, reverse scored if needed
    response_confidence = Column(Float)  # Quality indicator for this response
    
    # Relationships
    response = relationship("SurveyResponse", back_populates="question_responses")
    question = relationship("SurveyQuestion", back_populates="responses")
    
    def __repr__(self):
        return f"<QuestionResponse(response_id={self.response_id}, question_id={self.question_id}, score={self.normalized_score})>"

class OpenTextResponse(Base):
    __tablename__ = "open_text_responses"
    
    response_id = Column(String(36), ForeignKey("survey_responses.response_id"), primary_key=True)
    question_code = Column(String(10), primary_key=True)  # Q23, Q24, Q25
    response_text = Column(Text, nullable=False)
    text_length = Column(Integer)
    sentiment_score = Column(Float)  # -1.00 to 1.00
    risk_keywords = Column(JSON)  # ["panic attacks", "threatened", "retaliation"]
    ai_risk_classification = Column(String(20))  # Low, Medium, High, Critical
    ai_category_tags = Column(JSON)  # ["power_abuse", "mental_health"]
    processed_at = Column(DateTime)
    
    # Relationships
    response = relationship("SurveyResponse", back_populates="text_responses")
    
    def __repr__(self):
        return f"<OpenTextResponse(response_id={self.response_id}, question_code={self.question_code})>"

class AIRiskScore(Base):
    __tablename__ = "ai_risk_scores"
    
    response_id = Column(String(36), ForeignKey("survey_responses.response_id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("hseg_categories.category_id"), primary_key=True)
    calculated_score = Column(Float, nullable=False)  # 1.00 to 4.00
    weighted_score = Column(Float, nullable=False)  # Score * Category Weight
    confidence_interval_lower = Column(Float)
    confidence_interval_upper = Column(Float)
    risk_tier = Column(Enum(RiskTier))
    contributing_factors = Column(JSON)  # ["low_speaking_safety", "retaliation_fear"]
    model_version = Column(String(20))
    calculated_at = Column(DateTime, default=func.now())
    
    # Relationships
    response = relationship("SurveyResponse", back_populates="risk_scores")
    category = relationship("HSEGCategory", back_populates="risk_scores")
    
    def __repr__(self):
        return f"<AIRiskScore(response_id={self.response_id}, category_id={self.category_id}, score={self.calculated_score})>"

class OrganizationRiskProfile(Base):
    __tablename__ = "organization_risk_profiles"
    
    org_id = Column(String(36), ForeignKey("organizations.org_id"), primary_key=True)
    campaign_id = Column(String(36), ForeignKey("survey_campaigns.campaign_id"), primary_key=True)
    overall_hseg_score = Column(Float, nullable=False)  # 7.0 to 28.0
    overall_risk_tier = Column(Enum(RiskTier), nullable=False, index=True)
    sample_size = Column(Integer, nullable=False)
    confidence_level = Column(Float, nullable=False)  # 0.80 to 0.99
    statistical_significance = Column(Boolean)
    category_scores = Column(JSON)  # {"Power_Abuse": 8.2, "Discrimination": 11.4, ...}
    predicted_outcomes = Column(JSON)  # {"turnover_risk": 0.67, "legal_risk": 0.23, ...}
    intervention_priorities = Column(JSON)  # [{"category": "Power_Abuse", "urgency": "Immediate"}]
    benchmark_percentile = Column(Float)  # 0.0 to 100.0
    industry_comparison = Column(Float)  # Difference from industry average
    calculated_at = Column(DateTime, default=func.now())
    model_version = Column(String(20))
    
    # Relationships
    organization = relationship("Organization", back_populates="risk_profiles")
    
    def __repr__(self):
        return f"<OrganizationRiskProfile(org_id={self.org_id}, score={self.overall_hseg_score}, tier={self.overall_risk_tier.value})>"

# Additional Models for ML Pipeline
class ModelPrediction(Base):
    __tablename__ = "model_predictions"
    
    prediction_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.org_id"), nullable=False)
    campaign_id = Column(String(36), ForeignKey("survey_campaigns.campaign_id"), nullable=False)
    model_type = Column(String(50))  # "individual", "organizational", "text_classifier"
    model_version = Column(String(20))
    input_features = Column(JSON)  # Feature values used for prediction
    prediction_results = Column(JSON)  # Model outputs
    confidence_score = Column(Float)
    processing_time_ms = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<ModelPrediction(id={self.prediction_id}, type={self.model_type})>"

class ModelMetrics(Base):
    __tablename__ = "model_metrics"
    
    metric_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_type = Column(String(50), nullable=False)
    model_version = Column(String(20), nullable=False)
    metric_name = Column(String(100), nullable=False)  # "accuracy", "f1_score", etc.
    metric_value = Column(Float, nullable=False)
    evaluation_date = Column(DateTime, default=func.now())
    dataset_size = Column(Integer)
    notes = Column(Text)
    
    def __repr__(self):
        return f"<ModelMetrics(type={self.model_type}, metric={self.metric_name}, value={self.metric_value})>"

# Utility Functions for Models
class DatabaseUtils:
    """Utility functions for database operations"""
    
    @staticmethod
    def get_organization_by_name(db, org_name: str) -> Optional[Organization]:
        """Get organization by name"""
        return db.query(Organization).filter(Organization.org_name == org_name).first()
    
    @staticmethod
    def get_active_campaigns(db, org_id: str) -> List[SurveyCampaign]:
        """Get active campaigns for an organization"""
        return db.query(SurveyCampaign).filter(
            SurveyCampaign.org_id == org_id,
            SurveyCampaign.status == CampaignStatus.ACTIVE
        ).all()
    
    @staticmethod
    def get_responses_for_campaign(db, campaign_id: str) -> List[SurveyResponse]:
        """Get all responses for a campaign"""
        return db.query(SurveyResponse).filter(
            SurveyResponse.campaign_id == campaign_id
        ).all()
    
    @staticmethod
    def get_risk_profile(db, org_id: str, campaign_id: str) -> Optional[OrganizationRiskProfile]:
        """Get risk profile for organization and campaign"""
        return db.query(OrganizationRiskProfile).filter(
            OrganizationRiskProfile.org_id == org_id,
            OrganizationRiskProfile.campaign_id == campaign_id
        ).first()
    
    @staticmethod
    def get_hseg_categories(db) -> List[HSEGCategory]:
        """Get all HSEG categories"""
        return db.query(HSEGCategory).order_by(HSEGCategory.category_id).all()
    
    @staticmethod
    def get_category_questions(db, category_id: int) -> List[SurveyQuestion]:
        """Get questions for a specific category"""
        return db.query(SurveyQuestion).filter(
            SurveyQuestion.category_id == category_id
        ).all()

# Export all models and utilities
__all__ = [
    'Organization',
    'SurveyCampaign', 
    'SurveyResponse',
    'RespondentDemographic',
    'HSEGCategory',
    'SurveyQuestion',
    'QuestionResponse',
    'OpenTextResponse',
    'AIRiskScore',
    'OrganizationRiskProfile',
    'ModelPrediction',
    'ModelMetrics',
    'DatabaseUtils',
    'DomainType',
    'RiskTier',
    'PriorityLevel',
    'SurveyType',
    'CampaignStatus'
]