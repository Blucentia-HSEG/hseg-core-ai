import React, { useState } from 'react';
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
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [surveyData, setSurveyData] = useState({
    domain: 'Business',
    survey_responses: {},
    demographics: {
      age_range: '25-34',
      gender_identity: 'Prefer_not_to_say',
      position_level: 'Mid'
    },
    text_responses: {
      q23: '',
      q24: '',
      q25: ''
    }
  });

  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/predict/individual`, surveyData);
      setPrediction(response.data);
    } catch (error) {
      console.error('Prediction failed:', error);
      setError(error.response?.data?.detail || 'Prediction failed. Please try again.');
    } finally {
      setLoading(false);
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
      category: `Cat ${category}`,
      score: parseFloat(score),
      fullScore: 4.0
    }));
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom align="center" color="primary">
        HSEG Workplace Safety Assessment
      </Typography>

      <Typography variant="subtitle1" gutterBottom align="center" color="textSecondary" sx={{ mb: 4 }}>
        Psychological Safety and Risk Assessment Tool
      </Typography>

      <Grid container spacing={4}>
        {/* Survey Form */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Assessment Survey
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
                      step={0.1}
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
                  rows={3}
                  label="What would you change about your workplace?"
                  value={surveyData.text_responses.q23}
                  onChange={(e) => setSurveyData({
                    ...surveyData,
                    text_responses: {...surveyData.text_responses, q23: e.target.value}
                  })}
                  sx={{ mb: 2 }}
                />

                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="How does work impact your mental health?"
                  value={surveyData.text_responses.q24}
                  onChange={(e) => setSurveyData({
                    ...surveyData,
                    text_responses: {...surveyData.text_responses, q24: e.target.value}
                  })}
                  sx={{ mb: 2 }}
                />
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
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
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
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={prepareChartData()}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="category" />
                      <YAxis domain={[0, 4]} />
                      <Tooltip />
                      <Bar dataKey="score" fill="#1976d2" />
                    </BarChart>
                  </ResponsiveContainer>
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
  );
}

export default App;