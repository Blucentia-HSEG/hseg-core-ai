# Frontend-Backend Integration Guide

## Integration Architecture Overview

The Culture Score platform implements a modern single-page application (SPA) architecture with React frontend communicating with a FastAPI backend through REST APIs and real-time WebSocket connections.

### Technology Stack Integration
```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                          │
├─────────────────────────────────────────────────────────────┤
│  React 18.x + TypeScript + Material-UI + Recharts        │
│  State: Context API + useReducer                           │
│  HTTP: Axios + React Query                                 │
│  WebSockets: Socket.io-client                             │
└─────────────────────────────────────────────────────────────┘
                           │ HTTPS/WSS
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway                            │
├─────────────────────────────────────────────────────────────┤
│  Nginx Reverse Proxy                                       │
│  SSL Termination + Rate Limiting                          │
│  Load Balancing + Static Asset Serving                    │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend Layer                           │
├─────────────────────────────────────────────────────────────┤
│  FastAPI + Uvicorn + SQLAlchemy                           │
│  JWT Authentication + RBAC                                 │
│  ML Pipeline + Redis Cache                                 │
│  WebSocket Handlers                                        │
└─────────────────────────────────────────────────────────────┘
```

## Frontend Application Architecture

### Project Structure
```
frontend/
├── public/
│   ├── index.html              # Main HTML template
│   └── manifest.json           # PWA manifest
├── src/
│   ├── components/             # React components
│   │   ├── common/            # Reusable components
│   │   ├── survey/            # Survey-specific components
│   │   ├── dashboard/         # Analytics components
│   │   └── admin/             # Administrative components
│   ├── hooks/                 # Custom React hooks
│   ├── services/              # API service layer
│   ├── types/                 # TypeScript definitions
│   ├── utils/                 # Helper functions
│   ├── contexts/              # React contexts
│   └── App.tsx                # Main application component
├── package.json               # Dependencies and scripts
└── vite.config.ts            # Build configuration
```

### State Management Architecture
```typescript
// Global Application State
interface AppState {
  auth: AuthState;
  survey: SurveyState;
  dashboard: DashboardState;
  ui: UIState;
}

// Authentication State
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  permissions: string[];
}

// Survey State
interface SurveyState {
  currentSurvey: SurveyData | null;
  responses: SurveyResponse[];
  currentQuestion: number;
  isSubmitting: boolean;
  validation: ValidationErrors;
}

// Dashboard State
interface DashboardState {
  organizationData: OrganizationMetrics | null;
  selectedDateRange: DateRange;
  filters: DashboardFilters;
  isLoading: boolean;
  error: string | null;
}
```

### Component Architecture Pattern
```typescript
// Higher-Order Component Pattern for Authentication
const withAuth = <P extends object>(
  Component: React.ComponentType<P>
) => {
  return (props: P) => {
    const { user, isAuthenticated } = useAuth();

    if (!isAuthenticated) {
      return <LoginRedirect />;
    }

    return <Component {...props} user={user} />;
  };
};

// Usage
const ProtectedDashboard = withAuth(Dashboard);

// Custom Hook Pattern for API Integration
const useIndividualPrediction = () => {
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const predict = async (surveyData: SurveyData) => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiService.predictIndividual(surveyData);
      setPrediction(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { prediction, loading, error, predict };
};
```

## API Service Layer

### HTTP Client Configuration
```typescript
// services/apiClient.ts
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

class APIClient {
  private client: AxiosInstance;

  constructor(baseURL: string) {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request Interceptor - Add Auth Token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response Interceptor - Handle Errors
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired, try to refresh
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            try {
              const response = await this.refreshAuthToken(refreshToken);
              localStorage.setItem('auth_token', response.data.access_token);

              // Retry original request
              error.config.headers.Authorization = `Bearer ${response.data.access_token}`;
              return this.client.request(error.config);
            } catch (refreshError) {
              // Refresh failed, redirect to login
              this.handleAuthFailure();
            }
          } else {
            this.handleAuthFailure();
          }
        }
        return Promise.reject(error);
      }
    );
  }

  private handleAuthFailure() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
  }

  // Generic API methods
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }
}

export const apiClient = new APIClient(process.env.REACT_APP_API_URL || 'http://localhost:8000/v1');
```

### Prediction Service Implementation
```typescript
// services/predictionService.ts
import { apiClient } from './apiClient';
import {
  SurveyData,
  IndividualPrediction,
  OrganizationalAssessment,
  BatchPredictionRequest,
  BatchPredictionResponse
} from '../types/prediction';

export class PredictionService {

  async predictIndividual(data: SurveyData): Promise<IndividualPrediction> {
    try {
      const prediction = await apiClient.post<IndividualPrediction>(
        '/predict/individual',
        {
          response_id: data.responseId,
          domain: data.domain,
          survey_responses: data.surveyResponses,
          text_responses: data.textResponses,
          demographics: data.demographics,
          response_quality: this.calculateResponseQuality(data)
        }
      );

      // Cache prediction locally for offline access
      this.cacheResult('individual', data.responseId, prediction);

      return prediction;
    } catch (error) {
      console.error('Individual prediction error:', error);
      throw this.handlePredictionError(error);
    }
  }

  async predictOrganizational(
    orgId: string,
    filters?: OrganizationalFilters
  ): Promise<OrganizationalAssessment> {
    try {
      const assessment = await apiClient.post<OrganizationalAssessment>(
        '/predict/organizational',
        {
          organization_id: orgId,
          assessment_date: new Date().toISOString().split('T')[0],
          filters: filters || {}
        }
      );

      return assessment;
    } catch (error) {
      console.error('Organizational prediction error:', error);
      throw this.handlePredictionError(error);
    }
  }

  async batchPredict(requests: SurveyData[]): Promise<BatchPredictionResponse> {
    const batchData: BatchPredictionRequest = {
      batch_id: `batch_${Date.now()}`,
      responses: requests.map(data => ({
        response_id: data.responseId,
        survey_responses: data.surveyResponses,
        demographics: data.demographics,
        text_responses: data.textResponses
      }))
    };

    return apiClient.post<BatchPredictionResponse>('/predict/batch/individual', batchData);
  }

  private calculateResponseQuality(data: SurveyData): ResponseQuality {
    const responses = Object.values(data.surveyResponses);
    const textResponses = Object.values(data.textResponses || {});

    return {
      completion_rate: responses.filter(r => r !== null && r !== undefined).length / 22,
      response_time_seconds: data.responseTime || 300,
      text_length_avg: textResponses.reduce((sum, text) => sum + text.length, 0) / textResponses.length || 0
    };
  }

  private cacheResult(type: string, id: string, result: any): void {
    const cacheKey = `prediction_${type}_${id}`;
    const cacheData = {
      result,
      timestamp: Date.now(),
      ttl: 3600000 // 1 hour
    };

    try {
      localStorage.setItem(cacheKey, JSON.stringify(cacheData));
    } catch (error) {
      console.warn('Failed to cache prediction result:', error);
    }
  }

  private handlePredictionError(error: any): Error {
    if (error.response) {
      const { status, data } = error.response;

      switch (status) {
        case 400:
          return new Error(`Invalid request: ${data.detail}`);
        case 422:
          return new Error(`Validation error: ${data.errors?.[0]?.message || data.detail}`);
        case 429:
          return new Error('Rate limit exceeded. Please try again later.');
        case 503:
          return new Error('Service temporarily unavailable. Please try again.');
        default:
          return new Error(`Prediction failed: ${data.detail || 'Unknown error'}`);
      }
    }

    return new Error('Network error. Please check your connection.');
  }
}

export const predictionService = new PredictionService();
```

### Dashboard Service Implementation
```typescript
// services/dashboardService.ts
import { apiClient } from './apiClient';
import { DashboardData, OrganizationMetrics, AnalyticsFilters } from '../types/dashboard';

export class DashboardService {

  async getDashboardData(
    orgId: string,
    filters: AnalyticsFilters = {}
  ): Promise<DashboardData> {
    const params = new URLSearchParams();

    if (filters.dateRange) params.append('date_range', filters.dateRange);
    if (filters.departments?.length) params.append('departments', filters.departments.join(','));
    if (filters.metrics?.length) params.append('metrics', filters.metrics.join(','));

    const data = await apiClient.get<DashboardData>(
      `/analytics/dashboard/${orgId}?${params.toString()}`
    );

    return data;
  }

  async getOrganizationProfile(orgId: string): Promise<OrganizationMetrics> {
    return apiClient.get<OrganizationMetrics>(`/organizations/${orgId}/risk-profile`);
  }

  async exportDashboardData(
    orgId: string,
    format: 'csv' | 'excel' | 'pdf',
    filters: AnalyticsFilters = {}
  ): Promise<Blob> {
    const params = new URLSearchParams({
      format,
      ...filters
    });

    const response = await apiClient.get(
      `/analytics/export/${orgId}?${params.toString()}`,
      { responseType: 'blob' }
    );

    return response;
  }
}

export const dashboardService = new DashboardService();
```

## Real-time Communication

### WebSocket Integration
```typescript
// services/websocketService.ts
import { io, Socket } from 'socket.io-client';

export class WebSocketService {
  private socket: Socket | null = null;
  private eventHandlers: Map<string, Function[]> = new Map();

  connect(token: string): void {
    this.socket = io(process.env.REACT_APP_WS_URL || 'ws://localhost:8000', {
      auth: { token },
      transports: ['websocket'],
      upgrade: true
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.emit('connection', { status: 'connected' });
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
      this.emit('connection', { status: 'disconnected' });
    });

    this.socket.on('prediction_completed', (data) => {
      this.emit('predictionCompleted', data);
    });

    this.socket.on('dashboard_update', (data) => {
      this.emit('dashboardUpdate', data);
    });

    this.socket.on('organization_alert', (data) => {
      this.emit('organizationAlert', data);
    });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  on(event: string, handler: Function): void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, []);
    }
    this.eventHandlers.get(event)!.push(handler);
  }

  off(event: string, handler: Function): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  private emit(event: string, data: any): void {
    const handlers = this.eventHandlers.get(event) || [];
    handlers.forEach(handler => handler(data));
  }

  joinOrganizationRoom(orgId: string): void {
    if (this.socket) {
      this.socket.emit('join_organization', { organization_id: orgId });
    }
  }

  leaveOrganizationRoom(orgId: string): void {
    if (this.socket) {
      this.socket.emit('leave_organization', { organization_id: orgId });
    }
  }
}

export const websocketService = new WebSocketService();
```

### Real-time Dashboard Updates
```typescript
// hooks/useRealtimeDashboard.ts
import { useState, useEffect } from 'react';
import { websocketService } from '../services/websocketService';
import { dashboardService } from '../services/dashboardService';
import { DashboardData } from '../types/dashboard';

export const useRealtimeDashboard = (orgId: string) => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  useEffect(() => {
    // Initial data load
    loadDashboardData();

    // Setup WebSocket listeners
    websocketService.on('connection', handleConnection);
    websocketService.on('dashboardUpdate', handleDashboardUpdate);
    websocketService.joinOrganizationRoom(orgId);

    return () => {
      websocketService.off('connection', handleConnection);
      websocketService.off('dashboardUpdate', handleDashboardUpdate);
      websocketService.leaveOrganizationRoom(orgId);
    };
  }, [orgId]);

  const loadDashboardData = async () => {
    try {
      const data = await dashboardService.getDashboardData(orgId);
      setDashboardData(data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

  const handleConnection = (event: any) => {
    setIsConnected(event.status === 'connected');
  };

  const handleDashboardUpdate = (update: any) => {
    if (update.organization_id === orgId) {
      setDashboardData(prevData => ({
        ...prevData!,
        ...update.data
      }));
      setLastUpdate(new Date());
    }
  };

  const refreshData = () => {
    loadDashboardData();
  };

  return {
    dashboardData,
    isConnected,
    lastUpdate,
    refreshData
  };
};
```

## Survey Component Integration

### Survey Form Implementation
```typescript
// components/survey/SurveyForm.tsx
import React, { useState, useCallback } from 'react';
import {
  Stepper, Step, StepLabel, Button, Paper,
  Typography, CircularProgress
} from '@mui/material';
import { SurveyQuestion } from './SurveyQuestion';
import { PredictionResults } from './PredictionResults';
import { useSurveyForm } from '../../hooks/useSurveyForm';
import { SurveyData, SurveyResponse } from '../../types/survey';

interface SurveyFormProps {
  onComplete: (prediction: IndividualPrediction) => void;
  orgId: string;
}

export const SurveyForm: React.FC<SurveyFormProps> = ({ onComplete, orgId }) => {
  const {
    currentStep,
    responses,
    demographics,
    textResponses,
    validation,
    isSubmitting,
    prediction,
    handleResponseChange,
    handleDemographicChange,
    handleTextResponseChange,
    nextStep,
    prevStep,
    submitSurvey
  } = useSurveyForm(orgId);

  const totalSteps = 4; // Survey questions, Demographics, Text responses, Review

  const renderStepContent = useCallback(() => {
    switch (currentStep) {
      case 0:
        return (
          <SurveyQuestion
            responses={responses}
            validation={validation}
            onResponseChange={handleResponseChange}
          />
        );
      case 1:
        return (
          <DemographicsForm
            demographics={demographics}
            onDemographicChange={handleDemographicChange}
          />
        );
      case 2:
        return (
          <TextResponseForm
            textResponses={textResponses}
            onTextResponseChange={handleTextResponseChange}
          />
        );
      case 3:
        return (
          <SurveyReview
            responses={responses}
            demographics={demographics}
            textResponses={textResponses}
          />
        );
      default:
        return null;
    }
  }, [currentStep, responses, demographics, textResponses, validation]);

  const handleNext = useCallback(async () => {
    if (currentStep === totalSteps - 1) {
      // Final step - submit survey
      const result = await submitSurvey();
      if (result) {
        onComplete(result);
      }
    } else {
      nextStep();
    }
  }, [currentStep, totalSteps, submitSurvey, nextStep, onComplete]);

  if (prediction) {
    return <PredictionResults prediction={prediction} />;
  }

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Culture Assessment Survey
      </Typography>

      <Stepper activeStep={currentStep} sx={{ mb: 4 }}>
        <Step>
          <StepLabel>Survey Questions</StepLabel>
        </Step>
        <Step>
          <StepLabel>Demographics</StepLabel>
        </Step>
        <Step>
          <StepLabel>Additional Comments</StepLabel>
        </Step>
        <Step>
          <StepLabel>Review & Submit</StepLabel>
        </Step>
      </Stepper>

      {renderStepContent()}

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
        <Button
          disabled={currentStep === 0}
          onClick={prevStep}
        >
          Previous
        </Button>

        <Button
          variant="contained"
          onClick={handleNext}
          disabled={isSubmitting}
          startIcon={isSubmitting ? <CircularProgress size={20} /> : null}
        >
          {isSubmitting ? 'Processing...' :
           currentStep === totalSteps - 1 ? 'Submit Survey' : 'Next'}
        </Button>
      </Box>
    </Paper>
  );
};
```

### Survey Form Hook
```typescript
// hooks/useSurveyForm.ts
import { useState, useCallback } from 'react';
import { predictionService } from '../services/predictionService';
import { SurveyResponse, Demographics, TextResponses, ValidationErrors } from '../types/survey';

export const useSurveyForm = (orgId: string) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [responses, setResponses] = useState<SurveyResponse>({});
  const [demographics, setDemographics] = useState<Demographics>({});
  const [textResponses, setTextResponses] = useState<TextResponses>({});
  const [validation, setValidation] = useState<ValidationErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [prediction, setPrediction] = useState(null);

  const validateStep = useCallback((step: number): boolean => {
    const errors: ValidationErrors = {};

    switch (step) {
      case 0: // Survey questions
        for (let i = 1; i <= 22; i++) {
          const key = `q${i}`;
          if (!responses[key] || responses[key] < 1 || responses[key] > 4) {
            errors[key] = 'Please select a rating between 1 and 4';
          }
        }
        break;

      case 1: // Demographics
        if (!demographics.age_range) errors.age_range = 'Age range is required';
        if (!demographics.department) errors.department = 'Department is required';
        if (!demographics.position_level) errors.position_level = 'Position level is required';
        break;

      case 2: // Text responses (optional)
        // Optional step, no validation required
        break;

      case 3: // Review
        // Final validation before submission
        if (Object.keys(responses).length < 22) {
          errors.general = 'Please complete all survey questions';
        }
        break;
    }

    setValidation(errors);
    return Object.keys(errors).length === 0;
  }, [responses, demographics]);

  const handleResponseChange = useCallback((questionId: string, value: number) => {
    setResponses(prev => ({ ...prev, [questionId]: value }));

    // Clear validation error for this field
    if (validation[questionId]) {
      setValidation(prev => {
        const newValidation = { ...prev };
        delete newValidation[questionId];
        return newValidation;
      });
    }
  }, [validation]);

  const handleDemographicChange = useCallback((field: string, value: any) => {
    setDemographics(prev => ({ ...prev, [field]: value }));

    // Clear validation error for this field
    if (validation[field]) {
      setValidation(prev => {
        const newValidation = { ...prev };
        delete newValidation[field];
        return newValidation;
      });
    }
  }, [validation]);

  const handleTextResponseChange = useCallback((questionId: string, value: string) => {
    setTextResponses(prev => ({ ...prev, [questionId]: value }));
  }, []);

  const nextStep = useCallback(() => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, 3));
    }
  }, [currentStep, validateStep]);

  const prevStep = useCallback(() => {
    setCurrentStep(prev => Math.max(prev - 1, 0));
  }, []);

  const submitSurvey = useCallback(async () => {
    if (!validateStep(currentStep)) {
      return null;
    }

    setIsSubmitting(true);

    try {
      const surveyData = {
        responseId: `resp_${Date.now()}`,
        domain: 'Business', // Default or from org settings
        surveyResponses: responses,
        demographics,
        textResponses,
        responseTime: Date.now() // Track completion time
      };

      const result = await predictionService.predictIndividual(surveyData);
      setPrediction(result);

      // Track completion analytics
      analytics.track('survey_completed', {
        organization_id: orgId,
        culture_score: result.overall_culture_score,
        risk_tier: result.overall_risk_tier,
        completion_time_ms: Date.now()
      });

      return result;
    } catch (error) {
      console.error('Survey submission failed:', error);
      setValidation({ general: error.message });
      return null;
    } finally {
      setIsSubmitting(false);
    }
  }, [currentStep, responses, demographics, textResponses, orgId, validateStep]);

  return {
    currentStep,
    responses,
    demographics,
    textResponses,
    validation,
    isSubmitting,
    prediction,
    handleResponseChange,
    handleDemographicChange,
    handleTextResponseChange,
    nextStep,
    prevStep,
    submitSurvey
  };
};
```

## Dashboard Component Integration

### Main Dashboard Component
```typescript
// components/dashboard/Dashboard.tsx
import React, { useState, useEffect } from 'react';
import {
  Grid, Card, CardContent, Typography, Box,
  FormControl, InputLabel, Select, MenuItem,
  CircularProgress, Alert
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { CultureScoreChart } from './CultureScoreChart';
import { RiskDistributionChart } from './RiskDistributionChart';
import { DepartmentComparison } from './DepartmentComparison';
import { KPICards } from './KPICards';
import { useRealtimeDashboard } from '../../hooks/useRealtimeDashboard';
import { useAuth } from '../../hooks/useAuth';

export const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [dateRange, setDateRange] = useState('30d');
  const [selectedDepartments, setSelectedDepartments] = useState<string[]>([]);

  const {
    dashboardData,
    isConnected,
    lastUpdate,
    refreshData
  } = useRealtimeDashboard(user?.organization_id);

  if (!dashboardData) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <CircularProgress />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Loading dashboard data...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4">
          Culture Dashboard
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Date Range</InputLabel>
            <Select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              label="Date Range"
            >
              <MenuItem value="7d">Last 7 days</MenuItem>
              <MenuItem value="30d">Last 30 days</MenuItem>
              <MenuItem value="90d">Last 3 months</MenuItem>
              <MenuItem value="1y">Last year</MenuItem>
            </Select>
          </FormControl>

          {/* Connection Status */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                backgroundColor: isConnected ? 'success.main' : 'error.main'
              }}
            />
            <Typography variant="caption" color="text.secondary">
              {isConnected ? 'Live' : 'Disconnected'}
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Real-time Update Indicator */}
      {lastUpdate && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Dashboard updated at {lastUpdate.toLocaleTimeString()}
        </Alert>
      )}

      {/* KPI Cards */}
      <KPICards
        summary={dashboardData.summary}
        kpis={dashboardData.kpis}
        sx={{ mb: 3 }}
      />

      {/* Charts Grid */}
      <Grid container spacing={3}>
        {/* Culture Score Trend */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Culture Score Trend
              </Typography>
              <CultureScoreChart
                data={dashboardData.charts.culture_score_trend}
                height={300}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Risk Distribution */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Distribution
              </Typography>
              <RiskDistributionChart
                data={dashboardData.charts.risk_distribution}
                height={300}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Department Comparison */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Department Comparison
              </Typography>
              <DepartmentComparison
                data={dashboardData.charts.department_comparison}
                height={400}
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
```

## Error Handling & User Experience

### Global Error Boundary
```typescript
// components/common/ErrorBoundary.tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Box, Typography, Button, Alert } from '@mui/material';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error boundary caught an error:', error, errorInfo);

    // Report to error monitoring service
    if (window.Sentry) {
      window.Sentry.captureException(error, {
        contexts: {
          react: {
            errorInfo
          }
        }
      });
    }
  }

  public render() {
    if (this.state.hasError) {
      return (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: 400,
            p: 3
          }}
        >
          <Alert severity="error" sx={{ mb: 2, maxWidth: 600 }}>
            <Typography variant="h6" gutterBottom>
              Something went wrong
            </Typography>
            <Typography variant="body2">
              We apologize for the inconvenience. The error has been logged and our team will investigate.
            </Typography>
          </Alert>

          <Button
            variant="contained"
            onClick={() => {
              this.setState({ hasError: false, error: null });
              window.location.reload();
            }}
          >
            Reload Application
          </Button>
        </Box>
      );
    }

    return this.props.children;
  }
}
```

### API Error Handler Hook
```typescript
// hooks/useErrorHandler.ts
import { useState, useCallback } from 'react';
import { toast } from 'react-toastify';

interface APIError {
  message: string;
  code: string;
  field?: string;
}

export const useErrorHandler = () => {
  const [errors, setErrors] = useState<APIError[]>([]);

  const handleError = useCallback((error: any) => {
    let apiErrors: APIError[] = [];

    if (error.response?.data) {
      const data = error.response.data;

      if (data.errors && Array.isArray(data.errors)) {
        apiErrors = data.errors.map((err: any) => ({
          message: err.message,
          code: err.code,
          field: err.field
        }));
      } else if (data.detail) {
        apiErrors = [{
          message: data.detail,
          code: data.error_code || 'UNKNOWN_ERROR'
        }];
      }
    } else if (error.message) {
      apiErrors = [{
        message: error.message,
        code: 'NETWORK_ERROR'
      }];
    } else {
      apiErrors = [{
        message: 'An unexpected error occurred',
        code: 'UNKNOWN_ERROR'
      }];
    }

    setErrors(apiErrors);

    // Show toast notification for critical errors
    if (apiErrors.some(err => err.code === 'NETWORK_ERROR' || err.code === 'SERVER_ERROR')) {
      toast.error('Service temporarily unavailable. Please try again.');
    }

    return apiErrors;
  }, []);

  const clearErrors = useCallback((field?: string) => {
    if (field) {
      setErrors(prev => prev.filter(err => err.field !== field));
    } else {
      setErrors([]);
    }
  }, []);

  const getFieldError = useCallback((field: string): string | null => {
    const fieldError = errors.find(err => err.field === field);
    return fieldError?.message || null;
  }, [errors]);

  return {
    errors,
    handleError,
    clearErrors,
    getFieldError
  };
};
```

## Performance Optimization

### React Query Integration
```typescript
// hooks/useAPIQuery.ts
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { predictionService, dashboardService } from '../services';

// Dashboard data with caching and background updates
export const useDashboardQuery = (orgId: string, filters = {}) => {
  return useQuery(
    ['dashboard', orgId, filters],
    () => dashboardService.getDashboardData(orgId, filters),
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: true,
      refetchInterval: 30 * 1000, // 30 seconds background refresh
      retry: 3,
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
    }
  );
};

// Individual prediction with optimistic updates
export const usePredictionMutation = () => {
  const queryClient = useQueryClient();

  return useMutation(predictionService.predictIndividual, {
    onMutate: async (surveyData) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries(['predictions']);

      // Snapshot the previous value
      const previousPredictions = queryClient.getQueryData(['predictions']);

      // Optimistically update with loading state
      queryClient.setQueryData(['predictions'], (old: any[]) => [
        ...old,
        { id: surveyData.responseId, status: 'loading' }
      ]);

      return { previousPredictions };
    },
    onError: (err, variables, context) => {
      // Rollback to previous state on error
      if (context?.previousPredictions) {
        queryClient.setQueryData(['predictions'], context.previousPredictions);
      }
    },
    onSuccess: (data) => {
      // Update cache with successful prediction
      queryClient.setQueryData(['predictions'], (old: any[]) =>
        old.map(p => p.id === data.response_id ? data : p)
      );

      // Invalidate related queries
      queryClient.invalidateQueries(['dashboard']);
    }
  });
};
```

### Component Lazy Loading
```typescript
// components/LazyComponents.tsx
import { lazy, Suspense } from 'react';
import { CircularProgress, Box } from '@mui/material';

// Lazy load heavy dashboard components
export const LazyDashboard = lazy(() => import('./dashboard/Dashboard'));
export const LazySurveyForm = lazy(() => import('./survey/SurveyForm'));
export const LazyAdminPanel = lazy(() => import('./admin/AdminPanel'));

// Loading fallback component
const LoadingFallback = () => (
  <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
    <CircularProgress />
  </Box>
);

// Wrapper with suspense
export const withSuspense = <P extends object>(
  Component: React.ComponentType<P>
) => (props: P) => (
  <Suspense fallback={<LoadingFallback />}>
    <Component {...props} />
  </Suspense>
);

// Usage in routing
export const SuspenseDashboard = withSuspense(LazyDashboard);
export const SuspenseSurveyForm = withSuspense(LazySurveyForm);
export const SuspenseAdminPanel = withSuspense(LazyAdminPanel);
```

This comprehensive integration guide provides the foundation for seamless frontend-backend communication in the Culture Score platform, ensuring optimal performance, user experience, and maintainability at enterprise scale.