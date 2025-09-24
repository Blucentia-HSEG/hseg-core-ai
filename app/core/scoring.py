"""
HSEG Scoring Configuration
Centralizes category weights, question counts, and 28-point tier thresholds
per HSEG_Comprehensive_Scoring_Documentation.md (Doc Version 1.0).
"""

from typing import Dict

DOC_VERSION = "1.0"

# Category weights and number of questions
CATEGORY_CONFIG: Dict[int, Dict[str, float]] = {
    1: { 'weight': 3.0, 'num_questions': 4 },  # Power Abuse & Suppression
    2: { 'weight': 2.5, 'num_questions': 3 },  # Discrimination & Exclusion
    3: { 'weight': 2.0, 'num_questions': 3 },  # Manipulative Work Culture
    4: { 'weight': 3.0, 'num_questions': 4 },  # Failure of Accountability
    5: { 'weight': 2.5, 'num_questions': 4 },  # Mental Health Harm
    6: { 'weight': 2.0, 'num_questions': 4 },  # Erosion of Voice & Autonomy
}

# Precomputed convenience map
CATEGORY_WEIGHTS = {k: v['weight'] for k, v in CATEGORY_CONFIG.items()}

# 55.5 max weighted points across categories; 13.875 theoretical min
MAX_TOTAL_POINTS = 55.5
MIN_TOTAL_POINTS = 13.875

# 28-point normalized scale boundaries
NORMALIZED_MAX = 28.0
NORMALIZED_MIN = 7.0

# Tier upper-bounds on 28-point scale
THRESHOLDS_28 = {
    'crisis_max': 12.0,
    'at_risk_max': 16.0,
    'mixed_max': 20.0,
    'safe_max': 24.0,
}

def normalize_points_to_28(total_weighted_points: float) -> float:
    """Normalize total weighted points (0..MAX_TOTAL_POINTS) to 28-point scale."""
    return (total_weighted_points / MAX_TOTAL_POINTS) * NORMALIZED_MAX

