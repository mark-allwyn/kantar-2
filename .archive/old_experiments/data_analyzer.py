"""
Data Analyzer Module

Analyzes the Excel respondent data to understand the output format.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import pandas as pd
import openpyxl


@dataclass
class ColumnInfo:
    """Information about a column in the dataset"""
    name: str
    index: int
    dtype: str
    sample_values: List[Any] = field(default_factory=list)
    unique_count: int = 0
    null_count: int = 0
    belongs_to_concept: Optional[str] = None  # Which concept this column relates to


@dataclass
class DataStructure:
    """Structure of the Excel dataset"""
    columns: List[ColumnInfo] = field(default_factory=list)
    num_rows: int = 0
    num_columns: int = 0
    demographic_columns: List[str] = field(default_factory=list)
    question_columns: Dict[str, List[str]] = field(default_factory=dict)  # concept -> columns
    id_columns: List[str] = field(default_factory=list)


class DataAnalyzer:
    """Analyzer for Excel respondent data files"""

    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.df = None

    def analyze(self) -> DataStructure:
        """Analyze the Excel file structure"""
        # Read Excel file
        self.df = pd.read_excel(self.excel_path, sheet_name=0)

        structure = DataStructure()
        structure.num_rows = len(self.df)
        structure.num_columns = len(self.df.columns)

        # Analyze each column
        for idx, col_name in enumerate(self.df.columns):
            col_data = self.df[col_name]

            # Get sample values (non-null)
            sample_values = col_data.dropna().head(5).tolist()

            col_info = ColumnInfo(
                name=col_name,
                index=idx,
                dtype=str(col_data.dtype),
                sample_values=sample_values,
                unique_count=col_data.nunique(),
                null_count=col_data.isna().sum()
            )

            # Identify which concept this column belongs to
            for concept_num in range(1, 9):
                if f'Concept {concept_num}' in col_name or f'C{concept_num}' in col_name:
                    col_info.belongs_to_concept = f'Concept {concept_num}'
                    break

            structure.columns.append(col_info)

        # Categorize columns
        self._categorize_columns(structure)

        return structure

    def _categorize_columns(self, structure: DataStructure):
        """Categorize columns into demographics, questions, IDs, etc."""

        # Common demographic indicators
        demo_keywords = ['gender', 'sex', 'age', 'occupation', 'serial', 'date', 'sample']

        # ID indicators
        id_keywords = ['serial', 'id', 'stores pri', 'parent']

        for col_info in structure.columns:
            col_lower = col_info.name.lower()

            # Identify demographic columns
            if any(keyword in col_lower for keyword in demo_keywords):
                if not any(keyword in col_lower for keyword in ['quota', 'screener']):
                    structure.demographic_columns.append(col_info.name)

            # Identify ID columns
            if any(keyword in col_lower for keyword in id_keywords):
                structure.id_columns.append(col_info.name)

            # Identify question columns by concept
            if col_info.belongs_to_concept:
                if col_info.belongs_to_concept not in structure.question_columns:
                    structure.question_columns[col_info.belongs_to_concept] = []
                structure.question_columns[col_info.belongs_to_concept].append(col_info.name)

    def get_column_format(self, column_name: str) -> Dict[str, Any]:
        """Get detailed format information for a specific column"""
        if self.df is None:
            raise ValueError("Must run analyze() first")

        if column_name not in self.df.columns:
            raise ValueError(f"Column {column_name} not found")

        col_data = self.df[column_name]

        # Analyze the format
        sample_values = col_data.dropna().head(10).tolist()

        # Check if it uses the "(code) text" format
        has_code_format = False
        if sample_values and isinstance(sample_values[0], str):
            has_code_format = sample_values[0].startswith('(') and ')' in sample_values[0]

        return {
            'column_name': column_name,
            'dtype': str(col_data.dtype),
            'sample_values': sample_values,
            'unique_values': col_data.nunique(),
            'has_code_format': has_code_format,
            'null_percentage': (col_data.isna().sum() / len(col_data)) * 100
        }

    def extract_question_pattern(self, question_id: str) -> Dict[str, Any]:
        """Extract the response pattern for a specific question across all concepts"""
        if self.df is None:
            raise ValueError("Must run analyze() first")

        # Find columns matching this question ID
        matching_cols = [col for col in self.df.columns if question_id in col]

        patterns = {}
        for col in matching_cols:
            patterns[col] = self.get_column_format(col)

        return patterns

    def to_dict(self, structure: DataStructure) -> Dict:
        """Convert structure to dictionary for JSON serialization"""
        return {
            'num_rows': int(structure.num_rows),
            'num_columns': int(structure.num_columns),
            'columns': [
                {
                    'name': col.name,
                    'index': int(col.index),
                    'dtype': col.dtype,
                    'sample_values': [str(v) for v in col.sample_values],
                    'unique_count': int(col.unique_count),
                    'null_count': int(col.null_count),
                    'belongs_to_concept': col.belongs_to_concept
                }
                for col in structure.columns
            ],
            'demographic_columns': structure.demographic_columns,
            'question_columns': structure.question_columns,
            'id_columns': structure.id_columns
        }
