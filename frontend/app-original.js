// HSEG AI API Testing Dashboard
// Main application logic with authentication and error handling

class HSEGAPITester {
    constructor() {
        this.baseUrl = 'http://localhost:8001';
        this.authToken = '';
        this.organizationalData = {
            organization_info: {},
            individual_responses: []
        };
        this.init();
    }

    init() {
        this.generateSurveyQuestions();
        this.setupEventListeners();
        this.checkHealth();
        this.fillDefaultTextResponses();
    }

    // Generate Q1-Q22 survey questions dynamically
    generateSurveyQuestions() {
        const surveyContainer = document.getElementById('surveyQuestions');
        const questionCategories = [
            { range: [1, 4], label: 'Psychological Safety & Voice' },
            { range: [5, 8], label: 'Discrimination & Harassment' },
            { range: [9, 12], label: 'Power Dynamics & Abuse' },
            { range: [13, 16], label: 'Leadership & Accountability' },
            { range: [17, 20], label: 'Mental Health Impact' },
            { range: [21, 22], label: 'Work Environment' }
        ];

        questionCategories.forEach(category => {
            // Category header
            const categoryHeader = document.createElement('div');
            categoryHeader.className = 'col-12 mt-3 mb-2';
            categoryHeader.innerHTML = `<h6 class="text-primary">${category.label}</h6>`;
            surveyContainer.appendChild(categoryHeader);

            // Questions in this category
            for (let i = category.range[0]; i <= category.range[1]; i++) {
                const questionDiv = document.createElement('div');
                questionDiv.className = 'col-md-6 col-lg-3 mb-3';
                questionDiv.innerHTML = `
                    <label class="form-label">Q${i}</label>
                    <select class="form-control" id="q${i}" required>
                        <option value="">Select...</option>
                        <option value="1.0">1.0 - Strongly Disagree</option>
                        <option value="2.0">2.0 - Disagree</option>
                        <option value="2.5" selected>2.5 - Neutral</option>
                        <option value="3.0">3.0 - Agree</option>
                        <option value="4.0">4.0 - Strongly Agree</option>
                    </select>
                `;
                surveyContainer.appendChild(questionDiv);
            }
        });
    }

    // Fill default text responses
    fillDefaultTextResponses() {
        document.getElementById('q23Text').value = 'Management needs to improve communication and be more transparent with employees about company decisions and changes.';
        document.getElementById('q24Text').value = 'Work stress has been affecting my sleep and causing some anxiety, but it is generally manageable with current support systems.';
        document.getElementById('q25Text').value = 'The technical resources and office facilities are excellent, and there are good professional development opportunities available.';
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
            // Collect survey responses
            const surveyResponses = {};
            for (let i = 1; i <= 22; i++) {
                const value = document.getElementById(`q${i}`).value;
                if (!value) {
                    throw new Error(`Question ${i} is required`);
                }
                surveyResponses[`q${i}`] = parseFloat(value);
            }

            // Collect text responses
            const textResponses = {
                Q23: document.getElementById('q23Text').value,
                Q24: document.getElementById('q24Text').value,
                Q25: document.getElementById('q25Text').value
            };

            // Collect demographics
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

    // Generate sample organizational data
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

        // Generate 5 sample employees
        for (let i = 1; i <= 5; i++) {
            const surveyResponses = {};

            // Generate varied responses based on risk patterns
            const baseRisk = Math.random() * 3 + 1; // 1-4 scale
            for (let j = 1; j <= 22; j++) {
                const variation = (Math.random() - 0.5) * 1.0; // ±0.5 variation
                const value = Math.max(1.0, Math.min(4.0, baseRisk + variation));
                surveyResponses[`q${j}`] = Math.round(value * 2) / 2; // Round to nearest 0.5
            }

            const textResponses = {
                Q23: `Employee ${i} feedback on workplace culture and management practices`,
                Q24: `Mental health status and stress level description for employee ${i}`,
                Q25: `Positive aspects and resources available according to employee ${i}`
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
            `Generated ${this.organizationalData.individual_responses.length} sample employee responses for organizational assessment.`;
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

// Fill sample data function
function fillSampleData() {
    // Fill basic info
    document.getElementById('responseId').value = 'test_sample_001';
    document.getElementById('domain').value = 'Business';

    // Fill survey responses with varied risk pattern
    const riskPattern = [
        2.0, 3.0, 3.0, 2.5, 3.0, 2.0, 3.5, 2.5, 3.0, 2.5,
        3.0, 2.0, 3.5, 2.5, 3.0, 2.5, 3.0, 2.0, 3.5, 2.5, 3.0, 2.5
    ];

    for (let i = 1; i <= 22; i++) {
        document.getElementById(`q${i}`).value = riskPattern[i - 1];
    }

    // Fill demographics
    document.getElementById('ageRange').value = '35-44';
    document.getElementById('genderIdentity').value = 'Woman';
    document.getElementById('tenureRange').value = '1-3_years';
    document.getElementById('positionLevel').value = 'Mid';
    document.getElementById('department').value = 'Engineering';
    document.getElementById('supervisesOthers').value = 'false';

    // Text responses are already filled by default
    alert('Sample data filled! You can now submit the individual assessment.');
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