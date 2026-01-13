"""
Market demographic profiles for synthetic survey generation.

Provides predefined demographic distributions for common markets,
allowing users to generate surveys without ground truth data.
"""

from typing import Dict, Any


# Predefined market profiles
MARKET_PROFILES: Dict[str, Dict[str, Any]] = {
    'US_gaming': {
        'name': 'United States - iGaming',
        'description': 'US market profile for online gaming and lottery products',
        'demographics': {
            'gender': {
                'values': ['Male', 'Female', 'Non-binary', 'Prefer not to say'],
                'weights': [0.48, 0.48, 0.02, 0.02]
            },
            'age': {
                'min': 21,  # Legal gambling age in most US states
                'max': 75,
                'bands': {
                    '21-35': (21, 35),
                    '36-55': (36, 55),
                    '56-75': (56, 75)
                },
                'band_weights': [0.40, 0.35, 0.25]  # Skew younger for gaming
            },
            'occupation': {
                'values': [
                    'Technology', 'Finance', 'Healthcare', 'Education',
                    'Retail', 'Manufacturing', 'Hospitality', 'Transportation',
                    'Government', 'Other', 'Retired', 'Student', 'Unemployed'
                ],
                'weights': [0.15, 0.12, 0.10, 0.08, 0.08, 0.07, 0.06, 0.05, 0.05, 0.10, 0.08, 0.03, 0.03]
            },
            'category_buyer': {
                'values': [
                    'Lottery played in-store/person',
                    'Lottery played online/app',
                    'Paper scratchcards bought in person',
                    'Digital scratch games',
                    'None of the above'
                ],
                'weights': [0.30, 0.25, 0.25, 0.15, 0.05],
                'multi_select': True,
                'max_selections': 3
            },
            'category_non_rejector': {
                'values': [
                    'Lottery played in-store/person',
                    'Lottery played online/app',
                    'Paper scratchcards bought in person',
                    'None of the above'
                ],
                'weights': [0.10, 0.10, 0.05, 0.75],
                'multi_select': True,
                'max_selections': 3
            },
            'brand_buyers': {
                'values': [
                    'State Lottery',
                    'Powerball',
                    'Mega Millions',
                    'Scratch-offs',
                    'Daily Numbers',
                    'Other'
                ],
                'weights': [0.30, 0.25, 0.20, 0.15, 0.08, 0.02],
                'multi_select': True,
                'max_selections': 5
            },
            'inertia': {
                'min': 1,
                'max': 7,
                'distribution': 'normal',
                'mean': 4,
                'std': 1.5
            }
        }
    },

    'UK_lottery': {
        'name': 'United Kingdom - National Lottery',
        'description': 'UK market profile for National Lottery products',
        'demographics': {
            'gender': {
                'values': ['Male', 'Female', 'Non-binary', 'Prefer not to say'],
                'weights': [0.49, 0.49, 0.01, 0.01]
            },
            'age': {
                'min': 18,
                'max': 75,
                'bands': {
                    '18-35': (18, 35),
                    '36-55': (36, 55),
                    '56-75': (56, 75)
                },
                'band_weights': [0.30, 0.40, 0.30]  # Broader age distribution
            },
            'occupation': {
                'values': [
                    'Healthcare', 'Education', 'Finance', 'Technology',
                    'Retail', 'Manufacturing', 'Hospitality', 'Transportation',
                    'Government', 'Other', 'Retired', 'Student', 'Unemployed'
                ],
                'weights': [0.12, 0.10, 0.10, 0.10, 0.09, 0.08, 0.06, 0.05, 0.06, 0.10, 0.08, 0.03, 0.03]
            },
            'category_buyer': {
                'values': [
                    'Lottery played in-store/person',
                    'Lottery played online/app',
                    'Paper scratchcards bought in person',
                    'Digital scratch games',
                    'None of the above'
                ],
                'weights': [0.35, 0.30, 0.20, 0.10, 0.05],
                'multi_select': True,
                'max_selections': 3
            }
        }
    },

    'EU_general': {
        'name': 'European Union - General',
        'description': 'General EU market profile for lottery/gaming products',
        'demographics': {
            'gender': {
                'values': ['Male', 'Female', 'Non-binary', 'Prefer not to say'],
                'weights': [0.49, 0.49, 0.01, 0.01]
            },
            'age': {
                'min': 18,
                'max': 75,
                'bands': {
                    '18-35': (18, 35),
                    '36-55': (36, 55),
                    '56-75': (56, 75)
                },
                'band_weights': [0.32, 0.38, 0.30]
            },
            'occupation': {
                'values': [
                    'Healthcare', 'Education', 'Finance', 'Technology',
                    'Retail', 'Manufacturing', 'Hospitality', 'Transportation',
                    'Government', 'Other', 'Retired', 'Student', 'Unemployed'
                ],
                'weights': [0.11, 0.10, 0.09, 0.09, 0.09, 0.09, 0.07, 0.06, 0.06, 0.10, 0.08, 0.03, 0.03]
            },
            'category_buyer': {
                'values': [
                    'Lottery played in-store/person',
                    'Lottery played online/app',
                    'Paper scratchcards bought in person',
                    'Digital scratch games',
                    'None of the above'
                ],
                'weights': [0.30, 0.25, 0.25, 0.15, 0.05],
                'multi_select': True,
                'max_selections': 3
            },
            'category_non_rejector': {
                'values': [
                    'Lottery played in-store/person',
                    'Lottery played online/app',
                    'Paper scratchcards bought in person',
                    'None of the above'
                ],
                'weights': [0.10, 0.10, 0.05, 0.75],
                'multi_select': True,
                'max_selections': 3
            },
            'brand_buyers': {
                'values': [
                    'State Lottery',
                    'Powerball',
                    'Mega Millions',
                    'Scratch-offs',
                    'Daily Numbers',
                    'Other'
                ],
                'weights': [0.30, 0.25, 0.20, 0.15, 0.08, 0.02],
                'multi_select': True,
                'max_selections': 5
            },
            'inertia': {
                'min': 1,
                'max': 7,
                'distribution': 'normal',
                'mean': 4,
                'std': 1.5
            }
        }
    },

    'generic': {
        'name': 'Generic/Default',
        'description': 'Default demographic profile suitable for most markets',
        'demographics': {
            'gender': {
                'values': ['Male', 'Female', 'Non-binary', 'Prefer to self-identify', 'Prefer not to say'],
                'weights': [0.45, 0.45, 0.05, 0.03, 0.02]
            },
            'age': {
                'min': 18,
                'max': 75,
                'bands': {
                    '18-35': (18, 35),
                    '36-55': (36, 55),
                    '56-75': (56, 75)
                },
                'band_weights': [0.33, 0.34, 0.33]
            },
            'occupation': {
                'values': [
                    'Education', 'Healthcare', 'Technology', 'Finance',
                    'Retail', 'Manufacturing', 'Hospitality', 'Transportation',
                    'Government', 'Other', 'Retired', 'Student', 'Unemployed'
                ],
                'weights': None  # Uniform distribution
            },
            'category_buyer': {
                'values': [
                    'Lottery played in-store/person',
                    'Lottery played online/app',
                    'Paper scratchcards bought in person',
                    'None of the above'
                ],
                'weights': [0.30, 0.20, 0.30, 0.20],
                'multi_select': True,
                'max_selections': 3
            }
        }
    }
}


def get_market_profile(profile_name: str) -> Dict[str, Any]:
    """
    Get a market profile by name.

    Args:
        profile_name: Name of the profile (case-insensitive)

    Returns:
        Market profile dictionary

    Raises:
        ValueError: If profile not found
    """
    profile_name_lower = profile_name.lower()

    for key, profile in MARKET_PROFILES.items():
        if key.lower() == profile_name_lower:
            return profile

    raise ValueError(
        f"Market profile '{profile_name}' not found. "
        f"Available profiles: {', '.join(MARKET_PROFILES.keys())}"
    )


def list_market_profiles() -> Dict[str, str]:
    """
    List all available market profiles.

    Returns:
        Dictionary mapping profile names to descriptions
    """
    return {
        name: profile['description']
        for name, profile in MARKET_PROFILES.items()
    }


def validate_custom_demographics(demographics: Dict[str, Any]) -> bool:
    """
    Validate custom demographics dictionary.

    Args:
        demographics: Custom demographics to validate

    Returns:
        True if valid

    Raises:
        ValueError: If demographics invalid
    """
    required_keys = ['gender', 'age', 'occupation']

    for key in required_keys:
        if key not in demographics:
            raise ValueError(f"Missing required demographic key: '{key}'")

    # Validate gender
    if 'values' not in demographics['gender']:
        raise ValueError("Gender demographics must have 'values' key")

    # Validate age
    age = demographics['age']
    if not ('min' in age and 'max' in age):
        raise ValueError("Age demographics must have 'min' and 'max' keys")
    if age['min'] < 0 or age['max'] > 120 or age['min'] >= age['max']:
        raise ValueError("Invalid age range")

    # Validate occupation
    if 'values' not in demographics['occupation']:
        raise ValueError("Occupation demographics must have 'values' key")

    return True
