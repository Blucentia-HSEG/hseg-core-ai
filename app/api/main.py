"""
HSEG REST API - FastAPI server for psychological risk assessment
Provides endpoints for individual and organizational risk prediction
"""

import asyncio
import json
import uvicorn
from datetime import datetime, timedelta
import uuid
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

# FastAPI imports
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator, ConfigDict
import pandas as pd
import io

# Database imports
from app.config.database_config import (
    get_db, startup_database, shutdown_database,
    health_check as db_health_check
)
from app.models.database_models import (
    Organization, SurveyCampaign, SurveyResponse, OrganizationRiskProfile,
    DatabaseUtils, DomainType, RiskTier
)
from sqlalchemy.orm import Session

# ML Pipeline imports
from app.core.ml_pipeline import (
    initialize_ml_pipeline, predict_individual, predict_organization,
    process_campaign, get_pipeline_status, health_check as ml_health_check,
    reload_models as ml_reload_models, analyze_text_risk
)
from app.core import scoring as HSEG_SCORING
import pytesseract
from pdf2image import convert_from_bytes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommunicationRiskRequest(BaseModel):
    text: str

# Initialize FastAPI app
app = FastAPI(
    title="HSEG Psychological Risk Assessment API",
    description="API for workplace culture and psychological safety assessment",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on deployment needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Pydantic models for API
class SurveyResponseData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "response_id": "sample_001",
                    "domain": "Business",
                    "survey_responses": {
                        "q1": 3.0, "q2": 3.0, "q3": 2.5, "q4": 3.0,
                        "q5": 3.0, "q6": 3.0, "q7": 2.5,
                        "q8": 3.0, "q9": 2.5, "q10": 3.0,
                        "q11": 3.0, "q12": 2.5, "q13": 3.0, "q14": 2.5,
                        "q15": 2.5, "q16": 2.5, "q17": 3.0, "q18": 3.0,
                        "q19": 3.0, "q20": 3.0, "q21": 2.5, "q22": 3.0
                    },
                    "text_responses": {
                        "q23": "Improve transparency in decisions affecting teams.",
                        "q24": "Work has caused occasional anxiety in busy periods.",
                        "q25": "Strong peer collaboration and knowledge sharing."
                    },
                    "demographics": {
                        "age_range": "25-34",
                        "gender_identity": "Prefer_not_to_say",
                        "tenure_range": "1-3_years",
                        "position_level": "Mid",
                        "department": "Engineering",
                        "supervises_others": False,
                        "work_location": "Hybrid",
                        "employment_status": "Full_Time",
                        "education_level": "Bachelors"
                    },
                    "response_quality": {
                        "completion_time_seconds": 240,
                        "response_quality_score": 0.85,
                        "attention_check_passed": True,
                        "straight_line_response": False,
                        "text_response_quality": 0.9
                    }
                }
            ]
        }
    )
    response_id: Optional[str] = None
    domain: str = Field(..., description="Healthcare, University, or Business")
    survey_responses: Dict[str, float] = Field(..., description="Q1-Q22 responses (1-4 scale)")
    text_responses: Optional[Dict[str, str]] = Field(default={}, description="Open-ended text responses")
    demographics: Optional[Dict[str, Any]] = Field(default={}, description="Demographic information")
    response_quality: Optional[Dict[str, Any]] = Field(default={}, description="Response quality metrics")
    
    @validator('domain')
    def validate_domain(cls, v):
        if v not in ['Healthcare', 'University', 'Business']:
            raise ValueError('Domain must be Healthcare, University, or Business')
        return v
    
    @validator('survey_responses')
    def validate_responses(cls, v):
        for key, value in v.items():
            if not (1.0 <= value <= 4.0):
                raise ValueError(f'Response {key} must be between 1.0 and 4.0')
        return v

class OrganizationInfo(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "org_id": "org_demo_001",
                    "org_name": "Demo Org",
                    "domain": "Business",
                    "employee_count": 120,
                    "founded_year": 2005,
                    "is_public_company": False,
                    "industry_code": "5415",
                    "headquarters_location": "Austin, TX"
                }
            ]
        }
    )
    org_id: str
    org_name: str
    domain: str
    employee_count: Optional[int] = 100
    founded_year: Optional[int] = 2000
    is_public_company: Optional[bool] = False
    industry_code: Optional[str] = None
    headquarters_location: Optional[str] = None

class BatchPredictionRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "organization_info": {
                        "org_id": "org_demo_001",
                        "org_name": "Demo Org",
                        "domain": "Business",
                        "employee_count": 120
                    },
                    "individual_responses": [
                        {"response_id":"e1","domain":"Business","survey_responses":{"q1":3,"q2":3,"q3":3,"q4":3,"q5":3,"q6":3,"q7":3,"q8":3,"q9":3,"q10":3,"q11":3,"q12":3,"q13":3,"q14":3,"q15":3,"q16":3,"q17":3,"q18":3,"q19":3,"q20":3,"q21":3,"q22":3},"text_responses":{},"demographics":{"age_range":"25-34","gender_identity":"Man","tenure_range":"1-3_years","position_level":"Mid","department":"Engineering"}},
                        {"response_id":"e2","domain":"Business","survey_responses":{ "q1":2.5,"q2":2.5,"q3":2.5,"q4":2.5,"q5":2.5,"q6":2.5,"q7":2.5,"q8":2.5,"q9":2.5,"q10":2.5,"q11":2.5,"q12":2.5,"q13":2.5,"q14":2.5,"q15":2.5,"q16":2.5,"q17":2.5,"q18":2.5,"q19":2.5,"q20":2.5,"q21":2.5,"q22":2.5},"text_responses":{},"demographics":{"age_range":"35-44","gender_identity":"Woman","tenure_range":"4-7_years","position_level":"Senior","department":"Sales"}},
                        {"response_id":"e3","domain":"Business","survey_responses":{ "q1":3.5,"q2":3.5,"q3":3.0,"q4":3.5,"q5":3.5,"q6":3.0,"q7":3.0,"q8":3.5,"q9":3.0,"q10":3.5,"q11":3.0,"q12":3.0,"q13":3.5,"q14":3.0,"q15":3.0,"q16":3.5,"q17":3.0,"q18":3.0,"q19":3.5,"q20":3.0,"q21":3.0,"q22":3.5},"text_responses":{},"demographics":{"age_range":"45-54","gender_identity":"Non-binary","tenure_range":"8+_years","position_level":"Executive","department":"Operations"}},
                        {"response_id":"e4","domain":"Business","survey_responses":{ "q1":2.0,"q2":2.0,"q3":2.0,"q4":2.0,"q5":2.0,"q6":2.0,"q7":2.0,"q8":2.0,"q9":2.0,"q10":2.0,"q11":2.0,"q12":2.0,"q13":2.0,"q14":2.0,"q15":2.0,"q16":2.0,"q17":2.0,"q18":2.0,"q19":2.0,"q20":2.0,"q21":2.0,"q22":2.0},"text_responses":{},"demographics":{"age_range":"18-24","gender_identity":"Man","tenure_range":"<1_year","position_level":"Entry","department":"Support"}},
                        {"response_id":"e5","domain":"Business","survey_responses":{ "q1":3.0,"q2":2.5,"q3":2.5,"q4":3.0,"q5":3.0,"q6":2.5,"q7":2.5,"q8":3.0,"q9":2.5,"q10":3.0,"q11":3.0,"q12":2.5,"q13":3.0,"q14":2.5,"q15":2.5,"q16":2.5,"q17":3.0,"q18":3.0,"q19":3.0,"q20":3.0,"q21":2.5,"q22":3.0},"text_responses":{},"demographics":{"age_range":"25-34","gender_identity":"Prefer_not_to_say","tenure_range":"1-3_years","position_level":"Mid","department":"Engineering"}}
                    ]
                }
            ]
        }
    )
    organization_info: OrganizationInfo
    individual_responses: List[SurveyResponseData]
    
    @validator('individual_responses')
    def validate_responses(cls, v):
        if len(v) < 5:
            raise ValueError('Minimum 5 individual responses required for organizational assessment')
        if len(v) > 500:
            raise ValueError('Maximum 500 individual responses allowed per request')
        return v

class IndividualPredictionResponse(BaseModel):
    response_id: str
    overall_hseg_score: float
    overall_risk_tier: str
    category_scores: Dict[int, float]
    category_risk_levels: Dict[int, str]
    confidence_score: float
    contributing_factors: List[str]
    recommended_interventions: List[Dict]
    processing_time_ms: float

class OrganizationalPredictionResponse(BaseModel):
    organization_id: str
    overall_assessment: Dict[str, Any]
    category_breakdown: Dict[int, Dict[str, Any]]
    demographic_analysis: Dict[str, Dict[str, float]]
    intervention_recommendations: List[Dict[str, Any]]
    benchmarking: Dict[str, Any]
    risk_indicators: Dict[str, Any]

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str
    database: Dict[str, Any]
    ml_pipeline: Dict[str, Any]
    api_version: str

class AnalysisResult(BaseModel):
    label: str
    score: float

class TwoStepTextAnalysisResponse(BaseModel):
    hseg_risk_analysis: List[AnalysisResult]
    individual_distress_analysis: List[AnalysisResult]
    processing_time_ms: float
    model_name: str

# Authentication dependency (mock - implement proper auth for production)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Mock authentication - replace with real implementation
    if credentials and credentials.credentials == "test-token":
        return {"user_id": "test_user", "permissions": ["read", "write"]}
    return {"user_id": "anonymous", "permissions": ["read"]}

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize database and ML pipeline on startup"""
    try:
        logger.info("Starting HSEG API server...")
        
        # Initialize database
        await startup_database()
        logger.info("Database initialized")
        
        # Initialize ML pipeline
        pipeline_ready = await initialize_ml_pipeline()
        if pipeline_ready:
            logger.info("ML Pipeline initialized successfully")
        else:
            logger.warning("ML Pipeline initialization incomplete - some features may be limited")
        
        logger.info("HSEG API server startup complete")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

@app.on_event("shutdown") 
async def shutdown_event():
    """Cleanup on server shutdown"""
    try:
        await shutdown_database()
        logger.info("HSEG API server shutdown complete")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

# Health check endpoints
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check database
        db_status = db_health_check()
        
        # Check ML pipeline
        ml_status = await ml_health_check()
        
        # Overall status
        overall_status = "healthy"
        if db_status["status"] != "healthy" or ml_status["status"] != "healthy":
            overall_status = "degraded"
        
        return HealthCheckResponse(
            status=overall_status,
            timestamp=datetime.now().isoformat(),
            database=db_status,
            ml_pipeline=ml_status,
            api_version="1.0.0"
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/pipeline/status")
async def pipeline_status(user: dict = Depends(get_current_user)):
    """Get ML pipeline status and performance metrics"""
    try:
        status = get_pipeline_status()
        return JSONResponse(content=status)
    except Exception as e:
        logger.error(f"Pipeline status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/info")
async def models_info(user: dict = Depends(get_current_user)):
    """Return loaded model information and paths"""
    try:
        status = get_pipeline_status()
        return JSONResponse(content={
            'pipeline_ready': status.get('pipeline_ready'),
            'models_loaded': status.get('models_loaded'),
            'model_version': status.get('model_version'),
            'model_info': status.get('model_info')
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/models/reload")
async def models_reload(user: dict = Depends(get_current_user)):
    """Reload models from disk without retraining"""
    try:
        if "write" not in user.get("permissions", []):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        result = await ml_reload_models()
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scoring/info")
async def scoring_info():
    """Expose HSEG scoring configuration and thresholds"""
    try:
        return JSONResponse(content={
            'doc_version': HSEG_SCORING.DOC_VERSION,
            'category_config': HSEG_SCORING.CATEGORY_CONFIG,
            'category_weights': HSEG_SCORING.CATEGORY_WEIGHTS,
            'max_total_points': HSEG_SCORING.MAX_TOTAL_POINTS,
            'min_total_points': HSEG_SCORING.MIN_TOTAL_POINTS,
            'normalized_scale': {
                'min': HSEG_SCORING.NORMALIZED_MIN,
                'max': HSEG_SCORING.NORMALIZED_MAX
            },
            'thresholds_28': HSEG_SCORING.THRESHOLDS_28
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/communication_risk", response_model=TwoStepTextAnalysisResponse)
async def predict_communication_risk(
    request: Optional[CommunicationRiskRequest] = None,
    file: Optional[UploadFile] = File(None),
    user: dict = Depends(get_current_user)
):
    """Analyze text for communication risk from text or document"""
    try:
        text_to_analyze = ""
        if file:
            if file.content_type == "application/pdf":
                images = convert_from_bytes(await file.read())
                for image in images:
                    text_to_analyze += pytesseract.image_to_string(image)
            else:
                text_to_analyze = (await file.read()).decode("utf-8")
        elif request and request.text:
            text_to_analyze = request.text
        else:
            raise HTTPException(status_code=400, detail="No text or file provided")

        if not text_to_analyze.strip():
            raise HTTPException(status_code=400, detail="The provided text is empty")

        analysis = await analyze_text_risk(text_to_analyze)
        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Communication risk prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Individual prediction endpoints
@app.post("/predict/individual", response_model=IndividualPredictionResponse)
async def predict_individual_risk(
    response_data: SurveyResponseData,
    user: dict = Depends(get_current_user)
):
    """Predict psychological risk for individual survey response"""
    try:
        # Convert Pydantic model to dict
        data_dict = response_data.dict()
        # Ensure response_id is a non-empty string for downstream validation
        if not data_dict.get('response_id'):
            data_dict['response_id'] = f"ui_{uuid.uuid4().hex[:8]}"
        
        # Add user context
        data_dict['user_id'] = user.get('user_id')
        data_dict['prediction_timestamp'] = datetime.now().isoformat()
        
        # Predict individual risk
        prediction = await predict_individual(data_dict)
        
        if 'error' in prediction:
            raise HTTPException(status_code=400, detail=prediction['error'])
        
        # Coerce any missing/None response_id to a valid string for response validation
        if not prediction.get('response_id'):
            prediction['response_id'] = data_dict['response_id']
        return IndividualPredictionResponse(**prediction)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Individual prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/predict/batch/individual")
async def predict_batch_individual(
    responses: List[SurveyResponseData],
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Predict psychological risk for multiple individual responses"""
    try:
        if len(responses) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 responses per batch")
        
        predictions = []
        for response_data in responses:
            data_dict = response_data.dict()
            data_dict['user_id'] = user.get('user_id')
            
            prediction = await predict_individual(data_dict)
            predictions.append(prediction)
        
        return {
            "total_responses": len(responses),
            "successful_predictions": len([p for p in predictions if 'error' not in p]),
            "failed_predictions": len([p for p in predictions if 'error' in p]),
            "predictions": predictions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Organizational prediction endpoints
@app.post("/predict/organizational", response_model=OrganizationalPredictionResponse)
async def predict_organizational_risk(
    request: BatchPredictionRequest,
    user: dict = Depends(get_current_user)
):
    """Predict organizational risk from aggregated individual responses"""
    try:
        # Get individual predictions first
        individual_predictions = []
        for response_data in request.individual_responses:
            data_dict = response_data.dict()
            data_dict['user_id'] = user.get('user_id')
            
            prediction = await predict_individual(data_dict)
            if 'error' not in prediction:
                individual_predictions.append(prediction)
        
        if len(individual_predictions) < 5:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient valid responses: {len(individual_predictions)} (minimum 5 required)"
            )
        
        # Predict organizational risk
        org_prediction = await predict_organization(
            request.organization_info.org_id,
            individual_predictions,
            request.organization_info.dict()
        )
        
        if 'error' in org_prediction:
            raise HTTPException(status_code=400, detail=org_prediction['error'])

        # Map model output to API schema
        try:
            overall_assessment = {
                'org_id': request.organization_info.org_id,
                'org_name': request.organization_info.org_name,
                'overall_risk_tier': org_prediction.get('overall_risk_tier'),
                'average_hseg_score': org_prediction.get('overall_hseg_score'),
                'predicted_turnover_rate': org_prediction.get('predicted_outcomes', {}).get('predicted_turnover_rate'),
                'total_responses': org_prediction.get('sample_size'),
                'confidence_level': org_prediction.get('confidence_level'),
                'benchmark_percentile': org_prediction.get('benchmark_percentile'),
                'industry_comparison': org_prediction.get('industry_comparison'),
                'calculated_at': org_prediction.get('calculated_at')
            }

            # Category breakdown: include mean score and risk_rate if available
            category_breakdown = {}
            agg_stats = org_prediction.get('aggregated_statistics', {})
            for cid, score in org_prediction.get('category_scores', {}).items():
                stats = (agg_stats.get('categories') or {}).get(int(cid), {})
                category_breakdown[int(cid)] = {
                    'score': score,
                    'risk_rate': stats.get('risk_rate'),
                    'mean': stats.get('mean'),
                    'std': stats.get('std')
                }

            intervention_recommendations = org_prediction.get('intervention_priorities', [])

            benchmarking = {
                'percentile': org_prediction.get('benchmark_percentile'),
                'industry_comparison': org_prediction.get('industry_comparison')
            }

            risk_dist = (agg_stats.get('risk_distribution') or {})
            risk_indicators = {
                'crisis_rate': agg_stats.get('crisis_rate'),
                'at_risk_rate': agg_stats.get('at_risk_rate'),
                'safe_rate': agg_stats.get('safe_rate'),
                'risk_distribution': risk_dist
            }

            # Demographic analysis not computed here
            response_payload = {
                'organization_id': request.organization_info.org_id,
                'overall_assessment': overall_assessment,
                'category_breakdown': category_breakdown,
                'demographic_analysis': {},
                'intervention_recommendations': intervention_recommendations,
                'benchmarking': benchmarking,
                'risk_indicators': risk_indicators
            }

            return OrganizationalPredictionResponse(**response_payload)
        except Exception as map_err:
            logger.error(f"Mapping organizational prediction failed: {map_err}")
            # Fallback: return raw content for debugging
            return JSONResponse(content=org_prediction)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Organizational prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Database-driven endpoints
@app.get("/organizations")
async def list_organizations(
    domain: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """List organizations in database"""
    try:
        query = db.query(Organization)
        
        if domain:
            if domain not in ['Healthcare', 'University', 'Business']:
                raise HTTPException(status_code=400, detail="Invalid domain")
            query = query.filter(Organization.domain == DomainType(domain))
        
        organizations = query.offset(offset).limit(limit).all()
        
        return {
            "organizations": [
                {
                    "org_id": org.org_id,
                    "org_name": org.org_name,
                    "domain": org.domain.value,
                    "employee_count": org.employee_count,
                    "founded_year": org.founded_year
                }
                for org in organizations
            ],
            "total": query.count(),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"List organizations failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/organizations/{org_id}/risk-profile")
async def get_organization_risk_profile(
    org_id: str,
    campaign_id: Optional[str] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Get organization's latest risk profile"""
    try:
        query = db.query(OrganizationRiskProfile).filter(
            OrganizationRiskProfile.org_id == org_id
        )
        
        if campaign_id:
            query = query.filter(OrganizationRiskProfile.campaign_id == campaign_id)
        
        risk_profile = query.order_by(OrganizationRiskProfile.calculated_at.desc()).first()
        
        if not risk_profile:
            raise HTTPException(status_code=404, detail="Risk profile not found")
        
        return {
            "org_id": risk_profile.org_id,
            "campaign_id": risk_profile.campaign_id,
            "overall_hseg_score": risk_profile.overall_hseg_score,
            "overall_risk_tier": risk_profile.overall_risk_tier.value,
            "sample_size": risk_profile.sample_size,
            "confidence_level": risk_profile.confidence_level,
            "category_scores": json.loads(risk_profile.category_scores or "{}"),
            "predicted_outcomes": json.loads(risk_profile.predicted_outcomes or "{}"),
            "intervention_priorities": json.loads(risk_profile.intervention_priorities or "[]"),
            "benchmark_percentile": risk_profile.benchmark_percentile,
            "industry_comparison": risk_profile.industry_comparison,
            "calculated_at": risk_profile.calculated_at.isoformat(),
            "model_version": risk_profile.model_version
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get risk profile failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/campaigns/{campaign_id}/process")
async def process_survey_campaign(
    campaign_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Process survey campaign and generate risk assessment"""
    try:
        # Check if campaign exists
        campaign = db.query(SurveyCampaign).filter(
            SurveyCampaign.campaign_id == campaign_id
        ).first()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Check user permissions
        if "write" not in user.get("permissions", []):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Process campaign in background
        background_tasks.add_task(process_campaign_background, campaign_id)
        
        return {
            "message": "Campaign processing started",
            "campaign_id": campaign_id,
            "status": "processing",
            "estimated_completion": (datetime.now() + timedelta(minutes=5)).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Campaign processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_campaign_background(campaign_id: str):
    """Background task to process campaign"""
    try:
        result = await process_campaign(campaign_id)
        logger.info(f"Campaign {campaign_id} processed successfully")
        return result
    except Exception as e:
        logger.error(f"Background campaign processing failed: {e}")

# File upload endpoints
@app.post("/upload/survey-data")
async def upload_survey_data(
    file: UploadFile = File(...),
    organization_id: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    """Upload survey data from CSV/Excel file"""
    try:
        # Check permissions
        if "write" not in user.get("permissions", []):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Read file
        if file.content_type not in ["text/csv", "application/vnd.ms-excel", 
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            raise HTTPException(status_code=400, detail="File must be CSV or Excel")
        
        content = await file.read()
        
        # Parse data based on file type
        if file.content_type == "text/csv":
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        else:
            df = pd.read_excel(io.BytesIO(content))
        
        # Validate required columns
        required_columns = ['Domain', 'Q1_Safe_Speaking_Up', 'Q2_Leadership_Silencing']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {missing_columns}"
            )
        
        # Process each row
        predictions = []
        for index, row in df.iterrows():
            try:
                # Convert row to survey response format
                response_data = convert_row_to_response_data(row, index)
                
                # Predict individual risk
                prediction = await predict_individual(response_data)
                predictions.append(prediction)
                
            except Exception as e:
                logger.warning(f"Failed to process row {index}: {e}")
                predictions.append({"error": str(e), "row": index})
        
        return {
            "file_name": file.filename,
            "total_rows": len(df),
            "successful_predictions": len([p for p in predictions if 'error' not in p]),
            "failed_predictions": len([p for p in predictions if 'error' in p]),
            "predictions": predictions[:10],  # Return first 10 for preview
            "organization_id": organization_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def convert_row_to_response_data(row: pd.Series, index: int) -> Dict:
    """Convert pandas row to survey response data format"""
    
    # Extract survey responses (Q1-Q22)
    survey_responses = {}
    for i in range(1, 23):
        col_names = [f'Q{i}', f'Q{i}_Score', f'Question_{i}']
        for col_name in col_names:
            if col_name in row.index and pd.notna(row[col_name]):
                survey_responses[f'q{i}'] = float(row[col_name])
                break
        else:
            survey_responses[f'q{i}'] = 2.5  # Default neutral value
    
    # Extract demographics
    demographics = {}
    demo_mapping = {
        'Age_Range': 'age_range',
        'Gender': 'gender_identity', 
        'Tenure': 'tenure_range',
        'Position': 'position_level',
        'Department': 'department'
    }
    
    for excel_col, api_col in demo_mapping.items():
        if excel_col in row.index and pd.notna(row[excel_col]):
            demographics[api_col] = str(row[excel_col])
    
    # Extract text responses
    text_responses = {}
    text_columns = ['Q23_Change_One_Thing', 'Q24_Mental_Health_Impact', 'Q25_Workplace_Strength']
    for col in text_columns:
        if col in row.index and pd.notna(row[col]):
            text_responses[col[:3]] = str(row[col])
    
    return {
        'response_id': f'upload_{index}',
        'domain': str(row.get('Domain', 'Business')),
        'survey_responses': survey_responses,
        'text_responses': text_responses,
        'demographics': demographics,
        'response_quality': {
            'response_quality_score': 0.8,
            'attention_check_passed': True,
            'straight_line_response': False
        }
    }

# Analytics endpoints
@app.get("/analytics/dashboard/{org_id}")
async def get_dashboard_data(
    org_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Get dashboard data for organization visualization"""
    try:
        # Get latest risk profile
        risk_profile = db.query(OrganizationRiskProfile).filter(
            OrganizationRiskProfile.org_id == org_id
        ).order_by(OrganizationRiskProfile.calculated_at.desc()).first()
        
        if not risk_profile:
            raise HTTPException(status_code=404, detail="No risk assessment found for organization")
        
        # Get organization info
        organization = db.query(Organization).filter(Organization.org_id == org_id).first()
        
        # Prepare dashboard data
        dashboard_data = {
            "organization": {
                "org_id": organization.org_id,
                "org_name": organization.org_name,
                "domain": organization.domain.value,
                "employee_count": organization.employee_count
            },
            "overall_assessment": {
                "hseg_score": risk_profile.overall_hseg_score,
                "risk_tier": risk_profile.overall_risk_tier.value,
                "sample_size": risk_profile.sample_size,
                "confidence_level": risk_profile.confidence_level,
                "benchmark_percentile": risk_profile.benchmark_percentile
            },
            "category_breakdown": json.loads(risk_profile.category_scores or "{}"),
            "predicted_outcomes": json.loads(risk_profile.predicted_outcomes or "{}"),
            "intervention_priorities": json.loads(risk_profile.intervention_priorities or "[]"),
            "visualization_data": {
                "tier_color": {
                    "Crisis": "#DC3545",
                    "At_Risk": "#FD7E14", 
                    "Mixed": "#6C757D",
                    "Safe": "#0D6EFD",
                    "Thriving": "#198754"
                }.get(risk_profile.overall_risk_tier.value, "#6C757D"),
                "chart_data": prepare_chart_data(risk_profile),
                "alerts": generate_dashboard_alerts(risk_profile)
            },
            "last_updated": risk_profile.calculated_at.isoformat()
        }
        
        return dashboard_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dashboard data retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def prepare_chart_data(risk_profile: OrganizationRiskProfile) -> Dict:
    """Prepare data for dashboard charts"""
    category_scores = json.loads(risk_profile.category_scores or "{}")
    
    return {
        "category_pie_chart": [
            {"name": "Power Abuse", "value": category_scores.get("1", {}).get("score", 0), "color": "#DC3545"},
            {"name": "Discrimination", "value": category_scores.get("2", {}).get("score", 0), "color": "#FD7E14"},
            {"name": "Manipulation", "value": category_scores.get("3", {}).get("score", 0), "color": "#FFC107"},
            {"name": "Accountability", "value": category_scores.get("4", {}).get("score", 0), "color": "#28A745"},
            {"name": "Mental Health", "value": category_scores.get("5", {}).get("score", 0), "color": "#17A2B8"},
            {"name": "Voice/Autonomy", "value": category_scores.get("6", {}).get("score", 0), "color": "#6F42C1"}
        ],
        "risk_gauge": {
            "value": risk_profile.overall_hseg_score,
            "min": 7,
            "max": 28,
            "zones": [
                {"min": 7, "max": 12, "color": "#DC3545", "label": "Crisis"},
                {"min": 13, "max": 16, "color": "#FD7E14", "label": "At Risk"},
                {"min": 17, "max": 20, "color": "#6C757D", "label": "Mixed"},
                {"min": 21, "max": 24, "color": "#0D6EFD", "label": "Safe"},
                {"min": 25, "max": 28, "color": "#198754", "label": "Thriving"}
            ]
        }
    }

def generate_dashboard_alerts(risk_profile: OrganizationRiskProfile) -> List[Dict]:
    """Generate alerts for dashboard"""
    alerts = []
    
    if risk_profile.overall_risk_tier == RiskTier.CRISIS:
        alerts.append({
            "type": "error",
            "title": "Critical Risk Detected",
            "message": "Immediate intervention required. Multiple psychological safety issues detected.",
            "urgency": "immediate"
        })
    elif risk_profile.overall_risk_tier == RiskTier.AT_RISK:
        alerts.append({
            "type": "warning", 
            "title": "Risk Warning",
            "message": "Early warning signs detected. Preventive action recommended.",
            "urgency": "high"
        })
    
    if risk_profile.sample_size < 20:
        alerts.append({
            "type": "info",
            "title": "Limited Sample Size",
            "message": f"Assessment based on {risk_profile.sample_size} responses. More data recommended for higher confidence.",
            "urgency": "low"
        })
    
    return alerts

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    )

# Main entry point
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
