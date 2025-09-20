#!/usr/bin/env python3
"""
HSEG Dataset Validator and Quality Assurance System
Comprehensive validation of synthetic dataset quality for NLP training
"""

import pandas as pd
import numpy as np
import json
import re
from typing import Dict, List, Tuple, Any
from collections import Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HSEGDatasetValidator:
    """
    Comprehensive dataset validation system for quality assurance
    """

    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.df = None
        self.validation_results = {}

    def load_dataset(self) -> bool:
        """Load and perform initial validation of dataset"""
        try:
            logger.info(f"Loading dataset from {self.dataset_path}")
            self.df = pd.read_csv(self.dataset_path)
            logger.info(f"Dataset loaded: {len(self.df)} rows, {len(self.df.columns)} columns")
            return True
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            return False

    def validate_schema(self) -> Dict[str, Any]:
        """Validate dataset schema and structure"""
        logger.info("Validating dataset schema...")

        expected_columns = [
            "response_id", "organization_name", "domain", "employee_count",
            "department", "position_level", "age_range", "gender_identity",
            "tenure_range", "supervises_others"
        ] + [f"q{i}" for i in range(1, 23)] + [
            "q23_text", "q24_text", "q25_text", "submission_date"
        ]

        schema_validation = {
            "total_rows": len(self.df),
            "total_columns": len(self.df.columns),
            "expected_columns": len(expected_columns),
            "missing_columns": [],
            "extra_columns": [],
            "column_match": True
        }

        # Check for missing columns
        missing = set(expected_columns) - set(self.df.columns)
        if missing:
            schema_validation["missing_columns"] = list(missing)
            schema_validation["column_match"] = False

        # Check for extra columns
        extra = set(self.df.columns) - set(expected_columns)
        if extra:
            schema_validation["extra_columns"] = list(extra)

        # Data type validation
        schema_validation["data_types"] = {}
        for col in self.df.columns:
            schema_validation["data_types"][col] = str(self.df[col].dtype)

        return schema_validation

    def validate_likert_responses(self) -> Dict[str, Any]:
        """Validate Likert scale responses (Q1-Q22)"""
        logger.info("Validating Likert scale responses...")

        likert_validation = {
            "valid_responses": True,
            "invalid_responses": {},
            "response_distribution": {},
            "domain_bias_analysis": {}
        }

        likert_columns = [f"q{i}" for i in range(1, 23)]

        for col in likert_columns:
            if col in self.df.columns:
                # Check for valid range (1-4)
                invalid_values = self.df[~self.df[col].isin([1, 2, 3, 4])][col]
                if len(invalid_values) > 0:
                    likert_validation["valid_responses"] = False
                    likert_validation["invalid_responses"][col] = {
                        "count": len(invalid_values),
                        "values": invalid_values.unique().tolist()
                    }

                # Response distribution
                likert_validation["response_distribution"][col] = dict(
                    self.df[col].value_counts().sort_index()
                )

        # Domain bias analysis
        for domain in self.df['domain'].unique():
            domain_data = self.df[self.df['domain'] == domain]
            domain_means = {col: domain_data[col].mean() for col in likert_columns if col in self.df.columns}
            likert_validation["domain_bias_analysis"][domain] = domain_means

        return likert_validation

    def validate_narrative_quality(self) -> Dict[str, Any]:
        """Validate narrative text quality and authenticity"""
        logger.info("Validating narrative text quality...")

        narrative_validation = {
            "length_analysis": {},
            "vocabulary_diversity": {},
            "sentiment_distribution": {},
            "company_mention_analysis": {},
            "psychological_terminology": {},
            "repetition_analysis": {}
        }

        text_columns = ["q23_text", "q24_text", "q25_text"]

        for col in text_columns:
            if col in self.df.columns:
                # Length analysis
                lengths = self.df[col].str.len()
                narrative_validation["length_analysis"][col] = {
                    "mean_length": lengths.mean(),
                    "median_length": lengths.median(),
                    "min_length": lengths.min(),
                    "max_length": lengths.max(),
                    "std_length": lengths.std(),
                    "too_short_count": len(lengths[lengths < 50]),
                    "too_long_count": len(lengths[lengths > 1000])
                }

                # Vocabulary diversity
                all_text = ' '.join(self.df[col].astype(str))
                words = re.findall(r'\b\w+\b', all_text.lower())
                unique_words = set(words)
                narrative_validation["vocabulary_diversity"][col] = {
                    "total_words": len(words),
                    "unique_words": len(unique_words),
                    "diversity_ratio": len(unique_words) / len(words) if words else 0
                }

                # Company mention analysis
                company_mentions = 0
                for text in self.df[col]:
                    if pd.notna(text):
                        # Count mentions of company names
                        for company in self.df['organization_name'].unique():
                            if company.lower() in text.lower():
                                company_mentions += 1
                                break

                narrative_validation["company_mention_analysis"][col] = {
                    "responses_with_company_mentions": company_mentions,
                    "percentage": (company_mentions / len(self.df)) * 100
                }

        # Psychological terminology analysis
        psych_terms = [
            "anxiety", "depression", "ptsd", "trauma", "panic", "stress",
            "burnout", "overwhelmed", "exhausted", "therapy", "counseling",
            "mental health", "psychological", "emotional", "breakdown",
            "suicide", "self-harm", "crisis", "support", "resilience"
        ]

        for col in text_columns:
            if col in self.df.columns:
                term_counts = {}
                for term in psych_terms:
                    count = self.df[col].str.lower().str.contains(term, na=False).sum()
                    if count > 0:
                        term_counts[term] = count

                narrative_validation["psychological_terminology"][col] = term_counts

        # Repetition analysis (check for identical responses)
        for col in text_columns:
            if col in self.df.columns:
                duplicates = self.df[col].duplicated().sum()
                narrative_validation["repetition_analysis"][col] = {
                    "duplicate_responses": duplicates,
                    "unique_responses": self.df[col].nunique(),
                    "repetition_rate": (duplicates / len(self.df)) * 100
                }

        return narrative_validation

    def validate_demographic_distributions(self) -> Dict[str, Any]:
        """Validate demographic distributions for realism"""
        logger.info("Validating demographic distributions...")

        demo_validation = {
            "domain_distribution": {},
            "company_distribution": {},
            "age_distribution": {},
            "gender_distribution": {},
            "position_distribution": {},
            "tenure_distribution": {},
            "realistic_distributions": True,
            "distribution_warnings": []
        }

        # Domain distribution
        domain_dist = dict(self.df['domain'].value_counts(normalize=True))
        demo_validation["domain_distribution"] = domain_dist

        # Check if domain distribution is reasonable (Healthcare 30%, University 25%, Business 45%)
        expected_domain = {"Healthcare": 0.30, "University": 0.25, "Business": 0.45}
        for domain, expected in expected_domain.items():
            actual = domain_dist.get(domain, 0)
            if abs(actual - expected) > 0.05:  # 5% tolerance
                demo_validation["distribution_warnings"].append(
                    f"Domain {domain}: expected {expected:.1%}, got {actual:.1%}"
                )

        # Company distribution
        company_dist = dict(self.df['organization_name'].value_counts())
        demo_validation["company_distribution"] = company_dist

        # Age distribution
        age_dist = dict(self.df['age_range'].value_counts(normalize=True))
        demo_validation["age_distribution"] = age_dist

        # Gender distribution
        gender_dist = dict(self.df['gender_identity'].value_counts(normalize=True))
        demo_validation["gender_distribution"] = gender_dist

        # Position distribution
        position_dist = dict(self.df['position_level'].value_counts(normalize=True))
        demo_validation["position_distribution"] = position_dist

        # Tenure distribution
        tenure_dist = dict(self.df['tenure_range'].value_counts(normalize=True))
        demo_validation["tenure_distribution"] = tenure_dist

        return demo_validation

    def validate_risk_tier_consistency(self) -> Dict[str, Any]:
        """Validate consistency between Likert responses and narrative content"""
        logger.info("Validating risk tier consistency...")

        consistency_validation = {
            "likert_narrative_alignment": {},
            "risk_tier_estimates": {},
            "inconsistency_warnings": []
        }

        # Calculate average Likert scores
        likert_columns = [f"q{i}" for i in range(1, 23)]
        self.df['avg_likert'] = self.df[likert_columns].mean(axis=1)

        # Estimate risk tiers based on Likert averages
        def estimate_risk_tier(avg_score):
            if avg_score <= 2.0:
                return "Crisis"
            elif avg_score <= 2.5:
                return "At_Risk"
            elif avg_score <= 3.0:
                return "Mixed"
            elif avg_score <= 3.5:
                return "Safe"
            else:
                return "Thriving"

        self.df['estimated_risk_tier'] = self.df['avg_likert'].apply(estimate_risk_tier)

        risk_distribution = dict(self.df['estimated_risk_tier'].value_counts(normalize=True))
        consistency_validation["risk_tier_estimates"] = risk_distribution

        # Analyze narrative sentiment vs Likert scores
        crisis_indicators = ["suicide", "ptsd", "breakdown", "crisis", "devastating", "unbearable"]
        positive_indicators = ["supportive", "helpful", "positive", "thriving", "excellent"]

        crisis_narratives = 0
        positive_narratives = 0

        for idx, row in self.df.iterrows():
            q24_text = str(row['q24_text']).lower()
            avg_likert = row['avg_likert']

            has_crisis_terms = any(term in q24_text for term in crisis_indicators)
            has_positive_terms = any(term in q24_text for term in positive_indicators)

            if has_crisis_terms:
                crisis_narratives += 1
                if avg_likert > 3.0:  # High Likert but crisis narrative
                    consistency_validation["inconsistency_warnings"].append(
                        f"Row {idx}: Crisis narrative with high Likert score ({avg_likert:.1f})"
                    )

            if has_positive_terms:
                positive_narratives += 1
                if avg_likert < 2.5:  # Low Likert but positive narrative
                    consistency_validation["inconsistency_warnings"].append(
                        f"Row {idx}: Positive narrative with low Likert score ({avg_likert:.1f})"
                    )

        consistency_validation["narrative_sentiment_analysis"] = {
            "crisis_narratives": crisis_narratives,
            "positive_narratives": positive_narratives,
            "total_analyzed": len(self.df)
        }

        return consistency_validation

    def validate_data_completeness(self) -> Dict[str, Any]:
        """Validate data completeness and missing values"""
        logger.info("Validating data completeness...")

        completeness_validation = {
            "missing_values": {},
            "completeness_rate": {},
            "critical_missing": []
        }

        # Check missing values for each column
        for col in self.df.columns:
            missing_count = self.df[col].isnull().sum()
            completeness_rate = ((len(self.df) - missing_count) / len(self.df)) * 100

            completeness_validation["missing_values"][col] = missing_count
            completeness_validation["completeness_rate"][col] = completeness_rate

            # Flag critical missing data
            if missing_count > 0:
                completeness_validation["critical_missing"].append({
                    "column": col,
                    "missing_count": missing_count,
                    "percentage": 100 - completeness_rate
                })

        return completeness_validation

    def run_full_validation(self) -> Dict[str, Any]:
        """Run complete validation suite"""
        logger.info("Running full dataset validation...")

        if not self.load_dataset():
            return {"error": "Failed to load dataset"}

        validation_results = {
            "dataset_info": {
                "file_path": self.dataset_path,
                "file_size_mb": round(pd.io.common.file_size(self.dataset_path) / (1024*1024), 2),
                "validation_timestamp": pd.Timestamp.now().isoformat()
            },
            "schema_validation": self.validate_schema(),
            "likert_validation": self.validate_likert_responses(),
            "narrative_validation": self.validate_narrative_quality(),
            "demographic_validation": self.validate_demographic_distributions(),
            "consistency_validation": self.validate_risk_tier_consistency(),
            "completeness_validation": self.validate_data_completeness()
        }

        # Generate overall quality score
        quality_score = self._calculate_quality_score(validation_results)
        validation_results["overall_quality"] = quality_score

        self.validation_results = validation_results
        return validation_results

    def _calculate_quality_score(self, results: Dict) -> Dict[str, Any]:
        """Calculate overall dataset quality score"""
        score_components = {
            "schema_compliance": 100 if results["schema_validation"]["column_match"] else 70,
            "likert_validity": 100 if results["likert_validation"]["valid_responses"] else 50,
            "narrative_diversity": min(100, results["narrative_validation"]["vocabulary_diversity"].get("q24_text", {}).get("diversity_ratio", 0) * 500),
            "demographic_realism": 100 - len(results["demographic_validation"]["distribution_warnings"]) * 10,
            "consistency": 100 - len(results["consistency_validation"]["inconsistency_warnings"]) * 2,
            "completeness": min(100, sum(results["completeness_validation"]["completeness_rate"].values()) / len(results["completeness_validation"]["completeness_rate"]))
        }

        overall_score = sum(score_components.values()) / len(score_components)

        return {
            "overall_score": round(overall_score, 2),
            "component_scores": score_components,
            "quality_grade": self._get_quality_grade(overall_score),
            "recommendations": self._generate_recommendations(results, score_components)
        }

    def _get_quality_grade(self, score: float) -> str:
        """Convert quality score to letter grade"""
        if score >= 95:
            return "A+ (Excellent)"
        elif score >= 90:
            return "A (Very Good)"
        elif score >= 85:
            return "B+ (Good)"
        elif score >= 80:
            return "B (Acceptable)"
        elif score >= 75:
            return "C+ (Fair)"
        elif score >= 70:
            return "C (Needs Improvement)"
        else:
            return "D (Poor Quality)"

    def _generate_recommendations(self, results: Dict, scores: Dict) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []

        if scores["schema_compliance"] < 100:
            recommendations.append("Fix missing or extra columns to match expected schema")

        if scores["likert_validity"] < 100:
            recommendations.append("Correct invalid Likert scale responses (must be 1-4)")

        if scores["narrative_diversity"] < 80:
            recommendations.append("Increase vocabulary diversity in narrative responses")

        if scores["demographic_realism"] < 90:
            recommendations.append("Adjust demographic distributions to match expected ratios")

        if scores["consistency"] < 90:
            recommendations.append("Improve alignment between Likert scores and narrative sentiment")

        if scores["completeness"] < 100:
            recommendations.append("Address missing values in dataset")

        if not recommendations:
            recommendations.append("Dataset quality is excellent - ready for production use")

        return recommendations

    def save_validation_report(self, output_path: str = "data/validation_report.json"):
        """Save validation results to JSON file"""
        if self.validation_results:
            with open(output_path, 'w') as f:
                json.dump(self.validation_results, f, indent=2, default=str)
            logger.info(f"Validation report saved to {output_path}")
        else:
            logger.warning("No validation results to save")

    def generate_summary_report(self) -> str:
        """Generate human-readable summary report"""
        if not self.validation_results:
            return "No validation results available"

        results = self.validation_results
        overall = results["overall_quality"]

        report = f"""
HSEG Dataset Validation Report
================================

Dataset: {results['dataset_info']['file_path']}
Size: {results['dataset_info']['file_size_mb']} MB
Records: {results['schema_validation']['total_rows']:,}
Validation Date: {results['dataset_info']['validation_timestamp']}

OVERALL QUALITY SCORE: {overall['overall_score']}/100 ({overall['quality_grade']})

COMPONENT SCORES:
- Schema Compliance: {overall['component_scores']['schema_compliance']:.1f}/100
- Likert Validity: {overall['component_scores']['likert_validity']:.1f}/100
- Narrative Diversity: {overall['component_scores']['narrative_diversity']:.1f}/100
- Demographic Realism: {overall['component_scores']['demographic_realism']:.1f}/100
- Data Consistency: {overall['component_scores']['consistency']:.1f}/100
- Completeness: {overall['component_scores']['completeness']:.1f}/100

NARRATIVE QUALITY:
- Average Q24 length: {results['narrative_validation']['length_analysis']['q24_text']['mean_length']:.0f} characters
- Vocabulary diversity: {results['narrative_validation']['vocabulary_diversity']['q24_text']['diversity_ratio']:.3f}
- Company mentions: {results['narrative_validation']['company_mention_analysis']['q24_text']['percentage']:.1f}%

RISK DISTRIBUTION:
"""
        for tier, percentage in results['consistency_validation']['risk_tier_estimates'].items():
            report += f"- {tier}: {percentage:.1%}\n"

        report += f"""
RECOMMENDATIONS:
"""
        for i, rec in enumerate(overall['recommendations'], 1):
            report += f"{i}. {rec}\n"

        return report

def main():
    """Main validation execution"""
    import sys

    dataset_path = "data/hseg_50k_synthetic_dataset.csv"

    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]

    print("🔍 HSEG Dataset Validator")
    print("=" * 40)

    validator = HSEGDatasetValidator(dataset_path)
    results = validator.run_full_validation()

    if "error" in results:
        print(f"❌ Validation failed: {results['error']}")
        return

    # Save detailed results
    validator.save_validation_report()

    # Print summary
    summary = validator.generate_summary_report()
    print(summary)

    # Print final status
    score = results["overall_quality"]["overall_score"]
    if score >= 90:
        print("✅ Dataset is ready for production use!")
    elif score >= 80:
        print("⚠️  Dataset is acceptable but could be improved")
    else:
        print("❌ Dataset needs significant improvement before use")

if __name__ == "__main__":
    main()