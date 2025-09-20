# HSEG 50K Synthetic Dataset Generation - Complete Guide

## 🎯 Overview

This guide covers the generation of 50,000 sophisticated synthetic survey responses for the HSEG (Healthcare, Schools, Enterprise, Government) AI system. The dataset is designed for enterprise-scale NLP model training with authentic psychological trauma narratives and company-specific workplace culture elements.

## 📊 Dataset Specifications

### Scale and Structure
- **Total Records**: 50,000 synthetic responses
- **File Size**: ~150MB CSV format
- **Processing Time**: 15-30 minutes depending on system specs
- **Memory Requirements**: 4GB+ RAM recommended
- **Storage**: 200MB+ free disk space

### Data Schema
```csv
response_id,organization_name,domain,employee_count,department,position_level,
age_range,gender_identity,tenure_range,supervises_others,
q1,q2,q3,...,q22,q23_text,q24_text,q25_text,submission_date
```

### Domain Distribution
- **Healthcare**: 30% (15,000 records)
- **University**: 25% (12,500 records)
- **Business**: 45% (22,500 records)

## 🏢 Company Coverage

### Healthcare Organizations
- Kaiser Permanente (218K employees) - Integrated care model
- Mayo Clinic (73K employees) - Academic medical excellence
- Cleveland Clinic (74K employees) - Patient-first philosophy
- Johns Hopkins (51K employees) - Research-intensive culture
- HCA Healthcare (265K employees) - Corporate efficiency model

### Universities
- Harvard University (17K employees) - Elite academic pressure
- Stanford University (16K employees) - Innovation/entrepreneurial culture
- MIT (13K employees) - Technical excellence demands
- University of California (280K employees) - Public research challenges
- Yale University (12K employees) - Traditional academic culture

### Business Organizations
- Microsoft (221K employees) - Growth mindset culture
- Google (174K employees) - Innovation/data-driven approach
- Amazon (1.6M employees) - Customer obsession philosophy
- Apple (164K employees) - Perfectionist design culture
- Meta (87K employees) - Move fast/break things mentality
- Tesla (127K employees) - Mission-driven intensity
- Netflix (11K employees) - Freedom and responsibility model

## 📝 Narrative Features

### Response Types by Risk Tier

#### Crisis Tier (5% - 2,500 records)
- **Characteristics**: Severe trauma, PTSD, suicidal ideation
- **Length**: 400-800 characters with emotional progression
- **Content**: Specific incidents, trauma symptoms, help-seeking attempts
- **Examples**:
  - Patient deaths causing PTSD flashbacks
  - Academic harassment leading to suicide attempts
  - Workplace abuse triggering trauma responses

#### At-Risk Tier (15% - 7,500 records)
- **Characteristics**: Anxiety, depression, panic attacks
- **Length**: 300-600 characters with moderate emotional intensity
- **Content**: Escalating stress, early trauma symptoms, coping struggles
- **Examples**:
  - Burnout affecting personal relationships
  - Imposter syndrome causing performance anxiety
  - Workplace discrimination creating chronic stress

#### Mixed Tier (30% - 15,000 records)
- **Characteristics**: Moderate stress, work-life balance issues
- **Length**: 250-500 characters with balanced perspective
- **Content**: Manageable challenges, some support systems
- **Examples**:
  - Demanding workload with occasional overwhelm
  - Academic pressure with supportive mentorship
  - Corporate stress with adequate coping mechanisms

#### Safe Tier (35% - 17,500 records)
- **Characteristics**: Manageable stress, adequate support
- **Length**: 200-400 characters with positive undertones
- **Content**: Challenges with effective coping, support systems
- **Examples**:
  - Healthcare stress managed through team support
  - Academic challenges with mentor guidance
  - Work pressure balanced by company resources

#### Thriving Tier (15% - 7,500 records)
- **Characteristics**: Positive mental health, strong support
- **Length**: 200-350 characters with optimistic tone
- **Content**: Growth opportunities, effective support, resilience
- **Examples**:
  - Meaningful healthcare work with trauma support
  - Academic freedom enabling research passion
  - Corporate culture promoting work-life balance

### Narrative Sophistication

#### Emotional Progression Arcs
1. **Crisis Arc**: Incident → Impact → Escalation → Current State → Help/Isolation
2. **Burnout Arc**: Enthusiasm → Decline → Breaking Point → Coping → Uncertainty
3. **Recovery Arc**: Past Trauma → Turning Point → Support → Progress → Challenges

#### Linguistic Variation Features
- **Synonym Replacement**: 30+ contextual synonym sets
- **Intensity Modifiers**: Emotional amplification based on risk tier
- **Transition Phrases**: Temporal, causal, contrast, continuation markers
- **Company-Specific Terms**: Cultural phrases unique to each organization

#### Psychological Authenticity
- **Trauma Terminology**: Clinical language for severe cases
- **Progression Patterns**: Realistic psychological deterioration/recovery
- **Coping Mechanisms**: Evidence-based therapeutic approaches
- **Cultural Context**: Domain-specific workplace stressors

## 🚀 Generation Process

### System Architecture

```
hseg_50k_final_generator.py (Main Generator)
├── Company Data Initialization
├── Narrative Template System
├── Text Variation Engine
├── Batch Processing (5K batches)
└── Output Validation

advanced_narrative_generator.py (Narrative Engine)
├── Emotional Progression Arcs
├── Company-Specific Context
├── Psychological Authenticity
└── Cultural Phrase Integration

text_variation_engine.py (Linguistic Diversity)
├── Synonym Replacement
├── Intensity Modification
├── Transition Enhancement
└── Coherence Validation

dataset_validator.py (Quality Assurance)
├── Schema Validation
├── Narrative Quality Analysis
├── Demographic Distribution Checks
└── Risk Tier Consistency Validation
```

### Generation Steps

1. **Initialization** (30 seconds)
   - Load company profiles and cultural data
   - Initialize narrative templates and variation engines
   - Set up batch processing parameters

2. **Batch Generation** (15-25 minutes)
   - Process in 5,000 record batches for memory efficiency
   - Generate demographics using realistic distributions
   - Create Likert responses based on risk tier probabilities
   - Generate rich narratives with company-specific context
   - Apply linguistic variation for diversity

3. **Data Assembly** (2-3 minutes)
   - Combine all batches into final dataset
   - Apply column ordering and formatting
   - Generate metadata and statistics

4. **Validation** (1-2 minutes)
   - Schema compliance checking
   - Narrative quality assessment
   - Demographic distribution validation
   - Risk tier consistency analysis

## 💻 Usage Instructions

### Quick Start

```bash
# Method 1: Use the comprehensive batch file (Windows)
scripts\generate_50k_dataset.bat

# Method 2: Direct Python execution
python scripts/hseg_50k_final_generator.py

# Method 3: Custom configuration
python scripts/hseg_50k_final_generator.py --records 50000 --batch-size 5000
```

### System Requirements

#### Minimum Requirements
- Python 3.8+
- 4GB RAM
- 500MB free disk space
- Windows/Linux/macOS

#### Recommended Specifications
- Python 3.9+
- 8GB+ RAM
- 1GB+ free disk space
- SSD storage for faster I/O

#### Required Python Packages
```bash
pip install pandas numpy uuid datetime json logging
```

### Advanced Configuration

#### Custom Company Selection
```python
# Modify company data in hseg_50k_final_generator.py
custom_companies = {
    "Healthcare": {
        "Your Hospital": {
            "size": 50000,
            "culture": "patient_centered",
            "stress_factors": ["understaffing", "covid_impact"],
            "strengths": ["team_support", "innovation"],
            "cultural_phrases": ["patient-first culture", "healing environment"]
        }
    }
}
```

#### Narrative Template Customization
```python
# Add domain-specific scenarios
narrative_templates["Healthcare"]["crisis"].append(
    "New trauma scenario at {company} involving {culture_phrase}..."
)
```

#### Risk Distribution Adjustment
```python
# Modify risk tier weights
risk_weights = [0.10, 0.40, 0.35, 0.12, 0.03]  # Thriving, Safe, Mixed, At_Risk, Crisis
```

## 📈 Quality Assurance

### Validation Metrics

#### Schema Compliance (100 points)
- ✅ All expected columns present
- ✅ Correct data types
- ✅ No missing critical fields

#### Likert Scale Validity (100 points)
- ✅ All responses are integers 1-4
- ✅ Realistic distribution patterns
- ✅ Domain-specific bias adjustment

#### Narrative Quality (100 points)
- ✅ Appropriate length distribution (200-800 chars)
- ✅ High vocabulary diversity (>0.15 ratio)
- ✅ Company mentions in 80%+ of responses
- ✅ Psychological terminology usage
- ✅ Low repetition rate (<5%)

#### Demographic Realism (100 points)
- ✅ Domain distribution within 5% of target
- ✅ Age/gender distributions match workforce data
- ✅ Position/tenure realistic distributions

#### Risk Tier Consistency (100 points)
- ✅ Likert scores align with narrative sentiment
- ✅ Psychological terminology matches severity
- ✅ Risk distribution follows expected patterns

### Quality Scoring

| Score Range | Grade | Interpretation |
|-------------|-------|----------------|
| 95-100 | A+ | Excellent - Production ready |
| 90-94 | A | Very Good - Minor improvements |
| 85-89 | B+ | Good - Some refinements needed |
| 80-84 | B | Acceptable - Moderate improvements |
| 75-79 | C+ | Fair - Significant improvements |
| 70-74 | C | Needs Improvement - Major issues |
| <70 | D | Poor Quality - Regenerate recommended |

### Validation Execution

```bash
# Run comprehensive validation
python scripts/dataset_validator.py data/hseg_50k_synthetic_dataset.csv

# Generate validation report
python -c "
from scripts.dataset_validator import HSEGDatasetValidator
validator = HSEGDatasetValidator('data/hseg_50k_synthetic_dataset.csv')
results = validator.run_full_validation()
validator.save_validation_report()
print(validator.generate_summary_report())
"
```

## 🔬 NLP Training Applications

### Model Training Use Cases

#### 1. Crisis Detection Systems
```python
# Example: Binary classification for crisis vs non-crisis
import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer, AutoModelForSequenceClassification

df = pd.read_csv('data/hseg_50k_synthetic_dataset.csv')

# Create crisis labels
df['is_crisis'] = df['q24_text'].str.contains(
    'suicide|ptsd|breakdown|devastating|unbearable', case=False, na=False
)

# Training data preparation
X = df['q24_text'].values
y = df['is_crisis'].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
```

#### 2. Sentiment Analysis Models
```python
# Multi-class sentiment classification
sentiment_mapping = {
    'Crisis': 0, 'At_Risk': 1, 'Mixed': 2, 'Safe': 3, 'Thriving': 4
}

# Use estimated risk tiers as sentiment labels
df['sentiment_label'] = df['estimated_risk_tier'].map(sentiment_mapping)
```

#### 3. Named Entity Recognition
```python
# Extract workplace entities
entities = ['organization_name', 'department', 'position_level']
for entity in entities:
    # Train NER models to identify companies, roles, departments
    pass
```

#### 4. Topic Modeling
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# Discover workplace trauma themes
vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df['q24_text'])

lda = LatentDirichletAllocation(n_components=10, random_state=42)
lda.fit(tfidf_matrix)
```

#### 5. Text Generation Models
```python
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Fine-tune GPT-2 on workplace narratives
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')

# Fine-tuning on domain-specific narratives
training_texts = df['q24_text'].tolist()
```

### Performance Benchmarks

#### Expected Model Performance
- **Crisis Detection**: 90%+ F1-score
- **Sentiment Classification**: 85%+ accuracy across 5 classes
- **Topic Coherence**: 0.5+ coherence score
- **Entity Recognition**: 95%+ precision for company names
- **Text Generation**: High BLEU scores for domain consistency

#### Evaluation Metrics
```python
from sklearn.metrics import classification_report, confusion_matrix

# Comprehensive evaluation
def evaluate_model(y_true, y_pred, model_type):
    print(f"\n{model_type} Performance:")
    print(classification_report(y_true, y_pred))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_true, y_pred))
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Memory Errors
**Problem**: Out of memory during generation
**Solution**:
- Reduce batch size to 2,500 or 1,000
- Close other applications
- Use system with more RAM

```python
generator.generate_dataset(total_records=50000, batch_size=2500)
```

#### 2. Generation Time Too Long
**Problem**: Process takes >60 minutes
**Solution**:
- Use SSD storage
- Increase batch size if memory allows
- Run on faster CPU

#### 3. Validation Failures
**Problem**: Quality score below 80
**Solution**:
- Check narrative template quality
- Verify demographic distributions
- Adjust risk tier probabilities

#### 4. Insufficient Disk Space
**Problem**: Generation fails due to space
**Solution**:
- Free up 1GB+ disk space
- Use external storage
- Generate smaller dataset initially

### Performance Optimization

#### Memory Management
```python
import gc

# Force garbage collection between batches
def generate_batch_optimized(self, batch_size, batch_num):
    batch_records = self.generate_batch(batch_size, batch_num)
    gc.collect()  # Force cleanup
    return batch_records
```

#### Parallel Processing
```python
from multiprocessing import Pool

# Parallelize narrative generation (advanced)
def parallel_narrative_generation(args):
    domain, company, risk_tier, question_type = args
    return generate_rich_response(domain, company, risk_tier, question_type)
```

## 📚 Technical References

### Related Documentation
- [HSEG System Architecture](../README.md)
- [API Integration Guide](../app/api/README.md)
- [Database Schema Documentation](../app/models/README.md)
- [ML Pipeline Documentation](../app/core/README.md)

### Research Background
- Workplace psychological safety assessment methods
- Synthetic data generation for NLP training
- Trauma-informed dataset creation principles
- Enterprise-scale ML model training approaches

### Code Repository Structure
```
ai-modeling/
├── scripts/
│   ├── hseg_50k_final_generator.py      # Main generator
│   ├── advanced_narrative_generator.py  # Narrative engine
│   ├── text_variation_engine.py        # Linguistic diversity
│   ├── dataset_validator.py            # Quality assurance
│   └── generate_50k_dataset.bat        # Windows execution
├── data/
│   ├── hseg_50k_synthetic_dataset.csv  # Output dataset
│   └── validation_report.json          # Quality report
└── docs/
    └── 50K_Dataset_Generation_Guide.md # This guide
```

## 🎯 Next Steps

### Immediate Actions
1. **Execute Generation**: Run the batch file or Python script
2. **Validate Quality**: Use dataset validator to ensure quality
3. **Begin Training**: Start NLP model development with dataset

### Advanced Applications
1. **Custom Domain Addition**: Add new industry sectors
2. **Language Expansion**: Generate multilingual datasets
3. **Temporal Variation**: Create longitudinal survey responses
4. **Integration Testing**: Validate with existing HSEG API

### Production Deployment
1. **Model Training**: Use dataset for production model training
2. **Performance Monitoring**: Track model accuracy with synthetic data
3. **Continuous Improvement**: Regenerate with updated narratives
4. **Stakeholder Validation**: Verify authenticity with domain experts

---

**HSEG 50K Dataset Generator** - Enterprise-scale synthetic data for transforming workplace psychological safety through AI-powered analysis.