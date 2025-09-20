# HSEG AI API Testing Guide

## ✅ Server Running Successfully
**URL:** http://localhost:8001

## 📁 Created Test Files

1. **sample_survey_data.csv** - 10 sample survey responses with complete data
2. **test_individual_request.json** - Individual prediction test data

## 🧪 Test Commands

### Health Check:
curl http://localhost:8001/health

### Individual Prediction:
curl -X POST http://localhost:8001/predict/individual -H Content-Type: application/json -d @test_individual_request.json

### API Documentation:
http://localhost:8001/docs

## 📊 Sample Response
- Overall HSEG Score: 2.65/28 (Crisis level)
- Processing Time: ~180ms
- Category breakdowns available
- Intervention recommendations included

## ✅ Working Features
- Individual risk assessment
- Health monitoring  
- API documentation
- Real-time predictions

## ⚠️ Known Issues
- File upload requires authentication
- Text classifier training incomplete (version compatibility)

Visit http://localhost:8001/docs for interactive testing!
