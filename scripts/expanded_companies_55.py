#!/usr/bin/env python3
"""
Expanded Company Database - 55 Organizations
Comprehensive workplace culture profiles for realistic narrative generation
"""

# Expanded company database with 55 organizations
EXPANDED_COMPANIES = {
    "Healthcare": {
        # Major Health Systems (20 companies)
        "Kaiser Permanente": {
            "size": 218000, "culture": "integrated_care", "region": "West Coast",
            "stress_factors": ["hmo_pressure", "patient_deaths", "understaffing", "covid_trauma"],
            "strengths": ["comprehensive_benefits", "job_security", "innovation", "integrated_model"],
            "cultural_phrases": ["HMO model pressures", "integrated care challenges", "Permanente culture"]
        },
        "Mayo Clinic": {
            "size": 73000, "culture": "academic_medical", "region": "Midwest",
            "stress_factors": ["research_pressure", "complex_cases", "perfectionism", "academic_demands"],
            "strengths": ["world_reputation", "education", "collaboration", "resources"],
            "cultural_phrases": ["Mayo Model expectations", "team-based excellence", "academic medicine pressure"]
        },
        "Cleveland Clinic": {
            "size": 74000, "culture": "patient_first", "region": "Midwest",
            "stress_factors": ["high_acuity", "emotional_demands", "long_hours", "complexity"],
            "strengths": ["innovation", "teamwork", "technology", "patient_focus"],
            "cultural_phrases": ["patient-first philosophy", "caregivers not employees", "innovation pressure"]
        },
        "Johns Hopkins Medicine": {
            "size": 51000, "culture": "research_intensive", "region": "East Coast",
            "stress_factors": ["academic_pressure", "funding_competition", "case_complexity", "prestige_pressure"],
            "strengths": ["research_excellence", "prestige", "resources", "innovation"],
            "cultural_phrases": ["Hopkins excellence standard", "research-clinical balance", "academic medicine demands"]
        },
        "HCA Healthcare": {
            "size": 265000, "culture": "corporate_efficiency", "region": "National",
            "stress_factors": ["profit_pressure", "high_turnover", "resource_constraints", "efficiency_demands"],
            "strengths": ["protocols", "advancement", "scale", "systems"],
            "cultural_phrases": ["corporate healthcare model", "efficiency metrics", "for-profit pressures"]
        },
        "Intermountain Healthcare": {
            "size": 60000, "culture": "value_based_care", "region": "Mountain West",
            "stress_factors": ["quality_metrics", "cost_pressure", "rural_challenges", "staffing_remote"],
            "strengths": ["innovation_labs", "data_driven", "community_focus", "quality_care"],
            "cultural_phrases": ["value-based care model", "Intermountain Way", "quality over quantity"]
        },
        "Ascension Health": {
            "size": 142000, "culture": "mission_driven_catholic", "region": "National",
            "stress_factors": ["religious_conflicts", "mission_vs_profit", "diverse_facilities", "legacy_systems"],
            "strengths": ["mission_purpose", "community_service", "spiritual_care", "comprehensive_network"],
            "cultural_phrases": ["Catholic health mission", "serving all persons", "ministry of healing"]
        },
        "CommonSpirit Health": {
            "size": 150000, "culture": "faith_based_merger", "region": "National",
            "stress_factors": ["merger_integration", "cultural_conflicts", "system_complexity", "identity_crisis"],
            "strengths": ["expanded_resources", "diverse_expertise", "broader_reach", "shared_mission"],
            "cultural_phrases": ["merger challenges", "unified mission", "CommonSpirit way"]
        },
        "Providence Health": {
            "size": 120000, "culture": "compassionate_care", "region": "West Coast",
            "stress_factors": ["urban_violence", "homelessness_crisis", "mental_health_surge", "addiction_epidemic"],
            "strengths": ["community_focus", "social_justice", "innovation", "advocacy"],
            "cultural_phrases": ["Providence compassion", "serving the poor", "social justice medicine"]
        },
        "Sutter Health": {
            "size": 55000, "culture": "northern_california", "region": "California",
            "stress_factors": ["california_regulations", "seismic_upgrades", "wildfire_evacuations", "tech_competition"],
            "strengths": ["regional_expertise", "innovation", "quality_care", "community_roots"],
            "cultural_phrases": ["Northern California healthcare", "Sutter culture", "community-centered care"]
        },
        "Northwell Health": {
            "size": 74000, "culture": "new_york_intensity", "region": "New York",
            "stress_factors": ["covid_epicenter", "urban_trauma", "financial_pressure", "competitive_market"],
            "strengths": ["trauma_expertise", "research", "innovation", "resilience"],
            "cultural_phrases": ["New York healthcare intensity", "Northwell resilience", "pandemic front lines"]
        },
        "Mass General Brigham": {
            "size": 80000, "culture": "academic_excellence", "region": "Boston",
            "stress_factors": ["research_competition", "teaching_load", "complex_cases", "prestige_pressure"],
            "strengths": ["world_class_research", "innovation", "education", "prestige"],
            "cultural_phrases": ["Mass General excellence", "Partners legacy", "Boston medicine"]
        },
        "NewYork-Presbyterian": {
            "size": 48000, "culture": "manhattan_medicine", "region": "New York",
            "stress_factors": ["urban_complexity", "diverse_population", "high_expectations", "competitive_environment"],
            "strengths": ["prestige", "resources", "innovation", "expertise"],
            "cultural_phrases": ["Manhattan medicine", "Presbyterian excellence", "New York standards"]
        },
        "UPMC": {
            "size": 92000, "culture": "pittsburgh_innovation", "region": "Pennsylvania",
            "stress_factors": ["rust_belt_challenges", "population_decline", "economic_pressure", "legacy_issues"],
            "strengths": ["innovation", "research", "technology", "transformation"],
            "cultural_phrases": ["UPMC innovation", "Pittsburgh medicine", "transformation culture"]
        },
        "Geisinger Health": {
            "size": 26000, "culture": "rural_innovation", "region": "Pennsylvania",
            "stress_factors": ["rural_access", "provider_shortages", "transportation_barriers", "economic_challenges"],
            "strengths": ["innovation", "population_health", "integration", "technology"],
            "cultural_phrases": ["Geisinger innovation", "rural healthcare solutions", "ProvenCare model"]
        },
        "Atrium Health": {
            "size": 70000, "culture": "southeastern_growth", "region": "Southeast",
            "stress_factors": ["rapid_growth", "integration_challenges", "market_competition", "cultural_change"],
            "strengths": ["growth_opportunities", "innovation", "community_focus", "expansion"],
            "cultural_phrases": ["Atrium growth", "Carolinas healthcare", "transformation journey"]
        },
        "Advocate Aurora Health": {
            "size": 75000, "culture": "midwest_merger", "region": "Midwest",
            "stress_factors": ["merger_complexity", "cultural_integration", "system_harmonization", "identity_questions"],
            "strengths": ["expanded_scale", "shared_resources", "broader_expertise", "innovation"],
            "cultural_phrases": ["Advocate Aurora merger", "Midwest healthcare", "unified mission"]
        },
        "Texas Health Resources": {
            "size": 25000, "culture": "texas_independence", "region": "Texas",
            "stress_factors": ["texas_regulations", "border_health", "uninsured_population", "rural_challenges"],
            "strengths": ["independence", "community_focus", "innovation", "growth"],
            "cultural_phrases": ["Texas healthcare", "independent spirit", "community commitment"]
        },
        "Baylor Scott & White": {
            "size": 50000, "culture": "texas_academic", "region": "Texas",
            "stress_factors": ["academic_pressure", "research_demands", "teaching_load", "competition"],
            "strengths": ["academic_excellence", "research", "education", "innovation"],
            "cultural_phrases": ["Baylor medicine", "Scott & White legacy", "Texas academic excellence"]
        },
        "Orlando Health": {
            "size": 27000, "culture": "florida_tourism", "region": "Florida",
            "stress_factors": ["tourist_injuries", "seasonal_surge", "hurricane_preparedness", "diverse_population"],
            "strengths": ["trauma_expertise", "innovation", "growth", "community_service"],
            "cultural_phrases": ["Orlando healthcare", "tourist medicine", "Florida challenges"]
        }
    },

    "University": {
        # Top Academic Institutions (15 companies)
        "Harvard University": {
            "size": 17000, "culture": "elite_academic", "region": "Massachusetts",
            "stress_factors": ["imposter_syndrome", "publish_pressure", "elite_competition", "legacy_pressure"],
            "strengths": ["resources", "prestige", "networks", "freedom"],
            "cultural_phrases": ["Harvard excellence", "Crimson expectations", "elite institution pressure"]
        },
        "Stanford University": {
            "size": 16000, "culture": "innovation_entrepreneurial", "region": "California",
            "stress_factors": ["startup_pressure", "tech_competition", "innovation_demands", "valley_culture"],
            "strengths": ["innovation", "industry_ties", "resources", "flexibility"],
            "cultural_phrases": ["Stanford innovation culture", "Silicon Valley pressure", "entrepreneurial demands"]
        },
        "MIT": {
            "size": 13000, "culture": "technical_excellence", "region": "Massachusetts",
            "stress_factors": ["technical_perfectionism", "intense_workload", "competition", "hack_culture"],
            "strengths": ["problem_solving", "hands_on", "innovation", "community"],
            "cultural_phrases": ["MIT technical rigor", "hacker culture", "engineering excellence"]
        },
        "University of California System": {
            "size": 280000, "culture": "public_research", "region": "California",
            "stress_factors": ["funding_uncertainty", "bureaucracy", "political_pressure", "scale_challenges"],
            "strengths": ["diversity", "impact", "programs", "access"],
            "cultural_phrases": ["UC system bureaucracy", "public university challenges", "diverse community"]
        },
        "Yale University": {
            "size": 12000, "culture": "traditional_academic", "region": "Connecticut",
            "stress_factors": ["tradition_pressure", "elitism", "change_resistance", "competition"],
            "strengths": ["networks", "tradition", "mentorship", "resources"],
            "cultural_phrases": ["Yale tradition", "Ivy League pressure", "historic excellence"]
        },
        "Princeton University": {
            "size": 8500, "culture": "undergraduate_focus", "region": "New Jersey",
            "stress_factors": ["perfectionism", "grade_deflation", "social_pressure", "elite_competition"],
            "strengths": ["small_classes", "mentorship", "resources", "prestige"],
            "cultural_phrases": ["Princeton perfectionism", "Orange bubble", "undergraduate excellence"]
        },
        "Columbia University": {
            "size": 18000, "culture": "urban_academic", "region": "New York",
            "stress_factors": ["nyc_pressure", "urban_isolation", "competitive_environment", "cost_of_living"],
            "strengths": ["nyc_opportunities", "diversity", "resources", "networks"],
            "cultural_phrases": ["Columbia urban experience", "Manhattan academia", "city university pressure"]
        },
        "University of Chicago": {
            "size": 16500, "culture": "intellectual_rigor", "region": "Illinois",
            "stress_factors": ["academic_intensity", "grade_deflation", "intellectual_pressure", "harsh_winters"],
            "strengths": ["intellectual_freedom", "rigorous_thinking", "research", "innovation"],
            "cultural_phrases": ["UChicago rigor", "where fun comes to die", "intellectual intensity"]
        },
        "Carnegie Mellon University": {
            "size": 14000, "culture": "tech_innovation", "region": "Pennsylvania",
            "stress_factors": ["tech_pressure", "startup_culture", "competitive_cs", "work_life_blur"],
            "strengths": ["tech_innovation", "industry_connections", "hands_on", "entrepreneurship"],
            "cultural_phrases": ["CMU tech culture", "Silicon Valley of the East", "innovation pressure"]
        },
        "NYU": {
            "size": 20000, "culture": "urban_global", "region": "New York",
            "stress_factors": ["financial_pressure", "urban_stress", "competitive_arts", "identity_crisis"],
            "strengths": ["global_reach", "diversity", "arts_focus", "opportunity"],
            "cultural_phrases": ["NYU global culture", "Greenwich Village academia", "urban university life"]
        },
        "University of Texas System": {
            "size": 95000, "culture": "texas_scale", "region": "Texas",
            "stress_factors": ["political_pressure", "size_bureaucracy", "funding_battles", "cultural_wars"],
            "strengths": ["scale_resources", "diversity", "research", "tradition"],
            "cultural_phrases": ["UT system scale", "Texas higher education", "Longhorn tradition"]
        },
        "University of Michigan": {
            "size": 47000, "culture": "public_ivy", "region": "Michigan",
            "stress_factors": ["funding_cuts", "state_politics", "weather_isolation", "competitive_culture"],
            "strengths": ["research_excellence", "tradition", "alumni_network", "comprehensive_programs"],
            "cultural_phrases": ["Michigan excellence", "public ivy standards", "Go Blue culture"]
        },
        "Duke University": {
            "size": 40000, "culture": "southern_elite", "region": "North Carolina",
            "stress_factors": ["southern_expectations", "basketball_pressure", "social_hierarchy", "regional_bias"],
            "strengths": ["research_excellence", "beautiful_campus", "strong_alumni", "innovation"],
            "cultural_phrases": ["Duke excellence", "Blue Devil pride", "Southern ivy culture"]
        },
        "Northwestern University": {
            "size": 22000, "culture": "balanced_excellence", "region": "Illinois",
            "stress_factors": ["chicago_winters", "competitive_culture", "perfectionism", "social_pressure"],
            "strengths": ["balanced_programs", "strong_alumni", "research", "location"],
            "cultural_phrases": ["Northwestern excellence", "Purple pride", "lakefront academia"]
        },
        "University of Pennsylvania": {
            "size": 22000, "culture": "pre_professional", "region": "Pennsylvania",
            "stress_factors": ["pre_professional_pressure", "wharton_competition", "urban_campus", "networking_pressure"],
            "strengths": ["professional_preparation", "networks", "resources", "prestige"],
            "cultural_phrases": ["Penn pre-professional", "Wharton pressure", "Philly university life"]
        }
    },

    "Business": {
        # Major Corporations (20 companies)
        "Microsoft": {
            "size": 221000, "culture": "growth_mindset", "region": "Seattle",
            "stress_factors": ["constant_learning", "tech_evolution", "competition", "transformation"],
            "strengths": ["inclusion", "balance", "growth", "stability"],
            "cultural_phrases": ["growth mindset culture", "inclusive leadership", "cloud transformation"]
        },
        "Google": {
            "size": 174000, "culture": "innovation_data_driven", "region": "Silicon Valley",
            "stress_factors": ["performance_reviews", "rapid_change", "high_expectations", "competition"],
            "strengths": ["innovation", "benefits", "freedom", "impact"],
            "cultural_phrases": ["Google innovation", "data-driven culture", "Googler expectations"]
        },
        "Amazon": {
            "size": 1608000, "culture": "customer_obsession", "region": "Seattle",
            "stress_factors": ["high_pressure", "long_hours", "performance_culture", "rapid_growth"],
            "strengths": ["growth", "ownership", "innovation", "scale"],
            "cultural_phrases": ["customer obsession", "ownership principle", "Day 1 mentality"]
        },
        "Apple": {
            "size": 164000, "culture": "perfectionist_design", "region": "Silicon Valley",
            "stress_factors": ["secrecy_pressure", "perfectionism", "tight_deadlines", "innovation_pressure"],
            "strengths": ["product_pride", "design", "premium", "innovation"],
            "cultural_phrases": ["Apple perfectionism", "design excellence", "secrecy culture"]
        },
        "Meta": {
            "size": 87000, "culture": "move_fast_break_things", "region": "Silicon Valley",
            "stress_factors": ["rapid_iteration", "public_scrutiny", "pivot_pressure", "uncertainty"],
            "strengths": ["technical_challenges", "impact", "innovation", "growth"],
            "cultural_phrases": ["move fast philosophy", "Meta transformation", "social impact pressure"]
        },
        "Tesla": {
            "size": 127000, "culture": "mission_driven_intense", "region": "California",
            "stress_factors": ["unrealistic_deadlines", "high_pressure", "musk_demands", "volatility"],
            "strengths": ["mission", "innovation", "growth", "impact"],
            "cultural_phrases": ["Tesla mission", "Elon demands", "sustainable transport pressure"]
        },
        "Netflix": {
            "size": 11000, "culture": "freedom_responsibility", "region": "Los Angeles",
            "stress_factors": ["keeper_test", "performance_pressure", "rapid_change", "competition"],
            "strengths": ["compensation", "freedom", "talent", "innovation"],
            "cultural_phrases": ["Netflix culture", "keeper test", "freedom and responsibility"]
        },
        "Salesforce": {
            "size": 79000, "culture": "ohana_values", "region": "San Francisco",
            "stress_factors": ["aggressive_growth", "acquisition_integration", "competitive_market", "values_pressure"],
            "strengths": ["values_driven", "growth", "innovation", "community"],
            "cultural_phrases": ["Salesforce Ohana", "Trailblazer culture", "values-driven business"]
        },
        "Adobe": {
            "size": 26000, "culture": "creative_innovation", "region": "San Jose",
            "stress_factors": ["creative_pressure", "subscription_transition", "competition", "talent_retention"],
            "strengths": ["creative_tools", "innovation", "market_position", "culture"],
            "cultural_phrases": ["Adobe creativity", "digital transformation", "creative innovation pressure"]
        },
        "Oracle": {
            "size": 143000, "culture": "aggressive_enterprise", "region": "Austin",
            "stress_factors": ["aggressive_sales", "corporate_politics", "legacy_transition", "competition"],
            "strengths": ["enterprise_dominance", "stability", "compensation", "technology"],
            "cultural_phrases": ["Oracle aggression", "enterprise focus", "database dominance"]
        },
        "IBM": {
            "size": 345000, "culture": "legacy_transformation", "region": "New York",
            "stress_factors": ["legacy_decline", "layoff_anxiety", "transformation_pressure", "age_discrimination"],
            "strengths": ["stability", "experience", "global_reach", "innovation"],
            "cultural_phrases": ["IBM transformation", "Big Blue legacy", "enterprise heritage"]
        },
        "Uber": {
            "size": 32000, "culture": "hustle_disruption", "region": "San Francisco",
            "stress_factors": ["startup_pressure", "regulatory_battles", "culture_toxicity", "profitability_pressure"],
            "strengths": ["disruption", "growth", "global_reach", "innovation"],
            "cultural_phrases": ["Uber hustle", "disruption culture", "always be hustlin'"]
        },
        "Airbnb": {
            "size": 6800, "culture": "belong_anywhere", "region": "San Francisco",
            "stress_factors": ["pandemic_impact", "regulatory_challenges", "community_pressure", "growth_pressure"],
            "strengths": ["mission", "culture", "innovation", "community"],
            "cultural_phrases": ["belong anywhere", "host community", "sharing economy pressure"]
        },
        "SpaceX": {
            "size": 12000, "culture": "mars_mission", "region": "Los Angeles",
            "stress_factors": ["impossible_deadlines", "musk_intensity", "rocket_failures", "life_death_stakes"],
            "strengths": ["mission", "innovation", "breakthrough", "impact"],
            "cultural_phrases": ["Mars mission", "SpaceX intensity", "rocket science pressure"]
        },
        "Nvidia": {
            "size": 26000, "culture": "ai_revolution", "region": "Silicon Valley",
            "stress_factors": ["ai_hype_pressure", "talent_competition", "technical_complexity", "market_volatility"],
            "strengths": ["ai_leadership", "innovation", "growth", "technology"],
            "cultural_phrases": ["AI revolution", "GPU computing", "deep learning pressure"]
        },
        "Intel": {
            "size": 131000, "culture": "silicon_legacy", "region": "Silicon Valley",
            "stress_factors": ["competitive_pressure", "manufacturing_challenges", "talent_retention", "legacy_burden"],
            "strengths": ["engineering_excellence", "stability", "innovation", "scale"],
            "cultural_phrases": ["Intel inside", "silicon innovation", "semiconductor leadership"]
        },
        "Cisco": {
            "size": 83000, "culture": "networking_infrastructure", "region": "Silicon Valley",
            "stress_factors": ["enterprise_transitions", "cloud_competition", "legacy_products", "market_saturation"],
            "strengths": ["networking_expertise", "stability", "enterprise_relationships", "innovation"],
            "cultural_phrases": ["Cisco networking", "infrastructure foundation", "enterprise solutions"]
        },
        "PayPal": {
            "size": 30000, "culture": "fintech_innovation", "region": "San Jose",
            "stress_factors": ["financial_regulations", "security_threats", "competition", "fraud_prevention"],
            "strengths": ["fintech_leadership", "innovation", "security", "global_reach"],
            "cultural_phrases": ["PayPal payments", "fintech innovation", "digital money pressure"]
        },
        "Zoom": {
            "size": 7400, "culture": "video_first", "region": "San Jose",
            "stress_factors": ["pandemic_scrutiny", "security_concerns", "competition", "growth_management"],
            "strengths": ["video_leadership", "pandemic_success", "innovation", "culture"],
            "cultural_phrases": ["Zoom fatigue", "video communications", "pandemic hero pressure"]
        },
        "Slack": {
            "size": 2500, "culture": "future_of_work", "region": "San Francisco",
            "stress_factors": ["microsoft_competition", "acquisition_uncertainty", "product_evolution", "culture_preservation"],
            "strengths": ["work_transformation", "innovation", "culture", "user_love"],
            "cultural_phrases": ["future of work", "Slack culture", "workplace transformation"]
        }
    }
}

def get_company_distribution():
    """Calculate even distribution across 55 companies for 50K records"""
    total_companies = sum(len(companies) for companies in EXPANDED_COMPANIES.values())
    records_per_company = 50000 // total_companies
    remainder = 50000 % total_companies

    distribution = {}
    company_count = 0

    for domain, companies in EXPANDED_COMPANIES.items():
        distribution[domain] = {}
        for company_name, company_data in companies.items():
            base_records = records_per_company
            # Distribute remainder among first companies
            if company_count < remainder:
                base_records += 1

            distribution[domain][company_name] = base_records
            company_count += 1

    return distribution

if __name__ == "__main__":
    print("📊 Expanded Company Database - 55 Organizations")
    print("=" * 60)

    for domain, companies in EXPANDED_COMPANIES.items():
        print(f"\n{domain}: {len(companies)} companies")
        for company, data in companies.items():
            print(f"  - {company}: {data['size']:,} employees")

    total_companies = sum(len(companies) for companies in EXPANDED_COMPANIES.values())
    print(f"\n🎯 Total Companies: {total_companies}")

    distribution = get_company_distribution()
    print(f"\n📈 Records per company: ~{50000//total_companies:,}")

    total_records = sum(sum(dist.values()) for dist in distribution.values())
    print(f"Total records: {total_records:,}")