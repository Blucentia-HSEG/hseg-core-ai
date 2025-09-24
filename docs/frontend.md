# HSEG AI Frontend Testing Dashboard

## 🎯 Overview

A comprehensive web-based testing interface for the HSEG AI Psychological Risk Assessment API. This frontend provides full testing capabilities for all API endpoints with proper authentication handling and error management.

## ✨ Features

### 🔍 **API Health Monitoring**
- Real-time API status checking
- Visual status indicators (Healthy/Degraded/Error)
- Automatic connection testing

### 👤 **Individual Risk Assessment**
- Complete survey form (Q1-Q22) with 1.0-4.0 Likert scale
- Text response fields (Q23-Q25) for qualitative feedback
- Demographics collection with proper data validation
- Sample data generation for quick testing
- Real-time response formatting with risk tier color coding

### 🏢 **Organizational Assessment**
- Organization information collection
- Sample employee data generation (5 responses minimum)
- Bulk assessment processing
- Organizational risk aggregation results

### 📤 **File Upload Testing**
- CSV/Excel file upload support
- Authentication token handling
- File format validation
- Progress monitoring

### 🔐 **Authentication & Security**
- Bearer token configuration
- Automatic header management
- Authorization error detection
- Token validation feedback

### 📊 **System Status Dashboard**
- Pipeline status monitoring
- Performance metrics display
- Health check automation

## 🚀 Quick Start

### 1. Start the Backend API
Make sure your HSEG AI API is running:
```bash
# From the root ai-app directory
uvicorn app.api.main:app --host 0.0.0.0 --port 8001
```

### 2. Open the Frontend
Simply open `index.html` in your web browser:
```bash
# Navigate to the frontend directory
cd ai-app/frontend

# Open with default browser (Windows)
start index.html

# Open with default browser (Mac)
open index.html

# Open with default browser (Linux)
xdg-open index.html
```

### 3. Configure API Settings
1. Set the API Base URL (default: `http://localhost:8001`)
2. Add authorization token if needed for protected endpoints
3. Click "Check API Health" to verify connection

## 📋 Testing Workflows

### **Individual Assessment Testing**

1. **Quick Test with Sample Data:**
   - Click "Fill Sample Data" button
   - Review pre-filled values
   - Click "Submit Individual Assessment"
   - Review response with risk tier analysis

2. **Custom Data Testing:**
   - Fill in Response ID and Domain
   - Set survey responses (Q1-Q22) on 1.0-4.0 scale
   - Add descriptive text responses (Q23-Q25)
   - Complete demographics section
   - Submit and analyze results

### **Organizational Assessment Testing**

1. Set organization information
2. Click "Generate 5 Sample Employee Responses"
3. Submit organizational assessment
4. Review company-wide risk analysis

### **File Upload Testing**

1. **Prepare Test File:**
   - Use the sample CSV format provided
   - Include required columns: response_id, domain, q1-q22, Q23-Q25, demographics

2. **Upload Process:**
   - Set authorization token in API Configuration
   - Select CSV/Excel file
   - Add optional organization ID
   - Submit upload request

3. **Handle Authentication:**
   - Upload requires valid Bearer token
   - Error messages will indicate authentication issues
   - Test both authorized and unauthorized scenarios

## 🔧 API Endpoint Coverage

### ✅ **Fully Tested Endpoints**

- `GET /health` - API health check
- `POST /predict/individual` - Individual risk assessment
- `POST /predict/organizational` - Organizational risk assessment
- `POST /upload/survey-data` - File upload (with auth)
- `GET /pipeline/status` - System status

### 🛡️ **Authentication Testing**

- **No Auth Required:** Individual/Organizational predictions, Health check
- **Auth Required:** File upload, Pipeline status
- **Error Scenarios:** Invalid tokens, missing authorization, expired tokens

## 📊 Response Analysis Features

### **Risk Tier Color Coding**
- 🔴 **Crisis**: Red highlighting
- 🟠 **At Risk**: Orange highlighting
- 🟡 **Mixed**: Yellow highlighting
- 🟢 **Safe**: Green highlighting
- 🔵 **Thriving**: Blue highlighting

### **Response Display**
- JSON formatting with syntax highlighting
- Expandable response sections
- Error differentiation with clear messaging
- Processing time display
- Confidence score visualization

## 🎨 UI Components

### **Bootstrap 5 Framework**
- Responsive design for all screen sizes
- Professional styling with gradient themes
- Font Awesome icons for visual clarity
- Tab-based navigation for organized testing

### **Interactive Elements**
- Loading spinners during API calls
- Real-time status indicators
- Form validation with helpful error messages
- Smooth scrolling to responses

## 🧪 Sample Data Formats

### **Individual Assessment JSON**
```json
{
  "response_id": "test_001",
  "domain": "Business",
  "survey_responses": {
    "q1": 2.0,
    "q2": 3.0,
    // ... q3-q22
  },
  "text_responses": {
    "Q23": "Management needs improvement...",
    "Q24": "Work stress is manageable...",
    "Q25": "Good technical resources..."
  },
  "demographics": {
    "age_range": "35-44",
    "gender_identity": "Woman",
    "tenure_range": "1-3_years",
    "position_level": "Mid",
    "department": "Engineering"
  }
}
```

### **CSV Upload Format**
```csv
response_id,domain,q1,q2,q3,...,q22,Q23,Q24,Q25,age_range,gender_identity,tenure_range,position_level,department
test_001,Business,2.0,3.0,2.5,...,3.0,"Text response","Mental health response","Strengths",35-44,Woman,1-3_years,Mid,Engineering
```

## 🔍 Error Handling

### **Common Error Scenarios**
1. **API Connection Issues**: Network connectivity, wrong URL
2. **Authentication Errors**: Missing/invalid tokens for protected endpoints
3. **Validation Errors**: Required fields, invalid data formats
4. **Server Errors**: API processing failures, model prediction issues

### **Error Display**
- Clear error messages in red highlighting
- Detailed error information for debugging
- HTTP status code display
- Suggested resolution steps

## 🛠️ Troubleshooting

### **API Not Responding**
1. Verify backend server is running on port 8001
2. Check API Base URL configuration
3. Ensure no firewall blocking localhost connections

### **Authentication Issues**
1. Verify Bearer token format: `Bearer your-token-here`
2. Check token expiration
3. Test with endpoints that don't require auth first

### **File Upload Problems**
1. Ensure authorization token is set
2. Check file format (CSV/Excel only)
3. Verify file size under 10MB limit
4. Validate CSV column structure

### **Form Validation**
1. All Q1-Q22 survey responses are required
2. Response ID must be unique
3. Text responses should be descriptive
4. Demographics fields have specific valid values

## 🚀 Production Deployment

### **Frontend Hosting**
- Static files can be served by any web server
- No backend dependencies for the frontend itself
- CORS configuration required for cross-origin API calls

### **API Configuration**
- Update `baseUrl` for production API endpoint
- Configure proper authentication tokens
- Set up HTTPS for secure communication

## 📝 Development Notes

### **File Structure**
```
frontend/
├── index.html          # Main application interface
├── app.js             # JavaScript application logic
└── README.md          # This documentation
```

### **Dependencies**
- Bootstrap 5.1.3 (CSS framework)
- Font Awesome 6.0.0 (Icons)
- No build process required - runs directly in browser

### **Browser Compatibility**
- Modern browsers with ES6 support
- Chrome, Firefox, Safari, Edge (latest versions)
- Mobile browser support included

---

**HSEG AI Frontend Testing Dashboard** - Comprehensive API testing interface for psychological risk assessment platform.