import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  Container,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Box,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextField,
  Slider,
  Chip
} from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import './App.css';

// Prefer same-origin relative paths so CRA proxy (package.json "proxy") forwards to API during dev.
// Override with REACT_APP_API_URL to target a different host/port.
const API_BASE_URL = (process.env.REACT_APP_API_URL || '').replace(/\/$/, '');

function App() {
  const [surveyData, setSurveyData] = useState({
    domain: 'Business',
    survey_responses: Object.fromEntries(Array.from({ length: 22 }, (_, i) => [`q${i + 1}`, 3])),
    demographics: {
      age_range: '25-34',
      gender_identity: 'Prefer_not_to_say',
      position_level: 'Mid'
    },
    text_responses: {
      q23: 'Increase transparency in decision-making and follow-through on investigations.',
      q24: 'Workload spikes sometimes cause anxiety; support is inconsistent across teams.',
      q25: 'Strong peer collaboration and willingness to help new teammates.'
    }
  });

  const [prediction, setPrediction] = useState(null);
  const [textRiskResults, setTextRiskResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pipelineStatus, setPipelineStatus] = useState(null);
  const [health, setHealth] = useState(null);
  const [modelsInfo, setModelsInfo] = useState(null);

  // JSON prediction tool state
  const [jsonEndpoint, setJsonEndpoint] = useState('individual'); // 'individual' | 'organizational'
  const [jsonInput, setJsonInput] = useState('');
  const [jsonError, setJsonError] = useState(null);
  const [jsonResult, setJsonResult] = useState(null);
  const [jsonFileName, setJsonFileName] = useState('');
  const [jsonShowEditor, setJsonShowEditor] = useState(true);
  const [jsonShowRawResult, setJsonShowRawResult] = useState(false);

  // Text classification tool state
  const [textClassificationData, setTextClassificationData] = useState({
    q23: '',
    q24: '',
    q25: ''
  });
  const [textClassificationFiles, setTextClassificationFiles] = useState([]);
  const [textClassificationResult, setTextClassificationResult] = useState(null);
  const [textClassificationError, setTextClassificationError] = useState(null);
  const [textClassificationLoading, setTextClassificationLoading] = useState(false);
  const [textInputMethod, setTextInputMethod] = useState('manual'); // 'manual', 'file', 'sample'

  const questions = [
    "I feel safe speaking up about workplace issues",
    "Leadership encourages open communication",
    "I'm not afraid of consequences for reporting problems",
    "Domain-specific safety measures are adequate",
    "I receive fair treatment regardless of background",
    "Everyone has equal access to opportunities",
    "Workplace relationships are professional and respectful",
    "Management is transparent in decision making",
    "I feel valued and respected by colleagues",
    "Work expectations are reasonable and clear",
    "I have adequate resources to do my job well",
    "Feedback is constructive and helpful",
    "I'm included in important decisions that affect me",
    "The organization supports work-life balance",
    "I trust leadership to handle issues fairly",
    "I feel my voice is heard and valued",
    "Workplace policies are applied consistently",
    "I feel psychologically safe at work",
    "I can be authentic and true to myself here",
    "My mental health is supported by the organization",
    "I'm optimistic about my future here",
    "I would recommend this workplace to others"
  ];

  const handleQuestionChange = (questionIndex, value) => {
    setSurveyData(prev => ({
      ...prev,
      survey_responses: {
        ...prev.survey_responses,
        [`q${questionIndex + 1}`]: value
      }
    }));
  };

  const fillSampleInputs = (sampleType = 'default') => {
    const samples = {
      default: {
        responses: Object.fromEntries(Array.from({ length: 22 }, (_, i) => [`q${i + 1}`, 3])),
        textResponses: {
          q23: 'Improve accountability in handling reported issues; share outcomes clearly.',
          q24: 'Stress rises during deadlines; leadership communication sometimes adds pressure.',
          q25: 'We do peer mentoring very well and share knowledge openly.'
        },
        demographics: { age_range: '25-34', gender_identity: 'Prefer_not_to_say', position_level: 'Mid' }
      },
      high_risk: {
        responses: { q1: 1, q2: 1, q3: 1, q4: 2, q5: 1, q6: 2, q7: 1, q8: 2, q9: 1, q10: 2, q11: 1, q12: 1, q13: 1, q14: 2, q15: 1, q16: 1, q17: 1, q18: 2, q19: 1, q20: 1, q21: 1, q22: 2 },
        textResponses: {
          q23: 'Management needs to stop the harassment and retaliation. People are afraid to speak up because of consequences.',
          q24: 'Work is causing me severe anxiety and panic attacks. The toxic environment is destroying my mental health.',
          q25: 'There are no real strengths. The workplace culture is hostile and unsupportive.'
        },
        demographics: { age_range: '35-44', gender_identity: 'Woman', position_level: 'Entry' }
      },
      positive: {
        responses: Object.fromEntries(Array.from({ length: 22 }, (_, i) => [`q${i + 1}`, 4])),
        textResponses: {
          q23: 'Continue the excellent leadership development and transparent communication practices.',
          q24: 'Work is challenging but rewarding. Great support systems help maintain work-life balance.',
          q25: 'Outstanding team collaboration, supportive management, and genuine care for employee wellbeing.'
        },
        demographics: { age_range: '25-34', gender_identity: 'Non_binary', position_level: 'Senior' }
      }
    };

    const selectedSample = samples[sampleType];
    // Add some variation to default sample
    if (sampleType === 'default') {
      selectedSample.responses.q3 = 2;
      selectedSample.responses.q11 = 2;
      selectedSample.responses.q21 = 2;
      selectedSample.responses.q15 = 2;
      selectedSample.responses.q9 = 2;
    }

    setSurveyData(prev => ({
      ...prev,
      survey_responses: selectedSample.responses,
      text_responses: selectedSample.textResponses,
      demographics: selectedSample.demographics
    }));
  };

  // JSON sample data functions
  const loadJsonSample = (sampleType) => {
    const samples = {
      individual_high_risk: {
        response_id: "sample_001",
        domain: "Healthcare",
        survey_responses: { q1: 1, q2: 1, q3: 1, q4: 2, q5: 1, q6: 2, q7: 1, q8: 2, q9: 1, q10: 2, q11: 1, q12: 1, q13: 1, q14: 2, q15: 1, q16: 1, q17: 1, q18: 2, q19: 1, q20: 1, q21: 1, q22: 2 },
        demographics: { age_range: "35-44", gender_identity: "Woman", position_level: "Entry" },
        text_responses: {
          q23: "Need to address the hostile work environment and harassment from supervisors immediately.",
          q24: "Experiencing severe anxiety and panic attacks due to workplace stress and toxic culture.",
          q25: "No real strengths. Management protects perpetrators and ignores victim complaints."
        }
      },
      individual_positive: {
        response_id: "sample_002",
        domain: "Business",
        survey_responses: Object.fromEntries(Array.from({ length: 22 }, (_, i) => [`q${i + 1}`, 4])),
        demographics: { age_range: "25-34", gender_identity: "Non_binary", position_level: "Senior" },
        text_responses: {
          q23: "Continue excellent transparent leadership and employee development programs.",
          q24: "Work is challenging but rewarding with great support systems and work-life balance.",
          q25: "Outstanding collaboration, supportive management, genuine care for employee wellbeing."
        }
      },
      organizational: {
        organization_info: {
          org_id: "org_sample_001",
          org_name: "Sample Healthcare System",
          domain: "Healthcare",
          employee_count: 1250
        },
        individual_responses: [
          { response_id: "emp_001", overall_hseg_score: 8.5, overall_risk_tier: "Crisis", category_scores: {1: 1.2, 2: 1.8, 3: 2.1, 4: 1.5, 5: 1.3, 6: 1.6} },
          { response_id: "emp_002", overall_hseg_score: 15.2, overall_risk_tier: "At_Risk", category_scores: {1: 2.3, 2: 2.8, 3: 2.9, 4: 2.1, 5: 2.7, 6: 2.4} },
          { response_id: "emp_003", overall_hseg_score: 22.1, overall_risk_tier: "Safe", category_scores: {1: 3.4, 2: 3.8, 3: 3.6, 4: 3.9, 5: 3.7, 6: 3.7} }
        ]
      }
    };

    setJsonInput(JSON.stringify(samples[sampleType], null, 2));
    setJsonShowEditor(true);
  };

  const resetInputs = () => {
    setSurveyData({
      domain: 'Business',
      survey_responses: Object.fromEntries(Array.from({ length: 22 }, (_, i) => [`q${i + 1}`, 3])),
      demographics: {
        age_range: '25-34',
        gender_identity: 'Prefer_not_to_say',
        position_level: 'Mid'
      },
      text_responses: {
        q23: 'Increase transparency in decision-making and follow-through on investigations.',
        q24: 'Workload spikes sometimes cause anxiety; support is inconsistent across teams.',
        q25: 'Strong peer collaboration and willingness to help new teammates.'
      }
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setPrediction(null);
    setTextRiskResults(null);

    try {
      // Step 1: Get individual prediction (Q1-Q22 + demographics)
      const individualResponse = await axios.post(`${API_BASE_URL}/predict/individual`, surveyData);
      setPrediction(individualResponse.data);

      // Step 2: Get text classification for Q23-Q25
      const combinedText = [
        surveyData.text_responses.q23,
        surveyData.text_responses.q24,
        surveyData.text_responses.q25
      ].filter(t => t && t.trim()).join(' ');

      if (combinedText.trim()) {
        // Create FormData for text classification API
        const formData = new FormData();
        const textBlob = new Blob([combinedText], { type: 'text/plain' });
        formData.append('file', textBlob, 'survey_text_responses.txt');

        const textResponse = await fetch(`${API_BASE_URL}/predict/communication_risk`, {
          method: 'POST',
          headers: {
            'Authorization': 'Bearer test-token',
          },
          body: formData,
        });

        if (textResponse.ok) {
          const textResults = await textResponse.json();
          setTextRiskResults(textResults);
        }
      }
    } catch (error) {
      console.error('Prediction failed:', error);
      const detail = error.response?.data?.detail || error.response?.data?.error || error.message;
      setError(detail || 'Prediction failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const refreshStatus = async () => {
    try {
      const [statusRes, healthRes, modelsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/pipeline/status`),
        axios.get(`${API_BASE_URL}/health`),
        axios.get(`${API_BASE_URL}/models/info`)
      ]);
      setPipelineStatus(statusRes.data);
      setHealth(healthRes.data);
      setModelsInfo(modelsRes.data);
    } catch (e) {
      // Non-fatal for UI
    }
  };

  useEffect(() => {
    refreshStatus();
  }, []);

  const handleJsonFile = async (e) => {
    setJsonError(null);
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.json')) {
      setJsonError('Please upload a .json file');
      return;
    }
    try {
      const text = await file.text();
      // Basic validation
      JSON.parse(text);
      setJsonInput(text);
    } catch (err) {
      setJsonError('Invalid JSON file');
    }
  };

  const submitJsonPrediction = async () => {
    setJsonError(null);
    setJsonResult(null);
    let payload = null;
    try {
      payload = JSON.parse(jsonInput);
    } catch (e) {
      setJsonError('Please enter valid JSON');
      return;
    }
    try {
      const url = jsonEndpoint === 'individual'
        ? `${API_BASE_URL}/predict/individual`
        : `${API_BASE_URL}/predict/organizational`;
      const res = await axios.post(url, payload);
      setJsonResult(res.data);
    } catch (e) {
      const msg = e.response?.data?.detail || e.message || 'Prediction failed';
      setJsonError(msg);
    }
  };

  // Text classification functions
  const loadSampleTextResponses = (sampleType) => {
    const samples = {
      harassment: {
        q23: "Management needs to address the hostile work environment and inappropriate behavior from supervisors. There should be better reporting mechanisms.",
        q24: "The constant harassment has caused me severe anxiety and panic attacks. I'm having trouble sleeping and my mental health is deteriorating.",
        q25: "Some colleagues are supportive, but many are afraid to speak up due to fear of retaliation from management."
      },
      crisis: {
        q23: "The workplace needs immediate intervention. The toxic culture and lack of accountability is pushing people to their breaking point.",
        q24: "I'm experiencing thoughts of self-harm due to workplace stress. The constant pressure and public humiliation have destroyed my confidence.",
        q25: "There's no real support system. People are struggling but management doesn't care about employee wellbeing."
      },
      positive: {
        q23: "Continue fostering the open communication culture and transparent decision-making processes that we have now.",
        q24: "Work is challenging but manageable. The support from leadership and colleagues helps maintain good mental health.",
        q25: "Great team collaboration, excellent work-life balance, and leadership that genuinely cares about employee development."
      }
    };
    setTextClassificationData(samples[sampleType]);
    setTextInputMethod('manual');
  };

  const handleTextClassificationFiles = async (e) => {
    setTextClassificationError(null);
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    const processedFiles = [];
    for (const file of files) {
      try {
        let content = '';
        if (file.type === 'application/json' || file.name.endsWith('.json')) {
          const text = await file.text();
          const jsonData = JSON.parse(text);
          // Extract Q23, Q24, Q25 from JSON
          content = {
            q23: jsonData.text_responses?.q23 || jsonData.q23 || '',
            q24: jsonData.text_responses?.q24 || jsonData.q24 || '',
            q25: jsonData.text_responses?.q25 || jsonData.q25 || ''
          };
        } else if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
          const text = await file.text();
          // Assume single text applies to all three questions
          content = { q23: text, q24: '', q25: '' };
        } else {
          throw new Error('Unsupported file type. Please upload .txt, .json, or .pdf files');
        }
        processedFiles.push({ name: file.name, content });
      } catch (err) {
        setTextClassificationError(`Error processing ${file.name}: ${err.message}`);
        return;
      }
    }

    setTextClassificationFiles(processedFiles);
    if (processedFiles.length === 1) {
      setTextClassificationData(processedFiles[0].content);
    }
    setTextInputMethod('file');
  };

  const submitTextClassification = async () => {
    setTextClassificationLoading(true);
    setTextClassificationError(null);
    setTextClassificationResult(null);

    try {
      let textToAnalyze = '';

      if (textInputMethod === 'file' && textClassificationFiles.length > 0) {
        // Process multiple files or single file
        const allTexts = textClassificationFiles.map(file =>
          [file.content.q23, file.content.q24, file.content.q25].filter(t => t.trim()).join(' ')
        );
        textToAnalyze = allTexts.join(' ');
      } else {
        // Manual input - combine Q23, Q24, Q25
        textToAnalyze = [
          textClassificationData.q23,
          textClassificationData.q24,
          textClassificationData.q25
        ].filter(t => t.trim()).join(' ');
      }

      if (!textToAnalyze.trim()) {
        setTextClassificationError('Please provide text content to analyze');
        return;
      }

      // Create FormData for API call
      const formData = new FormData();
      const textBlob = new Blob([textToAnalyze], { type: 'text/plain' });
      formData.append('file', textBlob, 'combined_responses.txt');

      const response = await fetch(`${API_BASE_URL}/predict/communication_risk`, {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer test-token',
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || errorData.error || 'Text classification failed');
      }

      const result = await response.json();
      setTextClassificationResult(result);
    } catch (err) {
      setTextClassificationError(err.message);
    } finally {
      setTextClassificationLoading(false);
    }
  };

  const getRiskColor = (tier) => {
    const colors = {
      'Crisis': '#d32f2f',
      'At_Risk': '#f57c00',
      'Mixed': '#fbc02d',
      'Safe': '#388e3c',
      'Thriving': '#1976d2'
    };
    return colors[tier] || '#757575';
  };

  const prepareChartData = () => {
    if (!prediction?.category_scores) return [];

    return Object.entries(prediction.category_scores).map(([category, score]) => ({
      category: labelForCategory(category),
      score: parseFloat(score),
      fullScore: 4.0
    }));
  };

  const prepareChartDataFromResult = (res) => {
    if (!res) return [];
    if (res.category_scores) {
      return Object.entries(res.category_scores).map(([category, score]) => ({
        category: labelForCategory(category),
        score: parseFloat(score),
        fullScore: 4.0
      }));
    }
    if (res.category_breakdown) {
      return Object.entries(res.category_breakdown).map(([category, obj]) => ({
        category: labelForCategory(category),
        score: parseFloat(obj?.score ?? 0),
        fullScore: 4.0
      }));
    }
    return [];
  };

  const prepareRiskDistribution = (res) => {
    const dist = res?.risk_indicators?.risk_distribution || {};
    return Object.entries(dist)
      .filter(([_, v]) => v > 0)
      .map(([tier, pct]) => ({ name: tier, value: pct * 100 }));
  };

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1>🏢 Blucentia Culture Intelligence Platform</h1>
        <p>Advanced AI-Powered Psychological Safety Assessment</p>
      </div>

      <Container maxWidth="xl" className="main-container">

      <Grid container spacing={4}>
        {/* JSON Prediction Tool */}
        <Grid item xs={12} className="tools-section">
          <Paper elevation={2} sx={{ p: 2.5 }} className="enterprise-card">
            <Typography variant="h5" gutterBottom className="section-header">JSON Prediction Tool</Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              Paste JSON or upload a .json file, then select an endpoint to predict.
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={8}>
                {(!jsonShowEditor && jsonFileName) ? (
                  <Alert severity="success" sx={{ mb: 2 }}>
                    Loaded "{jsonFileName}" successfully.
                  </Alert>
                ) : (
                  <TextField
                    label="JSON Request Body"
                    placeholder="Paste JSON here..."
                    value={jsonInput}
                    onChange={(e) => setJsonInput(e.target.value)}
                    multiline
                    minRows={4}
                    maxRows={8}
                    fullWidth
                    className="json-input-field"
                    size="small"
                  />
                )}
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Endpoint</InputLabel>
                  <Select
                    value={jsonEndpoint}
                    label="Endpoint"
                    onChange={(e) => setJsonEndpoint(e.target.value)}
                  >
                    <MenuItem value="individual">/predict/individual</MenuItem>
                    <MenuItem value="organizational">/predict/organizational</MenuItem>
                  </Select>
                </FormControl>
                <Button variant="outlined" component="label" fullWidth sx={{ mb: 1 }}>
                  Upload .json File
                  <input hidden type="file" accept="application/json,.json" onChange={handleJsonFile} />
                </Button>
                <Box display="flex" gap={1} sx={{ mb: 1 }}>
                  <Button variant="text" onClick={() => setJsonShowEditor(v => !v)}>
                    {jsonShowEditor ? 'Hide JSON' : 'Show JSON'}
                  </Button>
                  <Button variant="text" color="secondary" onClick={() => { setJsonInput(''); setJsonFileName(''); setJsonShowEditor(true); }}>
                    Clear JSON
                  </Button>
                </Box>

                {/* Sample Data Options */}
                <Typography variant="subtitle2" sx={{ mb: 1, mt: 2 }}>Sample Data:</Typography>
                <Box display="flex" gap={1} flexWrap="wrap" sx={{ mb: 2 }}>
                  {jsonEndpoint === 'individual' && (
                    <>
                      <Button onClick={() => loadJsonSample('individual_high_risk')} variant="text" size="small" color="error">
                        High Risk Individual
                      </Button>
                      <Button onClick={() => loadJsonSample('individual_positive')} variant="text" size="small" color="success">
                        Positive Individual
                      </Button>
                    </>
                  )}
                  {jsonEndpoint === 'organizational' && (
                    <Button onClick={() => loadJsonSample('organizational')} variant="text" size="small" color="primary">
                      Organization Sample
                    </Button>
                  )}
                </Box>

                <Button variant="contained" onClick={submitJsonPrediction} fullWidth>
                  Predict from JSON
                </Button>
              </Grid>
            </Grid>
            {jsonError && (
              <Alert severity="error" sx={{ mt: 2 }}>{jsonError}</Alert>
            )}
            {jsonResult && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle1" gutterBottom>Prediction Summary</Typography>

                {/* Individual summary */}
                {jsonEndpoint === 'individual' && jsonResult.overall_hseg_score !== undefined && (
                  <Box>
                    <Card sx={{ mb: 2, bgcolor: getRiskColor(jsonResult.overall_risk_tier), color: 'white' }}>
                      <CardContent>
                        <Typography variant="h5">{jsonResult.overall_risk_tier}</Typography>
                        <Typography variant="body1">HSEG Score: {jsonResult.overall_hseg_score}/28</Typography>
                        {jsonResult.confidence_score !== undefined && (
                          <Typography variant="body2">Confidence: {(jsonResult.confidence_score * 100).toFixed(1)}%</Typography>
                        )}
                      </CardContent>
                    </Card>

                    {/* Category chart */}
                    <Box sx={{ mb: 2, maxWidth: 520, mx: 'auto' }}>
                      <Typography variant="subtitle1">Category Breakdown</Typography>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={prepareChartDataFromResult(jsonResult)}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="category" />
                          <YAxis domain={[0, 4]} />
                          <Tooltip />
                          <Bar dataKey="score" fill="#1976d2" />
                        </BarChart>
                      </ResponsiveContainer>
                    </Box>

                    {/* Contributing factors */}
                    {Array.isArray(jsonResult.contributing_factors) && jsonResult.contributing_factors.length > 0 && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle1">Key Risk Factors</Typography>
                        {jsonResult.contributing_factors.map((f, i) => (
                          <Chip key={i} label={f} color="warning" sx={{ mr: 1, mb: 1 }} />
                        ))}
                      </Box>
                    )}

                    {/* Interventions */}
                    {Array.isArray(jsonResult.recommended_interventions) && jsonResult.recommended_interventions.length > 0 && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle1">Recommended Actions</Typography>
                        {jsonResult.recommended_interventions.map((it, i) => (
                          <Alert key={i} severity="info" sx={{ mb: 1 }}>
                            <strong>{it.category}:</strong> {it.intervention}
                          </Alert>
                        ))}
                      </Box>
                    )}

                    {/* Text risk */}
                    {jsonResult.text_risk_analysis && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle1">Text Risk Analysis</Typography>
                        <Alert severity={jsonResult.text_risk_analysis.crisis_detection?.has_crisis_language ? 'error' : 'info'}>
                          Overall Text Risk: {jsonResult.text_risk_analysis.overall_risk_level || 'N/A'}
                        </Alert>
                      </Box>
                    )}
                  </Box>
                )}

                {/* Organizational summary */}
                {jsonEndpoint === 'organizational' && jsonResult.overall_assessment && (
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
                      <Button variant="outlined" size="small" onClick={() => window.print()}>Export PDF</Button>
                    </Box>
                    {/* Organizational Executive Narrative */}
                    <Box id="org-pdf-summary" sx={{ mb: 2 }}>
                      <Typography variant="h6" className="section-header">Executive Summary</Typography>
                      <Typography variant="body2" color="textSecondary">
                        {(() => {
                          const oa = jsonResult.overall_assessment || {};
                          const score = Number(oa.average_hseg_score ?? 0).toFixed(1);
                          const tier = oa.overall_risk_tier || 'Unknown';
                          const dist = jsonResult.risk_indicators?.risk_distribution || {};
                          const topTier = Object.entries(dist).sort((a,b)=>b[1]-a[1])[0];
                          const topTierText = topTier ? `${topTier[0]} ${(topTier[1]*100).toFixed(1)}%` : 'N/A';
                          const turnover = oa.predicted_turnover_rate != null ? `${(oa.predicted_turnover_rate*100).toFixed(1)}%` : 'N/A';
                          const actions = Array.isArray(jsonResult.intervention_recommendations) ? jsonResult.intervention_recommendations.slice(0,2) : [];
                          const actionText = actions.length ? actions.map(a => `${a.category.replace('_',' ')}: ${a.intervention}`).join('; ') : 'Maintain current practices; monitor key drivers.';
                          return `Overall ${tier} (${score}/28). Risk distribution led by ${topTierText}. Predicted turnover ~${turnover}. Priority actions: ${actionText}`;
                        })()}
                      </Typography>
                    </Box>
                    <Card sx={{ mb: 2, bgcolor: getRiskColor(jsonResult.overall_assessment.overall_risk_tier), color: 'white' }}>
                      <CardContent>
                        <Typography variant="h5">{jsonResult.overall_assessment.overall_risk_tier}</Typography>
                        <Typography variant="body1">Average HSEG Score: {jsonResult.overall_assessment.average_hseg_score}/28</Typography>
                        {jsonResult.overall_assessment.predicted_turnover_rate !== undefined && (
                          <Typography variant="body2">Predicted Turnover: {(jsonResult.overall_assessment.predicted_turnover_rate * 100).toFixed(1)}%</Typography>
                        )}
                        {jsonResult.overall_assessment.total_responses !== undefined && (
                          <Typography variant="body2">Responses Analyzed: {jsonResult.overall_assessment.total_responses}</Typography>
                        )}
                      </CardContent>
                    </Card>

                    {/* KPI Tiles */}
                    <Grid container spacing={2} sx={{ mb: 2 }}>
                      <Grid item xs={12} sm={6} md={3}>
                        <Paper className="enterprise-card" sx={{ p: 2, textAlign: 'center' }}>
                          <Typography variant="subtitle2" className="muted-text">Overall Score</Typography>
                          <Typography variant="h5">{Number(jsonResult.overall_assessment.average_hseg_score || 0).toFixed(1)}</Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <Paper className="enterprise-card" sx={{ p: 2, textAlign: 'center' }}>
                          <Typography variant="subtitle2" className="muted-text">Risk Tier</Typography>
                          <Typography variant="h6">{jsonResult.overall_assessment.overall_risk_tier}</Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <Paper className="enterprise-card" sx={{ p: 2, textAlign: 'center' }}>
                          <Typography variant="subtitle2" className="muted-text">Predicted Turnover</Typography>
                          <Typography variant="h6">{jsonResult.overall_assessment.predicted_turnover_rate != null ? `${(jsonResult.overall_assessment.predicted_turnover_rate*100).toFixed(1)}%` : 'N/A'}</Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <Paper className="enterprise-card" sx={{ p: 2, textAlign: 'center' }}>
                          <Typography variant="subtitle2" className="muted-text">Responses</Typography>
                          <Typography variant="h6">{jsonResult.overall_assessment.total_responses || 'N/A'}</Typography>
                        </Paper>
                      </Grid>
                    </Grid>

                    {/* Category chart */}
                    <Box sx={{ mb: 2, maxWidth: 520, mx: 'auto' }}>
                      <Typography variant="subtitle1">Category Breakdown</Typography>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={prepareChartDataFromResult(jsonResult)}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="category" />
                          <YAxis domain={[0, 4]} />
                          <Tooltip />
                          <Bar dataKey="score" fill="#1976d2" />
                        </BarChart>
                      </ResponsiveContainer>
                    </Box>

                    {/* Risk distribution pie */}
                    {jsonResult.risk_indicators?.risk_distribution && (
                      <Box sx={{ mb: 2, maxWidth: 520, mx: 'auto' }}>
                        <Typography variant="subtitle1">Risk Distribution</Typography>
                        <ResponsiveContainer width="100%" height={300}>
                          <PieChart>
                            <Pie data={prepareRiskDistribution(jsonResult)} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2}>
                              {prepareRiskDistribution(jsonResult).map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={getRiskColor(entry.name)} />
                              ))}
                            </Pie>
                            <Tooltip formatter={(v, n)=> [`${Number(v).toFixed(1)}%`, n]} />
                          </PieChart>
                        </ResponsiveContainer>
                      </Box>
                    )}

                    {/* Risk distribution chips */}
                    {jsonResult.risk_indicators?.risk_distribution && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle1">Risk Distribution</Typography>
                        <Box>
                          {Object.entries(jsonResult.risk_indicators.risk_distribution).map(([tier, pct]) => (
                            <Chip key={tier} label={`${tier}: ${(pct * 100).toFixed(1)}%`} sx={{ mr: 1, mb: 1 }} />
                          ))}
                        </Box>
                      </Box>
                    )}

                    {/* Top actions */}
                    {Array.isArray(jsonResult.intervention_recommendations) && jsonResult.intervention_recommendations.length > 0 && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle1">Top Priority Actions</Typography>
                        {jsonResult.intervention_recommendations.slice(0,3).map((it, i) => (
                          <Alert key={i} severity="info" sx={{ mb: 1 }}>
                            <strong>{it.category}:</strong> {it.intervention} — Urgency: {it.urgency}
                          </Alert>
                        ))}
                      </Box>
                    )}
                  </Box>
                )}

                {/* Toggle raw JSON if needed */}
                <Box sx={{ mt: 1 }}>
                  <Button variant="text" size="small" onClick={() => setJsonShowRawResult(v => !v)}>
                    {jsonShowRawResult ? 'Hide Raw JSON' : 'Show Raw JSON'}
                  </Button>
                </Box>
                {jsonShowRawResult && (
                  <Paper variant="outlined" sx={{ p: 2, maxHeight: 300, overflow: 'auto', bgcolor: '#0a0a0a0a', mt: 1 }}>
                    <pre style={{ margin: 0 }}>{JSON.stringify(jsonResult, null, 2)}</pre>
                  </Paper>
                )}
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Text Classification Tool */}
        <Grid item xs={12} className="tools-section">
          <Paper elevation={2} sx={{ p: 2.5 }} className="enterprise-card">
            <Typography variant="h5" gutterBottom className="section-header">
              Text Classification Tool
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              Analyze workplace feedback text responses using Zero-Shot Classification. Upload files or enter responses manually.
            </Typography>

            {/* Input Method Selection */}
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>Input Method:</Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                <Button
                  variant={textInputMethod === 'manual' ? 'contained' : 'outlined'}
                  size="small"
                  onClick={() => setTextInputMethod('manual')}
                >
                  Manual Input
                </Button>
                <Button
                  variant={textInputMethod === 'file' ? 'contained' : 'outlined'}
                  size="small"
                  onClick={() => setTextInputMethod('file')}
                >
                  File Upload
                </Button>
                <Button
                  variant={textInputMethod === 'sample' ? 'contained' : 'outlined'}
                  size="small"
                  onClick={() => setTextInputMethod('sample')}
                >
                  Sample Data
                </Button>
              </Box>
            </Box>

            <Grid container spacing={2}>
              <Grid item xs={12} md={8}>
                {/* Sample Data Selection */}
                {textInputMethod === 'sample' && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>Choose Sample:</Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      <Button
                        variant="contained"
                        color="error"
                        size="small"
                        onClick={() => loadSampleTextResponses('harassment')}
                      >
                        🚨 Workplace Harassment
                      </Button>
                      <Button
                        variant="contained"
                        color="secondary"
                        size="small"
                        onClick={() => loadSampleTextResponses('crisis')}
                      >
                        ⚠️ Mental Health Crisis
                      </Button>
                      <Button
                        variant="contained"
                        color="success"
                        size="small"
                        onClick={() => loadSampleTextResponses('positive')}
                      >
                        ✅ Positive Feedback
                      </Button>
                    </Box>
                  </Box>
                )}

                {/* Manual Input */}
                {(textInputMethod === 'manual' || textInputMethod === 'sample') && (
                  <Box>
                    <TextField
                      fullWidth
                      multiline
                      minRows={2}
                      maxRows={4}
                      label="Q23: What would you change about your workplace?"
                      value={textClassificationData.q23}
                      onChange={(e) => setTextClassificationData({
                        ...textClassificationData,
                        q23: e.target.value
                      })}
                      className="text-classification-input"
                      size="small"
                      sx={{ mb: 2 }}
                    />
                    <TextField
                      fullWidth
                      multiline
                      minRows={2}
                      maxRows={4}
                      label="Q24: How does work impact your mental health?"
                      value={textClassificationData.q24}
                      onChange={(e) => setTextClassificationData({
                        ...textClassificationData,
                        q24: e.target.value
                      })}
                      className="text-classification-input"
                      size="small"
                      sx={{ mb: 2 }}
                    />
                    <TextField
                      fullWidth
                      multiline
                      minRows={2}
                      maxRows={4}
                      label="Q25: What does your workplace do well?"
                      value={textClassificationData.q25}
                      onChange={(e) => setTextClassificationData({
                        ...textClassificationData,
                        q25: e.target.value
                      })}
                      className="text-classification-input"
                      size="small"
                      sx={{ mb: 2 }}
                    />
                  </Box>
                )}

                {/* File Upload */}
                {textInputMethod === 'file' && (
                  <Box>
                    <Button variant="outlined" component="label" fullWidth sx={{ mb: 2 }}>
                      Upload Files (.txt, .json, .pdf)
                      <input
                        hidden
                        type="file"
                        multiple
                        accept=".txt,.json,.pdf,application/json,text/plain"
                        onChange={handleTextClassificationFiles}
                      />
                    </Button>
                    {textClassificationFiles.length > 0 && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2">Uploaded Files:</Typography>
                        {textClassificationFiles.map((file, index) => (
                          <Chip
                            key={index}
                            label={`${file.name} (${Object.values(file.content).filter(t => t.trim()).length} fields)`}
                            color="primary"
                            size="small"
                            sx={{ mr: 1, mb: 1 }}
                          />
                        ))}
                      </Box>
                    )}
                  </Box>
                )}

                {/* Error Display */}
                {textClassificationError && (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {textClassificationError}
                  </Alert>
                )}

                {/* Results Display */}
                {textClassificationResult && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="h6" gutterBottom>Classification Results</Typography>

                    {/* Processing Info */}
                    <Box sx={{ mb: 2, p: 1, bgcolor: '#f5f5f5', borderRadius: 1 }}>
                      <Typography variant="caption" color="textSecondary">
                        Model: {textClassificationResult.model_name} |
                        Processing Time: {textClassificationResult.processing_time_ms?.toFixed(0)}ms
                      </Typography>
                    </Box>

                    {/* HSEG Risk Analysis */}
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle1" gutterBottom color="error">
                        🏢 Organizational Risk Categories (HSEG Framework)
                      </Typography>
                      {textClassificationResult.hseg_risk_analysis?.map((risk, index) => (
                        <Box key={index} sx={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          p: 1,
                          mb: 1,
                          bgcolor: '#f8f9fa',
                          borderRadius: 1,
                          borderLeft: `4px solid ${risk.score >= 0.7 ? '#d32f2f' : risk.score >= 0.5 ? '#ff9800' : '#4caf50'}`
                        }}>
                          <Typography variant="body2">
                            <strong>{risk.label}</strong>
                          </Typography>
                          <Chip
                            label={`${(risk.score * 100).toFixed(1)}%`}
                            color={risk.score >= 0.7 ? 'error' : risk.score >= 0.5 ? 'warning' : 'success'}
                            size="small"
                          />
                        </Box>
                      ))}
                    </Box>

                    {/* Individual Distress Analysis */}
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle1" gutterBottom color="secondary">
                        👤 Individual Distress Assessment
                      </Typography>
                      {textClassificationResult.individual_distress_analysis?.map((distress, index) => (
                        <Box key={index} sx={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          p: 1,
                          mb: 1,
                          bgcolor: '#f8f9fa',
                          borderRadius: 1,
                          borderLeft: `4px solid ${distress.score >= 0.7 ? '#d32f2f' : distress.score >= 0.5 ? '#ff9800' : '#4caf50'}`
                        }}>
                          <Typography variant="body2">
                            <strong>{distress.label}</strong>
                          </Typography>
                          <Chip
                            label={`${(distress.score * 100).toFixed(1)}%`}
                            color={distress.score >= 0.7 ? 'error' : distress.score >= 0.5 ? 'warning' : 'success'}
                            size="small"
                          />
                        </Box>
                      ))}
                    </Box>

                    {/* Crisis Alert */}
                    {textClassificationResult.individual_distress_analysis?.find(d =>
                      d.label.includes('self-harm') && d.score > 0.5
                    ) && (
                      <Alert severity="error" sx={{ mb: 2 }}>
                        <strong>⚠️ CRISIS ALERT ⚠️</strong><br />
                        High probability of self-harm ideation detected. Immediate intervention recommended.
                      </Alert>
                    )}
                  </Box>
                )}
              </Grid>

              <Grid item xs={12} md={4}>
                <Box>
                  <Typography variant="subtitle2" gutterBottom>Analysis Options:</Typography>
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Analysis Type</InputLabel>
                    <Select value="communication_risk" label="Analysis Type">
                      <MenuItem value="communication_risk">Communication Risk (Zero-Shot)</MenuItem>
                    </Select>
                  </FormControl>

                  <Button
                    variant="contained"
                    fullWidth
                    onClick={submitTextClassification}
                    disabled={textClassificationLoading}
                    sx={{ mb: 2 }}
                  >
                    {textClassificationLoading ? (
                      <>
                        <CircularProgress size={16} sx={{ mr: 1 }} />
                        Analyzing...
                      </>
                    ) : (
                      '🔍 Classify Text'
                    )}
                  </Button>

                  <Button
                    variant="text"
                    fullWidth
                    onClick={() => {
                      setTextClassificationData({ q23: '', q24: '', q25: '' });
                      setTextClassificationFiles([]);
                      setTextClassificationResult(null);
                      setTextClassificationError(null);
                    }}
                  >
                    Clear All
                  </Button>

                  {/* Info Box */}
                  <Box sx={{ mt: 2, p: 2, bgcolor: '#e3f2fd', borderRadius: 1 }}>
                    <Typography variant="caption">
                      <strong>How it works:</strong><br />
                      • Combines Q23, Q24, Q25 responses<br />
                      • Uses Facebook BART-large-mnli model<br />
                      • Two-step analysis: Organizational + Individual<br />
                      • Real-time zero-shot classification
                    </Typography>
                  </Box>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* System Status */}
        <Grid item xs={12}>
          <Paper elevation={1} sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }} className="enterprise-card">
            <Box>
              <Typography variant="subtitle1">
                Pipeline: {pipelineStatus?.pipeline_ready ? 'Ready' : 'Initializing'}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Models loaded: {pipelineStatus?.models_loaded ? 'Yes' : 'No'} | Version: {pipelineStatus?.model_version}
              </Typography>
            </Box>
            <Box textAlign="right">
              <Typography variant="body2" color="textSecondary">
                API Health: {health?.status || 'unknown'}
              </Typography>
              <Button size="small" onClick={refreshStatus} sx={{ mt: 1 }} variant="outlined">Refresh Status</Button>
            </Box>
          </Paper>
        </Grid>
        {/* Models Info */}
        <Grid item xs={12}>
          <Paper elevation={1} sx={{ p: 2 }} className="enterprise-card">
            <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="h6" className="section-header">Models</Typography>
              <Button size="small" variant="contained" color="secondary" onClick={async () => {
                try {
                  await axios.post(`${API_BASE_URL}/models/reload`, {}, { headers: { Authorization: 'Bearer test-token' } });
                  await refreshStatus();
                } catch (e) {}
              }}>Reload Models</Button>
            </Box>
            <Typography variant="body2" color="textSecondary">
              Version: {modelsInfo?.model_version}
            </Typography>
            <Box sx={{ mt: 1 }}>
              <Typography variant="body2">Individual: {modelsInfo?.model_info?.individual?.is_trained ? 'Trained' : 'Not trained'}</Typography>
              <Typography variant="body2">Text: {modelsInfo?.model_info?.text?.is_trained ? 'Trained' : 'Rule-based/Checkpoint missing'}</Typography>
              <Typography variant="body2">Organizational: {modelsInfo?.model_info?.organizational?.is_loaded ? 'Loaded' : 'Not loaded'}</Typography>
            </Box>
          </Paper>
        </Grid>
        {/* Survey Form */}
        <Grid item xs={12} md={6} className="tools-section">
          <Paper elevation={3} sx={{ p: 2.5 }} className="enterprise-card playground-section">
            <Typography variant="h5" gutterBottom className="section-header">
              Survey Playground
            </Typography>

            <form onSubmit={handleSubmit}>
              {/* Basic Information */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>Basic Information</Typography>

                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Domain</InputLabel>
                  <Select
                    value={surveyData.domain}
                    label="Domain"
                    onChange={(e) => setSurveyData({...surveyData, domain: e.target.value})}
                  >
                    <MenuItem value="Business">Business</MenuItem>
                    <MenuItem value="Healthcare">Healthcare</MenuItem>
                    <MenuItem value="University">University</MenuItem>
                  </Select>
                </FormControl>

                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Age Range</InputLabel>
                  <Select
                    value={surveyData.demographics.age_range}
                    label="Age Range"
                    onChange={(e) => setSurveyData({
                      ...surveyData,
                      demographics: {...surveyData.demographics, age_range: e.target.value}
                    })}
                  >
                    <MenuItem value="18-24">18-24</MenuItem>
                    <MenuItem value="25-34">25-34</MenuItem>
                    <MenuItem value="35-44">35-44</MenuItem>
                    <MenuItem value="45-54">45-54</MenuItem>
                    <MenuItem value="55+">55+</MenuItem>
                  </Select>
                </FormControl>

                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Position Level</InputLabel>
                  <Select
                    value={surveyData.demographics.position_level}
                    label="Position Level"
                    onChange={(e) => setSurveyData({
                      ...surveyData,
                      demographics: {...surveyData.demographics, position_level: e.target.value}
                    })}
                  >
                    <MenuItem value="Entry">Entry Level</MenuItem>
                    <MenuItem value="Mid">Mid Level</MenuItem>
                    <MenuItem value="Senior">Senior Level</MenuItem>
                    <MenuItem value="Executive">Executive</MenuItem>
                  </Select>
                </FormControl>
              </Box>

              {/* Survey Questions */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Survey Questions (Rate 1-4: Strongly Disagree to Strongly Agree)
                </Typography>

                {questions.map((question, index) => (
                  <Box key={index} sx={{ mb: 3 }}>
                    <Typography variant="body2" gutterBottom>
                      {index + 1}. {question}
                    </Typography>
                    <Slider
                      value={surveyData.survey_responses[`q${index + 1}`] || 2.5}
                      onChange={(e, value) => handleQuestionChange(index, value)}
                      min={1}
                      max={4}
                      step={1}
                      marks={[
                        { value: 1, label: '1' },
                        { value: 2, label: '2' },
                        { value: 3, label: '3' },
                        { value: 4, label: '4' }
                      ]}
                      valueLabelDisplay="auto"
                    />
                  </Box>
                ))}
              </Box>

              {/* Text Responses */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>Additional Comments (Optional)</Typography>

                <TextField
                  fullWidth
                  multiline
                  minRows={2}
                  maxRows={4}
                  label="What would you change about your workplace?"
                  value={surveyData.text_responses.q23}
                  onChange={(e) => setSurveyData({
                    ...surveyData,
                    text_responses: {...surveyData.text_responses, q23: e.target.value}
                  })}
                  className="survey-text-input"
                  size="small"
                  sx={{ mb: 2 }}
                />

                <TextField
                  fullWidth
                  multiline
                  minRows={2}
                  maxRows={4}
                  label="How does work impact your mental health?"
                  value={surveyData.text_responses.q24}
                  onChange={(e) => setSurveyData({
                    ...surveyData,
                    text_responses: {...surveyData.text_responses, q24: e.target.value}
                  })}
                  className="survey-text-input"
                  size="small"
                  sx={{ mb: 2 }}
                />

                <TextField
                  fullWidth
                  multiline
                  minRows={2}
                  maxRows={4}
                  label="What does your workplace do well?"
                  value={surveyData.text_responses.q25}
                  onChange={(e) => setSurveyData({
                    ...surveyData,
                    text_responses: {...surveyData.text_responses, q25: e.target.value}
                  })}
                  className="survey-text-input"
                  size="small"
                  sx={{ mb: 2 }}
                />
              </Box>

              <Box display="flex" gap={1} flexWrap="wrap">
                <Button onClick={() => fillSampleInputs('default')} variant="outlined" size="small">
                  Default Sample
                </Button>
                <Button onClick={() => fillSampleInputs('high_risk')} variant="outlined" size="small" color="error">
                  High Risk Sample
                </Button>
                <Button onClick={() => fillSampleInputs('positive')} variant="outlined" size="small" color="success">
                  Positive Sample
                </Button>
                <Button onClick={resetInputs} variant="text" size="small">Reset</Button>
              </Box>
              <Button
                type="submit"
                variant="contained"
                fullWidth
                size="large"
                disabled={loading}
                sx={{ mt: 2 }}
              >
                {loading ? <CircularProgress size={24} /> : 'Analyze Workplace Safety'}
              </Button>
            </form>
          </Paper>
        </Grid>

        {/* Results */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 2.5 }} className="enterprise-card assessment-results">
            <Typography variant="h5" gutterBottom className="section-header">
              Assessment Results
            </Typography>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            {loading && (
              <Box display="flex" justifyContent="center" sx={{ my: 4 }}>
                <CircularProgress />
              </Box>
            )}

            {prediction && (
              <Box>
                {/* Stakeholder Narrative */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="h6" className="section-header">Executive Summary</Typography>
                  <Typography variant="body2" color="textSecondary">
                    {(() => {
                      const res = prediction;
                      const score = Number(res.overall_hseg_score ?? 0).toFixed(1);
                      const tier = res.overall_risk_tier || 'Unknown';
                      const entries = Object.entries(res.category_scores || {}).map(([k, v]) => ({ k, v: Number(v) }));
                      const lows = entries.filter(e => e.v < 2.5).sort((a, b) => a.v - b.v).slice(0, 2).map(e => labelForCategory(e.k));
                      const highs = entries.filter(e => e.v >= 3.2).sort((a, b) => b.v - a.v).slice(0, 2).map(e => labelForCategory(e.k));
                      const textRisk = res.text_risk_analysis?.overall_risk_level;
                      const crisis = res.text_risk_analysis?.crisis_detection?.has_crisis_language;
                      const actions = Array.isArray(res.recommended_interventions) ? res.recommended_interventions.slice(0, 2) : [];
                      const engagement = Math.max(0, Math.min(100, ((Number(res.overall_hseg_score || 0) / 28) * 100))).toFixed(0);
                      const focusText = lows.length ? `Focus on ${lows.join(' & ')}` : 'No critical focus areas detected';
                      const strengthText = highs.length ? `Strengths in ${highs.join(' & ')}` : 'Strengths emerging across categories';
                      const textRiskText = crisis ? 'Crisis language detected in text; escalate immediately.' : (textRisk ? `Text risk: ${textRisk}.` : 'Text risk: Low/Not present.');
                      const actionText = actions.length ? `Priority actions: ${actions.map(a => `${a.category}: ${a.intervention}`).join('; ')}.` : 'No urgent actions required.';
                      return `Overall ${tier} (${score}/28). ${focusText}. ${strengthText}. Engagement index ~${engagement}%. ${textRiskText} ${actionText}`;
                    })()}
                  </Typography>
                </Box>
                {/* Overall Risk */}
                <Card sx={{ mb: 3, bgcolor: getRiskColor(prediction.overall_risk_tier), color: 'white' }}>
                  <CardContent>
                    <Typography variant="h4" component="div">
                      {prediction.overall_risk_tier}
                    </Typography>
                    <Typography variant="h6">
                      HSEG Score: {prediction.overall_hseg_score}/28
                    </Typography>
                    <Typography variant="body2">
                      Confidence: {(prediction.confidence_score * 100).toFixed(1)}%
                    </Typography>
                  </CardContent>
                </Card>

                {/* Category Breakdown Chart */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom>Category Breakdown</Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={prepareChartData()}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="category" />
                        <YAxis domain={[0, 4]} />
                        <Tooltip />
                        <Bar dataKey="score" fill="#1976d2" />
                      </BarChart>
                    </ResponsiveContainer>
                  </Box>

                {/* Analytics insights */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="h6" gutterBottom>Analytics Insights</Typography>
                  {(() => {
                    const entries = Object.entries(prediction.category_scores || {});
                    const lows = entries.filter(([_, v]) => parseFloat(v) < 2.5).map(([k]) => labelForCategory(k));
                    const highs = entries.filter(([_, v]) => parseFloat(v) >= 3.2).map(([k]) => labelForCategory(k));
                    return (
                      <Box className="stack-gap">
                        <Alert severity={lows.length ? 'warning' : 'info'} className="alert-warning">
                          Focus areas: {lows.length ? lows.join(', ') : 'None (no categories below 2.5)'}
                        </Alert>
                        <Alert severity="info" className="alert-info">
                          Strengths: {highs.length ? highs.join(', ') : 'Emerging strengths (no categories above 3.2)'}
                        </Alert>
                      </Box>
                    );
                  })()}
                </Box>

                {/* Contributing Factors */}
                {prediction.contributing_factors && prediction.contributing_factors.length > 0 && (
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom>Key Risk Factors</Typography>
                    <Box>
                      {prediction.contributing_factors.map((factor, index) => (
                        <Chip
                          key={index}
                          label={factor}
                          color="warning"
                          sx={{ mr: 1, mb: 1 }}
                        />
                      ))}
                    </Box>
                  </Box>
                )}

                {/* Interventions */}
                {prediction.recommended_interventions && prediction.recommended_interventions.length > 0 && (
                  <Box>
                    <Typography variant="h6" gutterBottom>Recommended Actions</Typography>
                    {prediction.recommended_interventions.map((intervention, index) => (
                      <Alert key={index} severity="info" sx={{ mb: 1 }}>
                        <strong>{intervention.category}:</strong> {intervention.intervention}
                      </Alert>
                    ))}
                  </Box>
                )}
                {/* Zero-Shot Text Classification Results (Q23-Q25) */}
                {textRiskResults && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="h6" gutterBottom>Zero-Shot Text Classification (Q23-Q25)</Typography>

                    {/* Processing Info */}
                    <Box sx={{ mb: 2, p: 1, bgcolor: '#f5f5f5', borderRadius: 1 }}>
                      <Typography variant="caption" color="textSecondary">
                        Model: {textRiskResults.model_name} | Processing Time: {textRiskResults.processing_time_ms?.toFixed(0)}ms
                      </Typography>
                    </Box>

                    {/* HSEG Risk Analysis from Text */}
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle1" gutterBottom color="error">
                        🏢 Organizational Risks Detected in Text
                      </Typography>
                      {textRiskResults.hseg_risk_analysis?.slice(0, 3).map((risk, index) => (
                        <Box key={index} sx={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          p: 1,
                          mb: 1,
                          bgcolor: '#f8f9fa',
                          borderRadius: 1,
                          borderLeft: `4px solid ${risk.score >= 0.7 ? '#d32f2f' : risk.score >= 0.5 ? '#ff9800' : '#4caf50'}`
                        }}>
                          <Typography variant="body2">
                            <strong>{risk.label}</strong>
                          </Typography>
                          <Chip
                            label={`${(risk.score * 100).toFixed(1)}%`}
                            color={risk.score >= 0.7 ? 'error' : risk.score >= 0.5 ? 'warning' : 'success'}
                            size="small"
                          />
                        </Box>
                      ))}
                    </Box>

                    {/* Individual Distress from Text */}
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle1" gutterBottom color="secondary">
                        👤 Individual Distress Detected in Text
                      </Typography>
                      {textRiskResults.individual_distress_analysis?.map((distress, index) => (
                        <Box key={index} sx={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          p: 1,
                          mb: 1,
                          bgcolor: '#f8f9fa',
                          borderRadius: 1,
                          borderLeft: `4px solid ${distress.score >= 0.7 ? '#d32f2f' : distress.score >= 0.5 ? '#ff9800' : '#4caf50'}`
                        }}>
                          <Typography variant="body2">
                            <strong>{distress.label}</strong>
                          </Typography>
                          <Chip
                            label={`${(distress.score * 100).toFixed(1)}%`}
                            color={distress.score >= 0.7 ? 'error' : distress.score >= 0.5 ? 'warning' : 'success'}
                            size="small"
                          />
                        </Box>
                      ))}
                    </Box>

                    {/* Crisis Alert */}
                    {textRiskResults.individual_distress_analysis?.find(d =>
                      d.label.includes('self-harm') && d.score > 0.5
                    ) && (
                      <Alert severity="error">
                        <strong>⚠️ CRISIS ALERT ⚠️</strong><br />
                        High probability of self-harm ideation detected in text responses. Immediate intervention recommended.
                      </Alert>
                    )}
                  </Box>
                )}

                {/* Legacy Text Risk Analysis (if available from individual prediction) */}
                {prediction.text_risk_analysis && !textRiskResults && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="h6" gutterBottom>Text Risk Analysis</Typography>
                    <Alert severity={prediction.text_risk_analysis.crisis_detection?.has_crisis_language ? 'error' : 'info'} sx={{ mb: 2 }}>
                      Overall Text Risk: {prediction.text_risk_analysis.overall_risk_level || 'N/A'}
                    </Alert>
                  </Box>
                )}
              </Box>
            )}

            {!prediction && !loading && (
              <Typography variant="body1" color="textSecondary" align="center" sx={{ py: 4 }}>
                Complete the assessment to see your workplace safety analysis
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
      </Container>
    </div>
  );
}

export default App;
  const CATEGORY_LABELS = {
    '1': 'Power Abuse & Suppression',
    '2': 'Discrimination & Exclusion',
    '3': 'Manipulative Work Culture',
    '4': 'Failure of Accountability',
    '5': 'Mental Health Harm',
    '6': 'Voice & Autonomy'
  };

  const labelForCategory = (key) => CATEGORY_LABELS[String(key)] || `Category ${key}`;
