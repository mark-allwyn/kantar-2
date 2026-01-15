"""
Kantar Excel formatter for matching ground truth template format.

Extends the base ExcelFormatter to produce output that exactly matches
the Kantar ground truth Excel structure.
"""

import pandas as pd
from typing import List, Dict, Optional
from pathlib import Path
import logging

from ..survey.survey_engine import RespondentData, ConceptResponse
from ..output.excel_formatter import ExcelFormatter
from .column_mapper import ColumnMapper

logger = logging.getLogger(__name__)


class KantarExcelFormatter(ExcelFormatter):
    """
    Formatter for Kantar survey data.

    Produces Excel output matching exact Kantar ground truth format,
    including column naming, ordering, and response formatting.
    """

    def __init__(self,
                 template_path: Optional[Path] = None,
                 concept_mapping: Optional[Dict[str, str]] = None):
        """
        Initialize the Kantar formatter.

        Args:
            template_path: Path to ground truth Excel for template
            concept_mapping: Map from extracted concept names to GT names
        """
        super().__init__()
        self.template_path = template_path
        self.concept_mapping = concept_mapping or {}
        self.column_mapper = ColumnMapper()
        self.template_columns = None

        if template_path and template_path.exists():
            self._load_template_structure()

    def _load_template_structure(self):
        """Load template column structure from ground truth."""
        try:
            template_df = pd.read_excel(self.template_path)
            self.template_columns = list(template_df.columns)
            logger.info(f"Loaded template with {len(self.template_columns)} columns")
        except Exception as e:
            logger.warning(f"Failed to load template: {e}")
            self.template_columns = None

    def format_to_dataframe(self,
                           respondent_data_list: List[RespondentData],
                           concept_names: List[str] = None) -> pd.DataFrame:
        """
        Format respondent data to DataFrame matching Kantar structure.

        Args:
            respondent_data_list: List of RespondentData
            concept_names: List of concept names (extracted from PPTX)

        Returns:
            DataFrame in Kantar ground truth format
        """
        if not respondent_data_list:
            return pd.DataFrame()

        rows = []

        for respondent_data in respondent_data_list:
            # Skip screened out respondents
            if respondent_data.metadata.get('screened_out'):
                continue

            persona = respondent_data.persona

            # Create base row with demographics
            base_row = self._build_demographic_columns(respondent_data, persona)

            # Add concept assignment columns
            base_row.update(self._build_concept_assignment_columns(respondent_data, concept_names))

            # Process each concept response
            for concept_response in respondent_data.concept_responses:
                concept_name = self._get_concept_name(concept_response, concept_names)

                # Map to ground truth concept name if mapping provided
                gt_concept_name = self.concept_mapping.get(concept_name, concept_name)

                # Add question responses for this concept
                question_columns = self._build_question_columns(
                    concept_response,
                    gt_concept_name
                )
                base_row.update(question_columns)

            rows.append(base_row)

        # Create DataFrame
        df = pd.DataFrame(rows)

        # Reorder columns to match template if available
        if self.template_columns:
            df = self._reorder_to_template(df)

        return df

    def _build_demographic_columns(self,
                                   respondent_data: RespondentData,
                                   persona) -> Dict:
        """Build demographic columns matching Kantar format."""
        demographics = {
            'SERIAL': respondent_data.respondent_id,
            'DATE': respondent_data.timestamp.split('T')[0],
            'Gender': persona.demographics.get('gender', ''),
            '(SEX_NONBINARY) SEX': persona.demographics.get('gender', ''),
            'AGE': persona.demographics.get('age', ''),
            '(AGEQUOTA) AGEBANDS': persona.demographics.get('age_band', ''),
            '(OCCUPATION_SCR) OCCUPATION SCREENER': persona.demographics.get('occupation', ''),
            '(GROUPFMR) SAMPLE TYPE': persona.psychographics.get('target_group', ''),
        }

        # Add category buyer
        category_buyer = persona.psychographics.get('category_buyer', [])
        if isinstance(category_buyer, list):
            demographics['(CATBUYER) PRODUCTS / SERVICES BOUGHT'] = ', '.join(category_buyer)
        else:
            demographics['(CATBUYER) PRODUCTS / SERVICES BOUGHT'] = str(category_buyer)

        # Add brand buyers
        # Brand buyers is a single-select field in persona (list with one item)
        # The value may already contain commas (e.g., "Brand A,Brand B") which are atomic
        brand_buyers = persona.psychographics.get('brand_buyers', [])
        if isinstance(brand_buyers, list) and len(brand_buyers) > 0:
            demographics['(BRDBUY) BRANDS BOUGHT'] = brand_buyers[0]
        else:
            demographics['(BRDBUY) BRANDS BOUGHT'] = str(brand_buyers) if brand_buyers else ''

        return demographics

    def _build_concept_assignment_columns(self,
                                         respondent_data: RespondentData,
                                         concept_names: List[str]) -> Dict:
        """Build concept assignment/rotation columns."""
        assignment = {}

        # Add concept block column (if exists in template)
        assignment['Concept_block_conceptbrands, helper'] = ''

        # Add position columns for each concept
        if concept_names:
            for concept_response in respondent_data.concept_responses:
                concept_name = self._get_concept_name(concept_response, concept_names)
                gt_concept_name = self.concept_mapping.get(concept_name, concept_name)

                # Position column (e.g., " - US Pulse Play  " = 2.0)
                position_col = f" - {gt_concept_name}  "
                assignment[position_col] = float(concept_response.position)

        return assignment

    def _build_question_columns(self,
                               concept_response: ConceptResponse,
                               concept_name: str) -> Dict:
        """Build question columns for a concept."""
        columns = {}

        # DEBUG: Log what responses are available
        logger.debug(f"Building columns for concept: {concept_name}")
        logger.debug(f"Available response keys: {list(concept_response.responses.keys())}")

        # Question ID to column mapping
        question_mapping = {
            'B2': 'UNPURINT',  # Unpriced purchase intent
            'B3': 'UNIQNESS',
            'B4': 'UNPRICEP',  # Expected price comparison
            'B6': 'LIKBILTY',
            'B7': 'INCREMNT',
            'B11': 'RELVANCE',
            'B11a': 'PLAYFLNS',
            'B12': 'EXCITMENT',
            'B13': 'Understanding Other Category',
            'B14': 'BELVBLTY',
            'B15': 'LIKES_STD',
            'B16': 'DISLIKES',
            'B21': 'BARRIERS',
            'B22': 'WOULD BUY AS GIFT',
            'B23': 'OCCASIONS',
            'B24': 'PLEASED WITH GIFT',
        }

        for question_id, kantar_id in question_mapping.items():
            if question_id in concept_response.responses:
                response = concept_response.responses[question_id]

                # Build Kantar column name
                if kantar_id in ['Understanding Other Category', 'DISLIKES', 'WOULD BUY AS GIFT']:
                    # These don't use the (ID) format
                    col_name = f"{kantar_id} - {concept_name}  "
                else:
                    # Use column mapper for standard format
                    col_name = self.column_mapper.build_kantar_column_name(
                        kantar_id,
                        concept_name
                    )

                logger.debug(f"Adding {question_id} -> {col_name}: {response.formatted_response}")
                columns[col_name] = response.formatted_response
            else:
                # Add empty column if question not answered
                if kantar_id not in ['Understanding Other Category', 'DISLIKES', 'WOULD BUY AS GIFT']:
                    col_name = self.column_mapper.build_kantar_column_name(
                        kantar_id,
                        concept_name
                    )
                    columns[col_name] = ''

        return columns

    def _get_concept_name(self,
                         concept_response: ConceptResponse,
                         concept_names: List[str]) -> str:
        """Get concept name from response."""
        if concept_names and concept_response.position <= len(concept_names):
            return concept_names[concept_response.position - 1]
        else:
            return concept_response.concept_id

    def _reorder_to_template(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reorder DataFrame columns to match template."""
        logger.debug(f"Before reorder: {len(df)} rows, {len(df.columns)} columns")
        logger.debug(f"Template has: {len(self.template_columns)} columns")

        # Get columns that exist in both
        common_cols = [col for col in self.template_columns if col in df.columns]

        # Get columns in df but not in template
        extra_cols = [col for col in df.columns if col not in self.template_columns]

        logger.debug(f"Common: {len(common_cols)}, Extra: {len(extra_cols)}")
        if len(extra_cols) > 0:
            logger.debug(f"Extra columns (first 10): {extra_cols[:10]}")

        # Reorder: template columns first, then extras
        ordered_cols = common_cols + extra_cols

        # Add missing template columns with NaN
        for col in self.template_columns:
            if col not in df.columns:
                df[col] = None

        # Reorder
        df = df[self.template_columns]

        logger.info(f"Reordered to template: {len(common_cols)} matching, {len(extra_cols)} extra")
        logger.debug(f"After reorder: {len(df)} rows")

        return df


def main():
    """CLI entry point for testing the formatter."""
    import sys
    from ..kantar.study_catalog import StudyCatalog
    from ..kantar.data_loader import GroundTruthLoader
    from ..kantar.concept_extractor import ConceptExtractor
    from ..kantar.column_mapper import ColumnMapper

    logging.basicConfig(level=logging.INFO)

    # Test with iGaming US market
    catalog = StudyCatalog()
    study = catalog.get_study('61405445-01')

    if not study:
        print("Study not found")
        sys.exit(1)

    market = study.get_market('US')
    if not market:
        print("US market not found")
        sys.exit(1)

    # Load ground truth template
    gt_path = market.excel_files[0]
    print(f"Template: {gt_path}")

    # Extract concepts
    extractor = ConceptExtractor()
    concepts = extractor.extract_from_pptx(market.pptx_files[0])
    concept_names = [c.name for c in concepts]
    print(f"Concepts: {concept_names}")

    # Load ground truth for concept mapping
    loader = GroundTruthLoader()
    gt_data = loader.load(gt_path)

    # Match concepts
    mapper = ColumnMapper()
    concept_mapping = mapper.match_concept_names(concept_names, gt_data.concept_names)
    print(f"Concept mapping: {concept_mapping}")

    # Create formatter
    formatter = KantarExcelFormatter(
        template_path=gt_path,
        concept_mapping=concept_mapping
    )

    print(f"\nFormatter initialized with {len(formatter.template_columns)} template columns")
    print("Ready for synthetic data generation")


if __name__ == "__main__":
    main()
