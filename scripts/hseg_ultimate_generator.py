#!/usr/bin/env python3
"""
HSEG Ultimate Generator - 55 Companies with AI-Powered Narratives
Complete synthetic dataset generation with prompt-engineered human-like trauma responses
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import uuid
import os
import gc
import time
import logging
import psutil
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

# Import our modules
from expanded_companies_55 import EXPANDED_COMPANIES, get_company_distribution
from gen_ai_narrative_engine import GenerativeAINarrativeEngine, TraumaContext

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set seeds for reproducibility
np.random.seed(42)
random.seed(42)

class HSEGUltimateGenerator:
    """
    Ultimate HSEG synthetic data generator with 55 companies and AI-powered narratives
    """

    def __init__(self):
        logger.info("Initializing HSEG Ultimate Generator with 55 companies...")

        # Load expanded company database
        self.companies = EXPANDED_COMPANIES
        self.company_distribution = get_company_distribution()

        # Initialize Generative AI narrative engine
        self.ai_narrative_engine = GenerativeAINarrativeEngine(ai_provider="openai")

        # Calculate total companies
        self.total_companies = sum(len(companies) for companies in self.companies.values())
        logger.info(f"Loaded {self.total_companies} companies across all domains")

        # Demographics and distributions
        self.initialize_distributions()

        logger.info("Ultimate Generator initialization complete.")

    def initialize_distributions(self):
        """Initialize demographic and risk distributions"""

        # Risk tier distribution for realistic psychological safety patterns
        self.risk_tiers = ["Thriving", "Safe", "Mixed", "At_Risk", "Crisis"]
        self.risk_weights = [0.15, 0.35, 0.30, 0.15, 0.05]

        # Demographics distributions
        self.age_ranges = ["22-24", "25-34", "35-44", "45-54", "55+"]
        self.age_weights = [0.15, 0.35, 0.30, 0.15, 0.05]

        self.genders = ["Woman", "Man", "Non-binary", "Prefer not to say"]
        self.gender_weights = [0.52, 0.45, 0.02, 0.01]

        self.tenures = ["<1_year", "1-3_years", "3-7_years", "7+_years"]
        self.tenure_weights = [0.20, 0.40, 0.25, 0.15]

        self.positions = ["Entry", "Mid", "Senior", "Executive"]
        self.position_weights = [0.25, 0.45, 0.25, 0.05]

        self.departments = ["Engineering", "Operations", "Sales_Marketing", "HR", "Finance", "Other"]
        self.dept_weights = [0.30, 0.20, 0.15, 0.10, 0.10, 0.15]

    def generate_likert_responses(self, risk_tier: str, domain: str) -> List[int]:
        """Generate realistic Likert scale responses (1-4 integers)"""

        # Base weights for each risk tier
        if risk_tier == "Thriving":
            weights = [0.05, 0.15, 0.35, 0.45]  # Mostly positive
        elif risk_tier == "Safe":
            weights = [0.10, 0.25, 0.40, 0.25]  # Balanced positive
        elif risk_tier == "Mixed":
            weights = [0.20, 0.30, 0.30, 0.20]  # Evenly distributed
        elif risk_tier == "At_Risk":
            weights = [0.35, 0.35, 0.20, 0.10]  # Mostly negative
        else:  # Crisis
            weights = [0.50, 0.35, 0.10, 0.05]  # Heavily negative

        # Domain-specific adjustments for workplace stress
        if domain == "Healthcare":
            # Healthcare has higher stress due to life-or-death situations
            weights = [w * m for w, m in zip(weights, [1.2, 1.1, 0.9, 0.8])]
        elif domain == "University":
            # Academic pressure and funding stress
            weights = [w * m for w, m in zip(weights, [1.1, 1.1, 0.95, 0.85])]

        # Normalize weights
        total = sum(weights)
        weights = [w/total for w in weights]

        # Generate 22 survey responses as integers
        return [np.random.choice([1, 2, 3, 4], p=weights) for _ in range(22)]

    def generate_ai_narratives(self, domain: str, company: str, risk_tier: str,
                              demographics: Dict[str, Any], company_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate AI-powered human-like narratives using real AI APIs"""

        # Select specific trauma based on domain
        domain_traumas = {
            "Healthcare": ["patient deaths during COVID surge", "medical error trauma", "violence from patients", "moral injury from resource scarcity"],
            "University": ["advisor psychological abuse", "sexual harassment with retaliation", "research theft", "academic bullying"],
            "Business": ["manager verbal abuse", "workplace harassment", "discrimination", "layoff trauma", "performance gaslighting"]
        }

        specific_trauma = random.choice(domain_traumas.get(domain, ["workplace stress"]))
        culture_phrase = random.choice(company_data.get("cultural_phrases", ["workplace culture"]))

        # Create trauma context for AI generation
        context = TraumaContext(
            company=company,
            domain=domain,
            risk_tier=risk_tier,
            demographics=demographics,
            company_culture=culture_phrase,
            specific_trauma=specific_trauma
        )

        # Generate narratives using real AI APIs
        narratives = {}
        try:
            narratives["q23"] = self.ai_narrative_engine.generate_trauma_narrative(context, "q23_change")
            narratives["q24"] = self.ai_narrative_engine.generate_trauma_narrative(context, "q24_mental_health")
            narratives["q25"] = self.ai_narrative_engine.generate_trauma_narrative(context, "q25_strength")
        except Exception as e:
            logger.warning(f"AI generation failed for {company}, using fallbacks: {e}")
            # Fallback to basic responses if AI fails
            narratives = {
                "q23": f"The systemic issues at {company} need complete overhaul. The {culture_phrase} has created an environment where trauma is normalized.",
                "q24": f"Working at {company} has severely impacted my mental health. The {specific_trauma} has left me with anxiety and depression.",
                "q25": f"Despite the challenges at {company}, the meaningful work and some supportive colleagues provide hope during difficult times."
            }

        return narratives

    def check_memory_usage(self) -> Tuple[float, bool]:
        """Check current memory usage and return percentage and if it's critical"""
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        is_critical = memory_percent > 85

        if is_critical:
            logger.warning(f"High memory usage detected: {memory_percent:.1f}%")

        return memory_percent, is_critical

    def generate_batch(self, batch_size: int, batch_num: int, target_distribution: Dict) -> List[Dict]:
        """Generate a batch of synthetic responses with realistic distribution"""

        # Check memory before starting batch
        memory_percent, is_critical = self.check_memory_usage()
        if is_critical:
            logger.warning(f"Memory usage is critical ({memory_percent:.1f}%), reducing batch size")
            batch_size = min(batch_size, 500)  # Reduce to 500 if memory is critical

        logger.info(f"Generating batch {batch_num} with {batch_size} records... (Memory: {memory_percent:.1f}%)")
        batch_records = []

        # Create list of (domain, company) pairs based on target distribution
        company_list = []
        for domain, companies in target_distribution.items():
            for company, count in companies.items():
                company_list.extend([(domain, company)] * count)

        # Shuffle to randomize order
        random.shuffle(company_list)

        # Take subset for this batch
        batch_companies = company_list[:batch_size]

        for i, (domain, company_name) in enumerate(batch_companies):
            if (i + 1) % 200 == 0:
                logger.info(f"  Progress: {i + 1}/{batch_size} records in batch {batch_num}")

            company_data = self.companies[domain][company_name]

            # Generate demographics
            risk_tier = np.random.choice(self.risk_tiers, p=self.risk_weights)
            age_range = np.random.choice(self.age_ranges, p=self.age_weights)
            gender = np.random.choice(self.genders, p=self.gender_weights)
            tenure = np.random.choice(self.tenures, p=self.tenure_weights)
            position = np.random.choice(self.positions, p=self.position_weights)
            department = np.random.choice(self.departments, p=self.dept_weights)
            supervises = np.random.choice([True, False], p=[0.3, 0.7])

            demographics = {
                "age_range": age_range,
                "gender_identity": gender,
                "tenure_range": tenure,
                "position_level": position,
                "department": department,
                "supervises_others": supervises
            }

            # Generate Likert scale responses
            survey_responses = self.generate_likert_responses(risk_tier, domain)

            # Generate AI-powered narratives
            narratives = self.generate_ai_narratives(domain, company_name, risk_tier, demographics, company_data)

            # Generate submission date (last year)
            start_date = datetime.now() - timedelta(days=365)
            random_days = random.randint(0, 365)
            submission_date = start_date + timedelta(days=random_days)

            # Create record
            record = {
                "response_id": f"resp_{str(uuid.uuid4())[:8]}",
                "organization_name": company_name,
                "domain": domain,
                "employee_count": company_data["size"],
                "department": department,
                "position_level": position,
                "age_range": age_range,
                "gender_identity": gender,
                "tenure_range": tenure,
                "supervises_others": supervises,
                "submission_date": submission_date.strftime("%Y-%m-%d")
            }

            # Add survey responses (Q1-Q22)
            for j, response in enumerate(survey_responses, 1):
                record[f"q{j}"] = response

            # Add AI-generated narrative responses
            record["q23_text"] = narratives.get("q23", f"Changes needed at {company_name}")
            record["q24_text"] = narratives.get("q24", f"Mental health impact at {company_name}")
            record["q25_text"] = narratives.get("q25", f"Workplace strengths at {company_name}")

            batch_records.append(record)

        logger.info(f"Batch {batch_num} generation complete.")
        return batch_records

    def generate_dataset(self, total_records: int = 50000, batch_size: int = 1000) -> str:
        """Generate complete 50K dataset with 55 companies and AI narratives"""

        logger.info(f"Starting generation of {total_records:,} records across {self.total_companies} companies...")
        start_time = time.time()

        # Create output directory
        os.makedirs("data", exist_ok=True)

        # Calculate distribution for 50K records across 55 companies
        distribution = self.company_distribution

        # Use progressive saving instead of keeping everything in memory
        output_path = "data/hseg_55companies_ai_dataset.csv"
        first_batch = True
        total_saved_records = 0
        num_batches = (total_records + batch_size - 1) // batch_size

        for batch_num in range(1, num_batches + 1):
            current_batch_size = min(batch_size, total_records - (batch_num - 1) * batch_size)

            # Calculate batch distribution
            batch_distribution = {}
            for domain, companies in distribution.items():
                batch_distribution[domain] = {}
                for company, total_count in companies.items():
                    # Calculate how many records this company gets in this batch
                    batch_count = (total_count * current_batch_size) // total_records
                    if batch_count > 0:
                        batch_distribution[domain][company] = batch_count

            batch_records = self.generate_batch(current_batch_size, batch_num, batch_distribution)

            # Convert batch to DataFrame and save immediately
            batch_df = pd.DataFrame(batch_records)

            if first_batch:
                # Save with header for first batch
                batch_df.to_csv(output_path, index=False, mode='w')
                first_batch = False
            else:
                # Append without header for subsequent batches
                batch_df.to_csv(output_path, index=False, mode='a', header=False)

            total_saved_records += len(batch_records)

            # Clear batch data from memory immediately
            del batch_records
            del batch_df

            # Force garbage collection after each batch
            gc.collect()

            logger.info(f"Completed batch {batch_num}/{num_batches}. Total records saved: {total_saved_records:,}")

        # Read final dataset for statistics (more memory efficient than keeping in memory)
        logger.info("Reading final dataset for statistics...")
        df = pd.read_csv(output_path)

        # Reorder columns if needed (file already saved progressively)
        columns_order = [
            "response_id", "organization_name", "domain", "employee_count",
            "department", "position_level", "age_range", "gender_identity",
            "tenure_range", "supervises_others"
        ] + [f"q{i}" for i in range(1, 23)] + [
            "q23_text", "q24_text", "q25_text", "submission_date"
        ]

        # Only reorder if columns are not in correct order
        if list(df.columns) != columns_order:
            df = df[columns_order]
            df.to_csv(output_path, index=False)

        end_time = time.time()
        generation_time = end_time - start_time

        # Generate comprehensive statistics
        self.generate_statistics(df, output_path, generation_time)

        return output_path

    def generate_statistics(self, df: pd.DataFrame, output_path: str, generation_time: float):
        """Generate comprehensive dataset statistics"""

        logger.info("Generating comprehensive statistics...")

        stats = {
            "generation_info": {
                "total_records": len(df),
                "total_companies": self.total_companies,
                "generation_time_minutes": generation_time / 60,
                "file_size_mb": os.path.getsize(output_path) / (1024 * 1024),
                "records_per_company": len(df) // self.total_companies
            },
            "domain_distribution": dict(df['domain'].value_counts()),
            "company_distribution": dict(df['organization_name'].value_counts()),
            "risk_analysis": self._analyze_risk_distribution(df),
            "narrative_analysis": self._analyze_narrative_quality(df),
            "demographic_analysis": self._analyze_demographics(df)
        }

        # Print summary
        print(f"\n🎯 HSEG Ultimate Dataset Generation Complete!")
        print(f"=" * 60)
        print(f"📊 Total Records: {stats['generation_info']['total_records']:,}")
        print(f"🏢 Total Companies: {stats['generation_info']['total_companies']}")
        print(f"⏱️  Generation Time: {stats['generation_info']['generation_time_minutes']:.1f} minutes")
        print(f"💾 File Size: {stats['generation_info']['file_size_mb']:.1f} MB")
        print(f"📈 Records per Company: ~{stats['generation_info']['records_per_company']:,}")

        print(f"\n📊 Domain Distribution:")
        for domain, count in stats['domain_distribution'].items():
            percentage = (count / len(df)) * 100
            print(f"   {domain}: {count:,} records ({percentage:.1f}%)")

        print(f"\n🏢 Top 10 Companies by Records:")
        for company, count in list(stats['company_distribution'].items())[:10]:
            print(f"   {company}: {count:,} records")

        print(f"\n📝 Narrative Quality:")
        print(f"   Q23 avg length: {stats['narrative_analysis']['q23_avg_length']:.0f} chars")
        print(f"   Q24 avg length: {stats['narrative_analysis']['q24_avg_length']:.0f} chars")
        print(f"   Q25 avg length: {stats['narrative_analysis']['q25_avg_length']:.0f} chars")

        print(f"\n🎯 Risk Distribution:")
        for tier, count in stats['risk_analysis'].items():
            percentage = (count / len(df)) * 100
            print(f"   {tier}: {count:,} records ({percentage:.1f}%)")

    def _analyze_risk_distribution(self, df: pd.DataFrame) -> Dict[str, int]:
        """Analyze risk tier distribution based on Likert scores"""
        likert_columns = [f"q{i}" for i in range(1, 23)]
        df['avg_likert'] = df[likert_columns].mean(axis=1)

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

        df['estimated_risk_tier'] = df['avg_likert'].apply(estimate_risk_tier)
        return dict(df['estimated_risk_tier'].value_counts())

    def _analyze_narrative_quality(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analyze narrative text quality"""
        return {
            "q23_avg_length": df['q23_text'].str.len().mean(),
            "q24_avg_length": df['q24_text'].str.len().mean(),
            "q25_avg_length": df['q25_text'].str.len().mean(),
        }

    def _analyze_demographics(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """Analyze demographic distributions"""
        return {
            "age_distribution": dict(df['age_range'].value_counts()),
            "gender_distribution": dict(df['gender_identity'].value_counts()),
            "position_distribution": dict(df['position_level'].value_counts()),
            "department_distribution": dict(df['department'].value_counts())
        }

def main():
    """Main execution function"""
    print("🚀 HSEG Ultimate Generator - 55 Companies with AI Narratives")
    print("=" * 70)
    print("🏢 Companies: 55 organizations across Healthcare, University, Business")
    print("🤖 AI Engine: Prompt-engineered human-like trauma narratives")
    print("📊 Output: Configurable dataset size (default: 50,000)")
    print("=" * 70)

    # Check available memory and suggest appropriate dataset size
    memory = psutil.virtual_memory()
    available_gb = memory.available / (1024**3)

    if available_gb < 2:
        suggested_records = 5000
        print(f"⚠️  Low memory detected ({available_gb:.1f}GB available)")
        print(f"🎯 Suggested dataset size: {suggested_records:,} records")
    elif available_gb < 4:
        suggested_records = 10000
        print(f"⚠️  Limited memory detected ({available_gb:.1f}GB available)")
        print(f"🎯 Suggested dataset size: {suggested_records:,} records")
    else:
        suggested_records = 50000
        print(f"✅ Sufficient memory available ({available_gb:.1f}GB)")
        print(f"🎯 Full dataset size: {suggested_records:,} records")

    generator = HSEGUltimateGenerator()

    # Use memory-optimized batch size
    optimal_batch_size = min(1000, suggested_records // 10)
    output_file = generator.generate_dataset(total_records=suggested_records, batch_size=optimal_batch_size)

    print(f"\n✅ Generation completed successfully!")
    print(f"📁 Output file: {output_file}")
    print(f"🎯 Ready for enterprise NLP model training!")
    print(f"🤖 AI-powered narratives provide human-like authenticity")

if __name__ == "__main__":
    main()