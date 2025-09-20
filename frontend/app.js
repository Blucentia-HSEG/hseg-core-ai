// HSEG AI API Testing Dashboard - Improved Survey Version
// Matches the improved_hseg_survey.md specifications exactly

class HSEGAPITester {
    constructor() {
        this.baseUrl = 'http://localhost:8001';
        this.authToken = '';
        this.organizationalData = {
            organization_info: {},
            individual_responses: []
        };

        // Improved HSEG Survey Questions
        this.surveyQuestions = {
            // Category 1: Power Abuse & Suppression (Critical Weight: 3.0)
            1: "I feel safe speaking up when I experience or witness something wrong at my workplace.",
            2: "Leadership uses their position to silence criticism rather than address concerns.",
            3: "People here avoid speaking up because they fear negative consequences.",
            4: "I can report concerns without fear of punishment/retaliation.",

            // Category 2: Discrimination & Exclusion (Severe Weight: 2.5)
            5: "People are treated fairly regardless of their race, gender, age, or background.",
            6: "Everyone has equal access to opportunities and resources here.",
            7: "In the past 30 days, how many times have you witnessed comments or behaviors that exclude or diminish others?",

            // Category 3: Manipulative Work Culture (Moderate Weight: 2.0)
            8: "Leadership manipulates emotions to control behavior rather than address real issues.",
            9: "We're pressured to appear positive even when facing serious problems.",
            10: "Personal time and well-being are respected and protected here.",

            // Category 4: Failure of Accountability (Critical Weight: 3.0)
            11: "Problems and mistakes are addressed transparently and fairly.",
            12: "Investigations of misconduct are conducted fairly without conflicts of interest.",
            13: "Information about decisions affecting us is shared openly and honestly.",
            14: "When someone reports a problem, appropriate action is taken.",

            // Category 5: Mental Health Harm (Severe Weight: 2.5)
            15: "During the past 30 days, how often did work make you feel nervous or anxious?",
            16: "During the past 30 days, how many days did work make you feel hopeless or depressed?",
            17: "Based on your definition of burnout, how would you rate your current level?",
            18: "Support is available when facing work-related emotional challenges.",

            // Category 6: Erosion of Voice & Autonomy (Moderate Weight: 2.0)
            19: "People feel their input is valued and acted upon when they speak up.",
            20: "I have sufficient autonomy to make decisions about my work.",
            21: "In the past 30 days, how many times have suggestions or concerns been ignored or dismissed?",
            22: "People here feel empowered to make improvements in their work area."
        };

        // Question-specific response options
        this.responseOptions = {
            // Standard Likert scale (most questions)
            standard: [
                { value: 4.0, text: "Strongly Agree" },
                { value: 3.0, text: "Agree" },
                { value: 2.0, text: "Disagree" },
                { value: 1.0, text: "Strongly Disagree" }
            ],

            // Reverse-scored questions (Q2, Q3, Q8, Q9)
            reverse: [
                { value: 4.0, text: "Strongly Disagree" },
                { value: 3.0, text: "Disagree" },
                { value: 2.0, text: "Agree" },
                { value: 1.0, text: "Strongly Agree" }
            ],

            // Frequency-based questions (Q7, Q21)
            frequency: [
                { value: 4.0, text: "Never (0 times)" },
                { value: 3.0, text: "Rarely (1-2 times)" },
                { value: 2.0, text: "Sometimes (3-5 times)" },
                { value: 1.0, text: "Often (6 or more times)" }
            ],

            // Time-based questions (Q15, Q16)
            timeFrequency: [
                { value: 4.0, text: "None of the time (0 days)" },
                { value: 3.0, text: "A little of the time (1-7 days)" },
                { value: 2.0, text: "Some of the time (8-14 days)" },
                { value: 1.0, text: "Most/All of the time (15+ days)" }
            ],

            // Burnout scale (Q17)
            burnout: [
                { value: 4.0, text: "No burnout" },
                { value: 3.0, text: "Mild burnout" },
                { value: 2.0, text: "Moderate burnout" },
                { value: 1.0, text: "Severe burnout" }
            ]
        };

        // Question to option mapping
        this.questionOptions = {
            1: 'standard', 2: 'reverse', 3: 'reverse', 4: 'standard',
            5: 'standard', 6: 'standard', 7: 'frequency',
            8: 'reverse', 9: 'reverse', 10: 'standard',
            11: 'standard', 12: 'standard', 13: 'standard', 14: 'standard',
            15: 'timeFrequency', 16: 'timeFrequency', 17: 'burnout', 18: 'standard',
            19: 'standard', 20: 'standard', 21: 'frequency', 22: 'standard'
        };

        this.init();
    }

    init() {
        this.generateImprovedSurveyQuestions();
        this.setupEventListeners();
        this.checkHealth();
        this.fillImprovedTextResponses();
    }

    // Generate Q1-Q22 survey questions with exact improved survey specifications
    generateImprovedSurveyQuestions() {
        const surveyContainer = document.getElementById('surveyQuestions');
        const questionCategories = [
            { range: [1, 4], label: 'Power Abuse & Suppression (Critical Weight: 3.0)', color: '#dc3545' },
            { range: [5, 7], label: 'Discrimination & Exclusion (Severe Weight: 2.5)', color: '#fd7e14' },
            { range: [8, 10], label: 'Manipulative Work Culture (Moderate Weight: 2.0)', color: '#ffc107' },
            { range: [11, 14], label: 'Failure of Accountability (Critical Weight: 3.0)', color: '#dc3545' },
            { range: [15, 18], label: 'Mental Health Harm (Severe Weight: 2.5)', color: '#fd7e14' },
            { range: [19, 22], label: 'Erosion of Voice & Autonomy (Moderate Weight: 2.0)', color: '#ffc107' }
        ];

        surveyContainer.innerHTML = ''; // Clear existing content

        questionCategories.forEach(category => {
            // Category header
            const categoryHeader = document.createElement('div');
            categoryHeader.className = 'col-12 mt-4 mb-3';
            categoryHeader.innerHTML = `
                <h5 style="color: ${category.color}; border-left: 4px solid ${category.color}; padding-left: 12px;">
                    ${category.label}
                </h5>
            `;
            surveyContainer.appendChild(categoryHeader);

            // Questions in this category
            for (let i = category.range[0]; i <= category.range[1]; i++) {
                const questionDiv = document.createElement('div');
                questionDiv.className = 'col-12 mb-4';

                const optionType = this.questionOptions[i];
                const options = this.responseOptions[optionType];

                const optionsHTML = options.map(option =>
                    `<option value="${option.value}">${option.text}</option>`
                ).join('');

                questionDiv.innerHTML = `
                    <div class="card">
                        <div class="card-body">
                            <label class="form-label fw-bold">Q${i}. ${this.surveyQuestions[i]}</label>
                            <select class="form-control form-control-lg" id="q${i}" required>
                                <option value="">Please select your response...</option>
                                ${optionsHTML}
                            </select>
                            ${this.getQuestionNote(i)}
                        </div>
                    </div>
                `;
                surveyContainer.appendChild(questionDiv);
            }
        });
    }

    // Get additional notes for specific questions
    getQuestionNote(questionNum) {
        const notes = {
            7: '<small class="text-muted">This includes comments, behaviors, or actions that make others feel excluded or diminished.</small>',
            15: '<small class="text-muted">Consider physical symptoms like stress, worry, or feeling on edge due to work.</small>',
            16: '<small class="text-muted">This includes feelings of hopelessness, sadness, or depression related to work.</small>',
            17: '<small class="text-muted">Use your own understanding of what burnout means to you personally.</small>',
            21: '<small class="text-muted">Times when your feedback, suggestions, or concerns were not acknowledged or acted upon.</small>'
        };
        return notes[questionNum] ? `<div class="mt-2">${notes[questionNum]}</div>` : '';
    }

    // Fill improved text responses based on survey specifications
    fillImprovedTextResponses() {
        document.getElementById('q23Text').value = 'Improve communication transparency and ensure leadership addresses concerns rather than silencing them.';
        document.getElementById('q24Text').value = 'Work-related stress and anxiety from unclear expectations and fear of speaking up about problems.';
        document.getElementById('q25Text').value = 'Strong technical resources and collaborative team environment that supports professional growth.';

        // Update labels to match improved survey
        document.querySelector('label[for="q23Text"]').textContent = 'Q23: If you could change one thing that would most improve safety and wellbeing in your workplace, what would it be? (150 characters max)';
        document.querySelector('label[for="q24Text"]').textContent = 'Q24: What workplace experience, if any, has most negatively impacted your mental health or wellbeing? (200 characters max)';
        document.querySelector('label[for="q25Text"]').textContent = 'Q25: What is one thing your workplace does exceptionally well that other organizations should adopt? (150 characters max)';

        // Add character limits
        document.getElementById('q23Text').setAttribute('maxlength', '150');
        document.getElementById('q24Text').setAttribute('maxlength', '200');
        document.getElementById('q25Text').setAttribute('maxlength', '150');
    }

    // Setup event listeners
    setupEventListeners() {
        // API Configuration
        document.getElementById('apiBaseUrl').addEventListener('change', (e) => {
            this.baseUrl = e.target.value;
        });

        document.getElementById('authToken').addEventListener('change', (e) => {
            this.authToken = e.target.value;
        });

        // Form submissions
        document.getElementById('individualForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitIndividualAssessment();
        });

        document.getElementById('organizationalForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitOrganizationalAssessment();
        });

        document.getElementById('uploadForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.uploadFile();
        });
    }

    // Get authorization headers
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (this.authToken) {
            headers['Authorization'] = this.authToken.startsWith('Bearer ')
                ? this.authToken
                : `Bearer ${this.authToken}`;
        }

        return headers;
    }

    // Show loading state
    showLoading(formId) {
        const form = document.getElementById(formId);
        const button = form.querySelector('button[type="submit"]');
        const spinner = button.querySelector('.loading');

        button.disabled = true;
        spinner.style.display = 'inline-block';
    }

    // Hide loading state
    hideLoading(formId) {
        const form = document.getElementById(formId);
        const button = form.querySelector('button[type="submit"]');
        const spinner = button.querySelector('.loading');

        button.disabled = false;
        spinner.style.display = 'none';
    }

    // Display response in formatted box
    displayResponse(containerId, data, isError = false) {
        const container = document.getElementById(containerId);
        container.style.display = 'block';

        if (isError) {
            container.innerHTML = `<div class="text-danger"><strong>Error:</strong><br>${JSON.stringify(data, null, 2)}</div>`;
        } else {
            let formattedResponse = JSON.stringify(data, null, 2);

            // Add color coding for risk tiers
            formattedResponse = formattedResponse.replace(
                /"overall_risk_tier":\s*"(Crisis|At_Risk|Mixed|Safe|Thriving)"/g,
                (match, tier) => {
                    const className = `risk-tier-${tier.toLowerCase().replace('_', '-')}`;
                    return match.replace(tier, `<span class="${className}">${tier}</span>`);
                }
            );

            container.innerHTML = `<div style="white-space: pre-wrap;">${formattedResponse}</div>`;
        }

        // Scroll to response
        container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // Check API health
    async checkHealth() {
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            const data = await response.json();

            const statusIndicator = document.querySelector('#apiStatus .status-indicator');
            const statusText = document.querySelector('#apiStatus span:last-child');

            if (response.ok) {
                statusIndicator.className = `status-indicator status-${data.status === 'healthy' ? 'healthy' : 'degraded'}`;
                statusText.textContent = `API Status: ${data.status.toUpperCase()}`;
            } else {
                statusIndicator.className = 'status-indicator status-error';
                statusText.textContent = 'API Status: ERROR';
            }
        } catch (error) {
            const statusIndicator = document.querySelector('#apiStatus .status-indicator');
            const statusText = document.querySelector('#apiStatus span:last-child');

            statusIndicator.className = 'status-indicator status-error';
            statusText.textContent = 'API Status: UNREACHABLE';
        }
    }

    // Submit individual assessment
    async submitIndividualAssessment() {
        this.showLoading('individualForm');

        try {
            // Collect survey responses with validation
            const surveyResponses = {};
            for (let i = 1; i <= 22; i++) {
                const value = document.getElementById(`q${i}`).value;
                if (!value) {
                    throw new Error(`Question ${i} is required. Please answer all questions to proceed.`);
                }
                surveyResponses[`q${i}`] = parseFloat(value);
            }

            // Validate text responses for character limits
            const q23Text = document.getElementById('q23Text').value;
            const q24Text = document.getElementById('q24Text').value;
            const q25Text = document.getElementById('q25Text').value;

            if (q23Text.length > 150) {
                throw new Error('Q23 response must be 150 characters or less.');
            }
            if (q24Text.length > 200) {
                throw new Error('Q24 response must be 200 characters or less.');
            }
            if (q25Text.length > 150) {
                throw new Error('Q25 response must be 150 characters or less.');
            }

            // Collect text responses
            const textResponses = {
                Q23: q23Text,
                Q24: q24Text,
                Q25: q25Text
            };

            // Collect demographics with improved survey options
            const demographics = {
                age_range: document.getElementById('ageRange').value,
                gender_identity: document.getElementById('genderIdentity').value,
                tenure_range: document.getElementById('tenureRange').value,
                position_level: document.getElementById('positionLevel').value,
                department: document.getElementById('department').value,
                supervises_others: document.getElementById('supervisesOthers').value === 'true'
            };

            const requestData = {
                response_id: document.getElementById('responseId').value,
                domain: document.getElementById('domain').value,
                survey_responses: surveyResponses,
                text_responses: textResponses,
                demographics: demographics
            };

            const response = await fetch(`${this.baseUrl}/predict/individual`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(requestData)
            });

            const data = await response.json();

            if (response.ok) {
                this.displayResponse('individualResponse', data);
            } else {
                this.displayResponse('individualResponse', data, true);
            }

        } catch (error) {
            this.displayResponse('individualResponse', { error: error.message }, true);
        } finally {
            this.hideLoading('individualForm');
        }
    }

    // Generate sample organizational data with improved survey patterns
    generateSampleOrgData() {
        const domains = ['Business', 'Healthcare', 'University'];
        const departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance'];
        const ageRanges = ['25-34', '35-44', '45-54'];
        const genders = ['Woman', 'Man', 'Non-binary'];
        const tenures = ['1-3_years', '4-7_years', '8+_years'];
        const positions = ['Entry', 'Mid', 'Senior'];

        this.organizationalData.organization_info = {
            org_id: document.getElementById('orgId').value,
            org_name: document.getElementById('orgName').value,
            domain: document.getElementById('orgDomain').value,
            employee_count: parseInt(document.getElementById('employeeCount').value)
        };

        this.organizationalData.individual_responses = [];

        // Generate 5 sample employees with varied risk patterns
        for (let i = 1; i <= 5; i++) {
            const surveyResponses = {};

            // Generate realistic patterns based on improved survey
            const riskPatterns = [
                [3.0, 2.0, 2.0, 3.0, 3.0, 3.0, 3.0, 2.0, 2.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 2.0, 3.0, 3.0, 3.0, 3.0, 3.0], // Moderate risk
                [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0], // Low risk
                [2.0, 1.0, 1.0, 2.0, 2.0, 2.0, 2.0, 1.0, 1.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 2.0, 2.0], // High risk
                [3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 2.0, 2.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0], // Mixed
                [2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0]  // At risk
            ];

            const pattern = riskPatterns[i - 1];
            for (let j = 1; j <= 22; j++) {
                surveyResponses[`q${j}`] = pattern[j - 1];
            }

            const textResponses = {
                Q23: `Employee ${i}: Improve transparency and address workplace concerns more effectively`,
                Q24: `Employee ${i}: Work-related stress and communication issues affecting wellbeing`,
                Q25: `Employee ${i}: Strong technical resources and supportive team collaboration`
            };

            const demographics = {
                age_range: ageRanges[Math.floor(Math.random() * ageRanges.length)],
                gender_identity: genders[Math.floor(Math.random() * genders.length)],
                tenure_range: tenures[Math.floor(Math.random() * tenures.length)],
                position_level: positions[Math.floor(Math.random() * positions.length)],
                department: departments[Math.floor(Math.random() * departments.length)],
                supervises_others: Math.random() > 0.7
            };

            this.organizationalData.individual_responses.push({
                response_id: `emp_${i.toString().padStart(3, '0')}`,
                domain: this.organizationalData.organization_info.domain,
                survey_responses: surveyResponses,
                text_responses: textResponses,
                demographics: demographics
            });
        }

        // Show confirmation
        document.getElementById('orgEmployeeCount').style.display = 'block';
        document.getElementById('employeeCountText').textContent =
            `Generated ${this.organizationalData.individual_responses.length} sample employee responses using improved HSEG survey patterns.`;
    }

    // Submit organizational assessment
    async submitOrganizationalAssessment() {
        this.showLoading('organizationalForm');

        try {
            if (this.organizationalData.individual_responses.length === 0) {
                throw new Error('Please generate sample employee data first or ensure you have at least 5 individual responses.');
            }

            const response = await fetch(`${this.baseUrl}/predict/organizational`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(this.organizationalData)
            });

            const data = await response.json();

            if (response.ok) {
                this.displayResponse('organizationalResponse', data);
            } else {
                this.displayResponse('organizationalResponse', data, true);
            }

        } catch (error) {
            this.displayResponse('organizationalResponse', { error: error.message }, true);
        } finally {
            this.hideLoading('organizationalForm');
        }
    }

    // Upload file
    async uploadFile() {
        this.showLoading('uploadForm');

        try {
            if (!this.authToken) {
                throw new Error('Authorization token is required for file upload. Please set it in the API Configuration section.');
            }

            const fileInput = document.getElementById('csvFile');
            const file = fileInput.files[0];

            if (!file) {
                throw new Error('Please select a file to upload');
            }

            const formData = new FormData();
            formData.append('file', file);

            const orgId = document.getElementById('uploadOrgId').value;
            if (orgId) {
                formData.append('organization_id', orgId);
            }

            const headers = {};
            if (this.authToken) {
                headers['Authorization'] = this.authToken.startsWith('Bearer ')
                    ? this.authToken
                    : `Bearer ${this.authToken}`;
            }

            const response = await fetch(`${this.baseUrl}/upload/survey-data`, {
                method: 'POST',
                headers: headers,
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                this.displayResponse('uploadResponse', data);
            } else {
                this.displayResponse('uploadResponse', data, true);
            }

        } catch (error) {
            this.displayResponse('uploadResponse', { error: error.message }, true);
        } finally {
            this.hideLoading('uploadForm');
        }
    }

    // Check pipeline status
    async checkPipelineStatus() {
        try {
            const response = await fetch(`${this.baseUrl}/pipeline/status`, {
                headers: this.getAuthHeaders()
            });

            const data = await response.json();

            if (response.ok) {
                this.displayResponse('pipelineResponse', data);
            } else {
                this.displayResponse('pipelineResponse', data, true);
            }

        } catch (error) {
            this.displayResponse('pipelineResponse', { error: error.message }, true);
        }
    }
}

// Fill sample data function with improved survey pattern
function fillSampleData() {
    // Fill basic info
    document.getElementById('responseId').value = 'improved_test_001';
    document.getElementById('domain').value = 'Business';

    // Fill survey responses with realistic improved survey pattern
    const samplePattern = {
        1: 3.0, 2: 3.0, 3: 2.0, 4: 3.0,     // Power Abuse & Suppression
        5: 3.0, 6: 3.0, 7: 3.0,             // Discrimination & Exclusion
        8: 3.0, 9: 2.0, 10: 3.0,            // Manipulative Work Culture
        11: 3.0, 12: 2.0, 13: 2.0, 14: 3.0, // Failure of Accountability
        15: 3.0, 16: 3.0, 17: 2.0, 18: 3.0, // Mental Health Harm
        19: 3.0, 20: 3.0, 21: 3.0, 22: 3.0  // Erosion of Voice & Autonomy
    };

    for (let i = 1; i <= 22; i++) {
        document.getElementById(`q${i}`).value = samplePattern[i];
    }

    // Fill demographics with improved survey options
    document.getElementById('ageRange').value = '35-44';
    document.getElementById('genderIdentity').value = 'Woman';
    document.getElementById('tenureRange').value = '1-3_years';
    document.getElementById('positionLevel').value = 'Mid';
    document.getElementById('department').value = 'Engineering';
    document.getElementById('supervisesOthers').value = 'false';

    alert('Improved HSEG survey sample data filled! All questions now use the exact specifications from improved_hseg_survey.md');
}

// Global functions
function checkHealth() {
    hsegApp.checkHealth();
}

function generateSampleOrgData() {
    hsegApp.generateSampleOrgData();
}

function checkPipelineStatus() {
    hsegApp.checkPipelineStatus();
}

// Initialize the application
const hsegApp = new HSEGAPITester();