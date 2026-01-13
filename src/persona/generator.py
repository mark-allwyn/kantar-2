"""
Persona Generator

Generates synthetic respondent personas with demographics and psychographics.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import random
import numpy as np


@dataclass
class Persona:
    """A synthetic respondent persona"""
    id: str
    demographics: Dict[str, Any] = field(default_factory=dict)
    psychographics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'demographics': self.demographics,
            'psychographics': self.psychographics,
            'metadata': self.metadata
        }

    def get_all_attributes(self) -> Dict[str, Any]:
        """Get all attributes (demographics + psychographics)"""
        return {**self.demographics, **self.psychographics}

    def to_description(self) -> str:
        """Generate natural language description for LLM prompts"""
        parts = []

        # Demographics
        if 'age' in self.demographics:
            parts.append(f"{self.demographics['age']} years old")

        if 'gender' in self.demographics:
            parts.append(self.demographics['gender'].lower())

        # Occupation
        if 'occupation' in self.demographics:
            parts.append(f"works in {self.demographics['occupation']}")

        # Psychographics
        if 'category_buyer' in self.psychographics:
            buyer_types = self.psychographics['category_buyer']
            if isinstance(buyer_types, list) and buyer_types:
                parts.append(f"buys {', '.join(buyer_types).lower()}")

        if 'inertia' in self.psychographics:
            inertia = self.psychographics['inertia']
            if inertia <= 3:
                parts.append("prefers to stick with familiar products")
            elif inertia >= 5:
                parts.append("likes to try new and different products")

        return ", ".join(parts) if parts else "a consumer"


class PersonaGenerator:
    """Generator for synthetic personas"""

    def __init__(self,
                 random_seed: Optional[int] = None,
                 ground_truth_demographics: Optional[Dict[str, Dict]] = None,
                 custom_distributions: Optional[Dict[str, Any]] = None,
                 demographics_schema: Optional[Any] = None):
        """
        Initialize the persona generator.

        Args:
            random_seed: Random seed for reproducibility
            ground_truth_demographics: Optional demographics from ground truth data
                                      Format: {column_name: {value: count}}
            custom_distributions: Optional pre-built distribution dict (e.g., from market profiles)
                                Format: {attribute: {values: [...], weights: [...]}}
            demographics_schema: Optional DemographicsSchema defining valid categorical values
        """
        if random_seed is not None:
            random.seed(random_seed)
            np.random.seed(random_seed)

        self.personas_generated = 0
        self.ground_truth_demographics = ground_truth_demographics
        self.custom_distributions = custom_distributions
        self.demographics_schema = demographics_schema

        # Define distributions based on questionnaire (or ground truth if provided)
        self.distributions = self._define_distributions()

    def _define_distributions(self) -> Dict[str, Any]:
        """Define sampling distributions for persona attributes"""
        # Use custom distributions if provided (e.g., from market profiles)
        if self.custom_distributions:
            # Merge with defaults to fill any missing keys
            defaults = self._get_default_distributions()
            distributions = {**defaults, **self.custom_distributions}
            return distributions

        # Use ground truth demographics if provided
        if self.ground_truth_demographics:
            return self._distributions_from_ground_truth()

        # Otherwise use default distributions
        return self._get_default_distributions()

    def generate_persona(self, quotas: Optional[Dict[str, Any]] = None) -> Persona:
        """
        Generate a single persona.

        Args:
            quotas: Optional quota constraints to apply

        Returns:
            Generated Persona
        """
        self.personas_generated += 1
        persona_id = f"P{self.personas_generated:05d}"

        demographics = {}
        psychographics = {}

        # Generate demographics
        demographics['gender'] = self._sample_categorical('gender')
        demographics['age'] = self._sample_age()
        demographics['occupation'] = self._sample_categorical('occupation')

        # Generate psychographics
        psychographics['category_buyer'] = self._sample_category_buyer()
        psychographics['category_non_rejector'] = self._sample_category_non_rejector()
        psychographics['brand_buyers'] = self._sample_brand_buyers()
        psychographics['inertia'] = self._sample_inertia()

        # Determine derived variables
        demographics['age_band'] = self._get_age_band(demographics['age'])

        # Sample target_group from GT if available, otherwise derive it
        if self.ground_truth_demographics and 'target_group' in self.distributions:
            psychographics['target_group'] = self._sample_categorical('target_group')
        else:
            psychographics['target_group'] = self._determine_target_group(
                demographics['age'],
                psychographics['category_buyer']
            )

        psychographics['sc_player_type'] = self._determine_sc_player_type(
            psychographics['category_buyer']
        )

        persona = Persona(
            id=persona_id,
            demographics=demographics,
            psychographics=psychographics
        )

        # Validate against schema if provided (GT mode with hard fail)
        if self.demographics_schema:
            is_valid, errors = self.demographics_schema.validate_demographics(demographics)
            if not is_valid:
                error_msg = f"Generated persona {persona_id} has invalid demographics:\n"
                error_msg += "\n".join(f"  - {err}" for err in errors)
                raise ValueError(error_msg)

        return persona

    def generate_batch(self,
                      n: int,
                      quotas: Optional[Dict[str, Any]] = None,
                      apply_screening: bool = True) -> List[Persona]:
        """
        Generate a batch of personas.

        Args:
            n: Number of personas to generate
            quotas: Optional quota constraints
            apply_screening: Whether to apply screening rules

        Returns:
            List of Personas
        """
        personas = []

        # Generate with buffer for screening
        buffer_multiplier = 1.5 if apply_screening else 1.0
        to_generate = int(n * buffer_multiplier)

        for _ in range(to_generate):
            persona = self.generate_persona(quotas)

            # Apply screening if enabled
            if apply_screening:
                if self._passes_screening(persona):
                    personas.append(persona)
            else:
                personas.append(persona)

            # Stop when we have enough
            if len(personas) >= n:
                break

        return personas[:n]

    def _sample_categorical(self, attribute: str) -> str:
        """Sample a categorical attribute"""
        dist = self.distributions[attribute]
        values = dist['values']
        weights = dist.get('weights')

        if weights:
            return random.choices(values, weights=weights)[0]
        else:
            return random.choice(values)

    def _sample_age(self) -> int:
        """Sample age within range and bands"""
        dist = self.distributions['age']

        # Check if this is ground truth data with actual ages
        if dist.get('from_ground_truth') and 'values' in dist:
            # Sample directly from ground truth ages using their weights
            values = dist['values']
            weights = dist.get('weights')

            # Convert to int and filter valid ages
            valid_ages = []
            valid_weights = []
            for i, v in enumerate(values):
                try:
                    age = int(v)
                    if 0 < age < 120:  # Sanity check
                        valid_ages.append(age)
                        valid_weights.append(weights[i] if weights else 1.0)
                except (ValueError, TypeError):
                    continue

            if valid_ages:
                return random.choices(valid_ages, weights=valid_weights)[0]

        # Standard band-based sampling (no-GT mode or profiles)
        if 'bands' in dist and 'band_weights' in dist:
            bands = list(dist['bands'].values())
            band_weights = dist['band_weights']

            selected_band = random.choices(bands, weights=band_weights)[0]
            min_age, max_age = selected_band

            # Sample age within band
            return random.randint(min_age, max_age)

        # Fallback: uniform sampling from min/max
        min_age = dist.get('min', 18)
        max_age = dist.get('max', 75)
        return random.randint(min_age, max_age)

    def _sample_category_buyer(self) -> List[str]:
        """Sample category buyer (multi-select)"""
        dist = self.distributions['category_buyer']
        values = dist['values']

        # Decide number of selections
        if 'None of the above' in values:
            # Could select none
            if random.random() < 0.2:  # 20% select "None of the above"
                return ['None of the above']

        # Select 1-3 options (excluding "None")
        available = [v for v in values if v != 'None of the above']
        n_select = random.randint(1, min(3, len(available)))

        return random.sample(available, n_select)

    def _sample_category_non_rejector(self) -> List[str]:
        """
        Sample S5: Category Non Rejector - what would you NEVER spend money on.

        Uses weighted sampling - most people select "None of the above" (won't reject anything),
        with low probability of rejecting paper scratchcards (which would screen them out).
        """
        dist = self.distributions['category_non_rejector']
        values = dist['values']
        weights = dist['weights']

        # Most likely to select "None of the above" (won't reject anything)
        if random.random() < 0.75:  # 75% chance
            return ['None of the above']

        # Otherwise, select items they would reject (1-2 items)
        # Avoid paper scratchcards to reduce screening
        available = [v for v in values if v != 'None of the above']
        available_weights = [w for v, w in zip(values, weights) if v != 'None of the above']

        # Normalize weights
        total = sum(available_weights)
        normalized_weights = [w/total for w in available_weights]

        n_select = random.randint(1, 2)
        selected = random.choices(available, weights=normalized_weights, k=n_select)

        # Remove duplicates
        return list(set(selected))

    def _sample_brand_buyers(self) -> List[str]:
        """Sample brand buyers (multi-select)"""
        dist = self.distributions['brand_buyers']
        values = dist['values']
        weights = dist['weights']
        max_selections = dist.get('max_selections', 5)  # Default to 5 if not specified

        # Decide number of brands to select (1-max)
        n_select = random.randint(1, min(max_selections, len(values)))

        # Use weighted sampling
        selected_brands = random.choices(values, weights=weights, k=n_select)

        # Remove duplicates while preserving order
        seen = set()
        unique_brands = []
        for brand in selected_brands:
            if brand not in seen:
                seen.add(brand)
                unique_brands.append(brand)

        return unique_brands

    def _sample_inertia(self) -> int:
        """Sample inertia level"""
        dist = self.distributions['inertia']

        if dist['distribution'] == 'normal':
            # Sample from normal distribution and clip to range
            value = np.random.normal(dist['mean'], dist['std'])
            value = int(round(np.clip(value, dist['min'], dist['max'])))
            return value
        else:
            return random.randint(dist['min'], dist['max'])

    def _get_age_band(self, age: int) -> str:
        """
        Determine age band from age.

        Uses demographics schema if available to ensure exact GT alignment,
        otherwise falls back to distribution-based mapping.
        """
        # Use schema if available (GT mode)
        if self.demographics_schema:
            age_band = self.demographics_schema.get_age_band(age)
            if age_band:
                return age_band

        # Fall back to distribution bands (no-GT mode or profile)
        if 'age' in self.distributions and 'bands' in self.distributions['age']:
            bands = self.distributions['age']['bands']
            for band_name, (min_age, max_age) in bands.items():
                if min_age <= age <= max_age:
                    return band_name

        # Legacy hard-coded fallback
        if 18 <= age <= 35:
            return '18-35'
        elif 36 <= age <= 55:
            return '36-55'
        elif 56 <= age <= 75:
            return '56-75'
        else:
            return 'Unknown'

    def _determine_target_group(self, age: int, category_buyer: List[str]) -> str:
        """
        Determine target group (S7) based on age and category buyer.

        Logic from questionnaire:
        - Young nonrejectors 18-35: S2_3=1 and (S4=3 or S5<>3)
        - Current SC players 36-75: S2_3=2,3 and S4=3

        Where:
        - S2_3=1 means age 18-35
        - S2_3=2,3 means age 36-75
        - S4=3 means "Paper scratchcards bought in person"
        """
        has_paper_scratchcards = 'Paper scratchcards bought in person' in category_buyer

        # Young nonrejectors 18-35 (players or nonplayers)
        # Age 18-35 AND (buys paper scratchcards OR non-rejector)
        if 18 <= age <= 35:
            # Since we don't have S5, we assume anyone not selecting "None of the above" is a non-rejector
            if has_paper_scratchcards or category_buyer != ['None of the above']:
                return 'Young nonrejectors 18-35 (players or nonplayers)'

        # Current SC players 36-75
        # Age 36-75 AND buys paper scratchcards
        if 36 <= age <= 75:
            if has_paper_scratchcards:
                return 'Current SC players 36-75'

        return 'Main'  # Default (matches ground truth)

    def _determine_sc_player_type(self, category_buyer: List[str]) -> str:
        """
        Determine S8: SC Player Type based on S4 (category buyer).

        Logic from questionnaire:
        - If S4=3 (has "Paper scratchcards bought in person") → "SC Players"
        - If S4<>3 (does NOT have "Paper scratchcards bought in person") → "SC Non Players"
        """
        has_paper_scratchcards = 'Paper scratchcards bought in person' in category_buyer

        if has_paper_scratchcards:
            return 'SC Players'
        else:
            return 'SC Non Players'

    def _passes_screening(self, persona: Persona) -> bool:
        """Check if persona passes screening criteria"""
        # Screen out excluded occupations
        excluded_occupations = [
            'Advertising/PR',
            'Marketing/Market Research',
            'Lottery sales/distribution',
            'Tobacco shop salesperson'
        ]

        if persona.demographics.get('occupation') in excluded_occupations:
            return False

        # Age must be in range
        age = persona.demographics.get('age', 0)
        if not (18 <= age <= 75):
            return False

        return True

    def _distributions_from_ground_truth(self) -> Dict[str, Any]:
        """
        Build distributions from ground truth demographics.

        Ground truth format: {column_name: {value: count}}
        Example: {'Gender': {'Male': 120, 'Female': 130}}
        """
        distributions = {}

        # Map ground truth column names to distribution keys
        column_mapping = {
            'Gender': 'gender',
            '(SEX_NONBINARY) SEX': 'gender',
            'AGE': 'age',
            '(AGEQUOTA) AGEBANDS': 'age_band',
            '(OCCUPATION_SCR) OCCUPATION SCREENER': 'occupation',
            '(CATBUYER) PRODUCTS / SERVICES BOUGHT': 'category_buyer',
            '(BRDBUY) BRANDS BOUGHT': 'brand_buyers',
            '(GROUPFMR) SAMPLE TYPE': 'target_group'
        }

        for gt_column, dist_key in column_mapping.items():
            if gt_column in self.ground_truth_demographics:
                value_counts = self.ground_truth_demographics[gt_column]

                # Convert counts to probabilities
                total = sum(value_counts.values())
                if total > 0:
                    values = list(value_counts.keys())
                    weights = [value_counts[v] / total for v in values]

                    # Special handling for different types
                    if dist_key == 'age':
                        # For age, we have actual ages - extract min/max and build distribution
                        ages = [int(v) for v in values if str(v).isdigit()]
                        if ages:
                            distributions['age'] = {
                                'min': min(ages),
                                'max': max(ages),
                                'values': values,
                                'weights': weights,
                                'from_ground_truth': True
                            }
                    elif dist_key in ['category_buyer', 'brand_buyers']:
                        # Multi-select fields - handle comma-separated values
                        distributions[dist_key] = {
                            'values': values,
                            'weights': weights,
                            'multi_select': True,
                            'from_ground_truth': True
                        }
                    else:
                        # Regular categorical
                        distributions[dist_key] = {
                            'values': values,
                            'weights': weights,
                            'from_ground_truth': True
                        }

        # Fill in any missing distributions with defaults
        default_dist = self._get_default_distributions()
        for key in ['gender', 'age', 'occupation', 'category_buyer', 'category_non_rejector', 'brand_buyers', 'inertia']:
            if key not in distributions:
                distributions[key] = default_dist[key]

        return distributions

    def _get_default_distributions(self) -> Dict[str, Any]:
        """Get default distributions (without recursion)."""
        return {
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
                'weights': None
            },
            'category_buyer': {
                'values': [
                    'Lottery played in-store/person',
                    'Lottery played online/app',
                    'Paper scratchcards bought in person',
                    'None of the above'
                ],
                'weights': [0.3, 0.2, 0.3, 0.2],
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
                'weights': [0.1, 0.1, 0.05, 0.75],
                'multi_select': True,
                'max_selections': 3
            },
            'sc_players': {
                'values': ['SC Players', 'SC Non-players'],
                'weights': [0.5, 0.5]
            },
            'inertia': {
                'min': 1,
                'max': 7,
                'distribution': 'normal',
                'mean': 4,
                'std': 1.5
            },
            'brand_buyers': {
                'values': [
                    'Zlatá rybka',
                    'Černá perla',
                    'Vánoční losy',
                    'Rentiér',
                    'Mates',
                    'Zlatá podkova',
                    'Zlatý měšec',
                    'Štístko',
                    'Maxa / Korunka',
                    'Fortuna',
                    'Other'
                ],
                'weights': [0.25, 0.20, 0.15, 0.12, 0.08, 0.05, 0.05, 0.04, 0.03, 0.02, 0.01],
                'multi_select': True,
                'max_selections': 5
            }
        }
