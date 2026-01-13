"""
Demographics schema extractor and validator.

Extracts valid categorical values from ground truth data to ensure
synthetic data uses the same categorical values (not just distributions).
"""

import pandas as pd
import re
import logging
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AgeBandRange:
    """Represents an age band with its label and numeric range."""
    label: str
    min_age: int
    max_age: int


class DemographicsSchema:
    """
    Extracts and stores valid categorical values from ground truth.

    Ensures synthetic data uses exactly the same categorical values as
    ground truth, preventing distribution mismatches during validation.
    """

    def __init__(self, ground_truth_df: Optional[pd.DataFrame] = None):
        """
        Initialize demographics schema.

        Args:
            ground_truth_df: Ground truth DataFrame to extract schema from
        """
        self.ground_truth_df = ground_truth_df
        self.schema: Dict[str, Set[str]] = {}
        self.age_bands: List[AgeBandRange] = []

        if ground_truth_df is not None:
            self._extract_schema()

    def _extract_schema(self):
        """Extract valid categorical values for all demographic fields."""
        logger.info("Extracting demographics schema from ground truth")

        # Map column names to schema keys
        column_mapping = {
            '(SEX_NONBINARY) SEX': 'gender',
            'Gender': 'gender_simple',
            '(AGEQUOTA) AGEBANDS': 'age_bands',
            '(OCCUPATION_SCR) OCCUPATION SCREENER': 'occupation',
            '(GROUPFMR) SAMPLE TYPE': 'target_group',
            '(CATBUYER) PRODUCTS / SERVICES BOUGHT': 'category_buyer',
            '(BRDBUY) BRANDS BOUGHT': 'brand_buyers'
        }

        for col_name, schema_key in column_mapping.items():
            if col_name in self.ground_truth_df.columns:
                unique_values = self.ground_truth_df[col_name].dropna().unique()
                self.schema[schema_key] = set(unique_values)
                logger.info(f"  {schema_key}: {len(unique_values)} unique values")

        # Extract age band ranges
        if 'age_bands' in self.schema:
            self.age_bands = self._parse_age_bands(list(self.schema['age_bands']))
            logger.info(f"  Parsed {len(self.age_bands)} age band ranges")

    def _parse_age_bands(self, age_band_labels: List[str]) -> List[AgeBandRange]:
        """
        Parse age band labels to extract numeric ranges.

        Handles formats like:
        - '18 - 34' → (18, 34)
        - '35 - 50' → (35, 50)
        - '21-35' → (21, 35)
        - '18 to 24' → (18, 24)
        """
        age_bands = []

        # Pattern to match age ranges with various separators
        pattern = r'(\d+)\s*[-–—to]+\s*(\d+)'

        for label in age_band_labels:
            match = re.search(pattern, label, re.IGNORECASE)
            if match:
                min_age = int(match.group(1))
                max_age = int(match.group(2))
                age_bands.append(AgeBandRange(
                    label=label,
                    min_age=min_age,
                    max_age=max_age
                ))
                logger.debug(f"  Parsed '{label}' → ({min_age}, {max_age})")
            else:
                logger.warning(f"Could not parse age band: '{label}'")

        # Sort by min_age
        age_bands.sort(key=lambda x: x.min_age)

        return age_bands

    def get_age_band(self, age: int) -> Optional[str]:
        """
        Map numeric age to ground truth age band label.

        Args:
            age: Numeric age

        Returns:
            Age band label from ground truth, or None if no match
        """
        for band in self.age_bands:
            if band.min_age <= age <= band.max_age:
                return band.label

        # If no exact match, try to find closest band
        if self.age_bands:
            if age < self.age_bands[0].min_age:
                return self.age_bands[0].label
            if age > self.age_bands[-1].max_age:
                return self.age_bands[-1].label

        return None

    def validate_value(self, field: str, value: str) -> bool:
        """
        Check if a value is valid for a demographic field.

        Args:
            field: Schema field name (e.g., 'gender', 'age_bands')
            value: Value to validate

        Returns:
            True if value exists in schema, False otherwise
        """
        if field not in self.schema:
            return True  # No schema defined for this field

        return value in self.schema[field]

    def get_valid_values(self, field: str) -> List[str]:
        """
        Get list of valid values for a demographic field.

        Args:
            field: Schema field name

        Returns:
            List of valid values, or empty list if field not in schema
        """
        if field not in self.schema:
            return []

        return sorted(list(self.schema[field]))

    def validate_demographics(self, demographics: Dict[str, any]) -> Tuple[bool, List[str]]:
        """
        Validate a full demographics dictionary against schema.

        Args:
            demographics: Dictionary of demographic values

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Check gender
        if 'gender' in demographics and 'gender' in self.schema:
            if not self.validate_value('gender', demographics['gender']):
                errors.append(
                    f"Invalid gender '{demographics['gender']}'. "
                    f"Valid values: {self.get_valid_values('gender')}"
                )

        # Check age band
        if 'age_band' in demographics and 'age_bands' in self.schema:
            if not self.validate_value('age_bands', demographics['age_band']):
                errors.append(
                    f"Invalid age band '{demographics['age_band']}'. "
                    f"Valid values: {self.get_valid_values('age_bands')}"
                )

        # Check occupation
        if 'occupation' in demographics and 'occupation' in self.schema:
            if not self.validate_value('occupation', demographics['occupation']):
                errors.append(
                    f"Invalid occupation '{demographics['occupation']}'. "
                    f"Valid values: {self.get_valid_values('occupation')}"
                )

        return len(errors) == 0, errors

    @classmethod
    def from_profile(cls, profile_demographics: Dict[str, any]) -> 'DemographicsSchema':
        """
        Create schema from market profile demographics configuration.

        Args:
            profile_demographics: Demographics dict from market profile

        Returns:
            DemographicsSchema instance
        """
        schema = cls(ground_truth_df=None)

        # Extract gender values
        if 'gender' in profile_demographics:
            schema.schema['gender'] = set(profile_demographics['gender']['values'])

        # Extract age bands from profile
        if 'age' in profile_demographics and 'bands' in profile_demographics['age']:
            bands_dict = profile_demographics['age']['bands']
            schema.schema['age_bands'] = set(bands_dict.keys())

            # Create age band ranges
            for label, (min_age, max_age) in bands_dict.items():
                schema.age_bands.append(AgeBandRange(
                    label=label,
                    min_age=min_age,
                    max_age=max_age
                ))
            schema.age_bands.sort(key=lambda x: x.min_age)

        # Extract occupation values
        if 'occupation' in profile_demographics:
            schema.schema['occupation'] = set(profile_demographics['occupation']['values'])

        # Extract category buyer values
        if 'category_buyer' in profile_demographics:
            schema.schema['category_buyer'] = set(profile_demographics['category_buyer']['values'])

        # Extract brand buyer values
        if 'brand_buyers' in profile_demographics:
            schema.schema['brand_buyers'] = set(profile_demographics['brand_buyers']['values'])

        logger.info(f"Created schema from market profile with {len(schema.schema)} fields")

        return schema

    def to_dict(self) -> Dict[str, any]:
        """Export schema to dictionary format."""
        return {
            'schema': {k: list(v) for k, v in self.schema.items()},
            'age_bands': [
                {'label': band.label, 'min_age': band.min_age, 'max_age': band.max_age}
                for band in self.age_bands
            ]
        }

    def __repr__(self) -> str:
        """String representation of schema."""
        fields = list(self.schema.keys())
        return f"DemographicsSchema(fields={fields}, age_bands={len(self.age_bands)})"
