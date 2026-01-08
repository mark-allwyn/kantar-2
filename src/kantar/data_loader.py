"""
Data loader for Kantar ground truth Excel files.

Loads and parses ground truth survey data from Excel files, extracting:
- Respondent demographics
- Survey responses
- Concept assignments
- Column structure for template matching
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class ColumnInfo:
    """Information about an Excel column."""
    name: str
    index: int
    column_type: str  # 'demographic', 'concept_assignment', 'question', 'metadata'
    concept_name: Optional[str] = None  # For question columns
    question_id: Optional[str] = None  # e.g., 'UNPURINT', 'UNIQNESS'


@dataclass
class GroundTruthData:
    """Ground truth survey data from Excel file."""
    df: pd.DataFrame
    file_path: Path
    column_info: List[ColumnInfo]
    concept_names: List[str]
    demographic_columns: List[str]
    question_columns: List[str]
    respondent_count: int

    def get_concept_columns(self, concept_name: str) -> List[str]:
        """Get all question columns for a specific concept."""
        return [
            col.name for col in self.column_info
            if col.concept_name == concept_name and col.column_type == 'question'
        ]

    def get_question_columns_by_id(self, question_id: str) -> List[str]:
        """Get all columns for a specific question ID across all concepts."""
        return [
            col.name for col in self.column_info
            if col.question_id == question_id and col.column_type == 'question'
        ]

    def get_demographics_summary(self) -> Dict[str, any]:
        """Get summary statistics of demographics."""
        summary = {}
        for col in self.demographic_columns:
            if col in self.df.columns:
                summary[col] = self.df[col].value_counts().to_dict()
        return summary


class GroundTruthLoader:
    """
    Loader for Kantar ground truth Excel files.

    Analyzes Excel structure to identify:
    - Demographic columns
    - Concept assignment columns
    - Question columns and their mapping to concepts
    - Response formats and scales
    """

    # Known demographic column patterns
    DEMOGRAPHIC_PATTERNS = [
        'SERIAL', 'DATE', 'Gender', 'SEX', 'AGE', 'OCCUPATION',
        'SAMPLE', 'QUOTA', 'CATBUYER', 'BRDBUY', 'GROUPFMR'
    ]

    # Known concept assignment patterns
    CONCEPT_ASSIGNMENT_PATTERNS = [
        'Concept_block', 'helper', 'Position'
    ]

    # Known question ID patterns (from column names like "(UNPURINT)")
    QUESTION_ID_PATTERN = re.compile(r'\(([A-Z_]+)\)')

    def __init__(self):
        """Initialize the ground truth loader."""
        pass

    def load(self, file_path: Path) -> GroundTruthData:
        """
        Load ground truth data from Excel file.

        Args:
            file_path: Path to Excel file

        Returns:
            GroundTruthData object

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file cannot be parsed
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Ground truth file not found: {file_path}")

        logger.info(f"Loading ground truth data from: {file_path}")

        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            raise ValueError(f"Failed to load Excel file: {e}")

        logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")

        # Analyze column structure
        column_info = self._analyze_columns(df)

        # Extract concept names from question columns
        concept_names = self._extract_concept_names(column_info)

        # Categorize columns
        demographic_cols = [col.name for col in column_info if col.column_type == 'demographic']
        question_cols = [col.name for col in column_info if col.column_type == 'question']

        logger.info(f"Found {len(concept_names)} concepts")
        logger.info(f"Demographic columns: {len(demographic_cols)}")
        logger.info(f"Question columns: {len(question_cols)}")

        return GroundTruthData(
            df=df,
            file_path=file_path,
            column_info=column_info,
            concept_names=concept_names,
            demographic_columns=demographic_cols,
            question_columns=question_cols,
            respondent_count=len(df)
        )

    def _analyze_columns(self, df: pd.DataFrame) -> List[ColumnInfo]:
        """
        Analyze DataFrame columns to identify their types and properties.

        Args:
            df: DataFrame to analyze

        Returns:
            List of ColumnInfo objects
        """
        column_info = []

        for idx, col_name in enumerate(df.columns):
            col_type, concept_name, question_id = self._classify_column(col_name)

            column_info.append(ColumnInfo(
                name=col_name,
                index=idx,
                column_type=col_type,
                concept_name=concept_name,
                question_id=question_id
            ))

        return column_info

    def _classify_column(self, col_name: str) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Classify a column by its name.

        Args:
            col_name: Column name

        Returns:
            Tuple of (column_type, concept_name, question_id)
        """
        # Check if it's a demographic column
        for pattern in self.DEMOGRAPHIC_PATTERNS:
            if pattern.upper() in col_name.upper():
                return ('demographic', None, None)

        # Check if it's a concept assignment column
        for pattern in self.CONCEPT_ASSIGNMENT_PATTERNS:
            if pattern in col_name:
                return ('concept_assignment', None, None)

        # Check if it's a question column (has question ID pattern)
        question_id_match = self.QUESTION_ID_PATTERN.search(col_name)
        if question_id_match:
            question_id = question_id_match.group(1)

            # Extract concept name (everything after the question ID)
            # Format: "(QUESTIONID) Question Text - Concept Name"
            parts = col_name.split(' - ', 1)
            if len(parts) == 2:
                concept_name = parts[1].strip()
            else:
                concept_name = None

            return ('question', concept_name, question_id)

        # Default to metadata
        return ('metadata', None, None)

    def _extract_concept_names(self, column_info: List[ColumnInfo]) -> List[str]:
        """
        Extract unique concept names from question columns.

        Args:
            column_info: List of ColumnInfo objects

        Returns:
            List of unique concept names
        """
        concept_names = set()

        for col in column_info:
            if col.column_type == 'question' and col.concept_name:
                concept_names.add(col.concept_name)

        return sorted(list(concept_names))

    def get_question_scale_info(self, df: pd.DataFrame, column_name: str) -> Dict[str, any]:
        """
        Analyze a question column to determine its scale type and values.

        Args:
            df: DataFrame containing the column
            column_name: Name of column to analyze

        Returns:
            Dictionary with scale information
        """
        if column_name not in df.columns:
            return {}

        values = df[column_name].dropna().unique()

        # Try to parse scale values
        scale_values = []
        for val in values:
            if isinstance(val, str):
                # Check for format like "(4) Probably would"
                match = re.match(r'\((\d+)\)', val)
                if match:
                    scale_values.append(int(match.group(1)))

        if scale_values:
            return {
                'scale_type': 'likert',
                'min_value': min(scale_values),
                'max_value': max(scale_values),
                'num_points': len(set(scale_values)),
                'sample_values': list(values[:5])
            }
        else:
            return {
                'scale_type': 'unknown',
                'unique_values': len(values),
                'sample_values': list(values[:5])
            }


def main():
    """CLI entry point for testing the loader."""
    import sys
    from .study_catalog import StudyCatalog

    logging.basicConfig(level=logging.INFO)

    # Test with iGaming US market
    catalog = StudyCatalog()
    study = catalog.get_study('61405445-01')

    if not study:
        print("Study not found")
        sys.exit(1)

    market = study.get_market('US')
    if not market or not market.excel_files:
        print("US market or Excel file not found")
        sys.exit(1)

    loader = GroundTruthLoader()
    data = loader.load(market.excel_files[0])

    print(f"\n=== Ground Truth Data Summary ===")
    print(f"File: {data.file_path.name}")
    print(f"Respondents: {data.respondent_count}")
    print(f"Concepts: {len(data.concept_names)}")
    print(f"  {', '.join(data.concept_names)}")
    print(f"\nDemographic columns: {len(data.demographic_columns)}")
    for col in data.demographic_columns[:5]:
        print(f"  - {col}")
    print(f"\nQuestion columns: {len(data.question_columns)}")
    print(f"  Sample: {data.question_columns[:3]}")

    # Analyze a sample question
    if data.question_columns:
        sample_col = data.question_columns[0]
        scale_info = loader.get_question_scale_info(data.df, sample_col)
        print(f"\nSample question analysis: {sample_col}")
        print(f"  Scale info: {scale_info}")


if __name__ == "__main__":
    main()
