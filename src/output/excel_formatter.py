"""
Excel Output Formatter

Formats synthetic survey data to match ground truth Excel structure.
"""

import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

from ..survey.survey_engine import RespondentData, ConceptResponse


class ExcelFormatter:
    """Formats survey data for Excel output"""

    def __init__(self):
        """Initialize formatter"""
        pass

    def format_to_dataframe(self,
                           respondent_data_list: List[RespondentData],
                           concept_names: List[str] = None) -> pd.DataFrame:
        """
        Format respondent data to DataFrame matching ground truth structure.

        Args:
            respondent_data_list: List of RespondentData
            concept_names: List of concept names (for column naming)

        Returns:
            DataFrame in ground truth format
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
            base_row = {
                'SERIAL': respondent_data.respondent_id,
                'DATE': respondent_data.timestamp.split('T')[0],
                'Gender': persona.demographics.get('gender', ''),
                '(SEX) SEX': persona.demographics.get('gender', ''),
                'AGE': persona.demographics.get('age', ''),
                '(AGEQUOTA) AGEBANDS': persona.demographics.get('age_band', ''),
                '(OCCUPATION_SCR) OCCUPATION SCREENER': persona.demographics.get('occupation', ''),
                '(GROUPFMR) SAMPLE TYPE': persona.psychographics.get('target_group', ''),
                'Stores pri': respondent_data.respondent_id,  # Use as persistent ID
            }

            # Add psychographics
            # S4: Category Buyer
            category_buyer = persona.psychographics.get('category_buyer', [])
            if isinstance(category_buyer, list):
                base_row['(CATBUYER) PRODUCTS / SERVICES BOUGHT'] = ', '.join(category_buyer)
            else:
                base_row['(CATBUYER) PRODUCTS / SERVICES BOUGHT'] = str(category_buyer)

            # S5: Category Non Rejector (what would you NEVER spend money on)
            category_non_rejector = persona.psychographics.get('category_non_rejector', [])
            if isinstance(category_non_rejector, list):
                base_row['(CATNREJ) WOULD NEVER SPEND MONEY ON'] = ', '.join(category_non_rejector)
            else:
                base_row['(CATNREJ) WOULD NEVER SPEND MONEY ON'] = str(category_non_rejector)

            # S8: SC Player Type (derived from S4)
            sc_player_type = persona.psychographics.get('sc_player_type', 'Main')
            base_row['(SCPLAYER) SC PLAYER TYPE'] = sc_player_type

            # S9: Brand Buyers
            brand_buyers = persona.psychographics.get('brand_buyers', [])
            if isinstance(brand_buyers, list):
                base_row['(BRDBUY) BRANDS BOUGHT'] = ','.join(brand_buyers)
            else:
                base_row['(BRDBUY) BRANDS BOUGHT'] = str(brand_buyers)

            # Add inertia
            base_row['Inertia'] = persona.psychographics.get('inertia', '')

            # Process each concept response
            for concept_response in respondent_data.concept_responses:
                concept_num = concept_response.position
                concept_prefix = f"Concept {concept_num}"

                # Add position
                base_row[f'{concept_prefix}: Dummy: Position'] = concept_num

                # Add concept ID
                base_row[f'{concept_prefix}: Concept ID'] = concept_response.concept_id

                # Map responses to columns
                response_mapping = {
                    'B2': f'{concept_prefix}: (PRPURINT) PRICED PURCHASE INTENT',
                    'B21': f'{concept_prefix}: (BARRIERS) BARRIERS TO PURCHASE',
                    'B3': f'{concept_prefix}: (UNIQNESS) UNIQUENESS',
                    'B4': f'{concept_prefix}: (PRVALMNY) VALUE FOR MONEY',
                    'B6': f'{concept_prefix}: (LIKBILTY) LIKEABILITY',
                    'B7': f'{concept_prefix}: (INCREMNT) BUY INSTEAD IF NOT AVAILABLE',
                    'B11': f'{concept_prefix}: (RELVANCE) RELEVANCE',
                    'B11a': f'{concept_prefix}: (PLAYFLNS) PLAYFULNESS',
                    'B12': f'{concept_prefix}: (EXCITMENT) EXCITEMENT',
                    'B13': f'{concept_prefix}: Understanding Other Category',
                    'B14': f'{concept_prefix}: (BELVBLTY) BELIEVEABILITY',
                    'B15': f'{concept_prefix}: (LIKES_STD) LIKES',
                    'B16': f'{concept_prefix}: DISLIKES',
                    'B22': f'{concept_prefix}: WOULD BUY AS GIFT',
                    'B23': f'{concept_prefix}: (OCCASIONS) GIFT OCCASIONS',
                    'B24': f'{concept_prefix}: PLEASED WITH GIFT',
                }

                for question_id, col_name in response_mapping.items():
                    if question_id in concept_response.responses:
                        response = concept_response.responses[question_id]
                        base_row[col_name] = response.formatted_response
                    else:
                        base_row[col_name] = ''

            rows.append(base_row)

        # Create DataFrame
        df = pd.DataFrame(rows)

        return df

    def save_to_excel(self,
                     df: pd.DataFrame,
                     output_path: str,
                     sheet_name: str = "Synthetic Data"):
        """
        Save DataFrame to Excel file.

        Args:
            df: DataFrame to save
            output_path: Path to output Excel file
            sheet_name: Name of the sheet
        """
        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Save to Excel
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"✓ Saved {len(df)} rows to {output_path}")

    def format_and_save(self,
                       respondent_data_list: List[RespondentData],
                       output_path: str,
                       concept_names: List[str] = None) -> pd.DataFrame:
        """
        Format and save in one step.

        Args:
            respondent_data_list: List of RespondentData
            output_path: Path to output Excel file
            concept_names: List of concept names

        Returns:
            DataFrame that was saved
        """
        df = self.format_to_dataframe(respondent_data_list, concept_names)
        self.save_to_excel(df, output_path)
        return df

    def create_comparison_summary(self,
                                 ground_truth_df: pd.DataFrame,
                                 synthetic_df: pd.DataFrame,
                                 question_columns: List[str]) -> pd.DataFrame:
        """
        Create summary comparison of ground truth vs synthetic.

        Args:
            ground_truth_df: Ground truth DataFrame
            synthetic_df: Synthetic DataFrame
            question_columns: Columns to compare

        Returns:
            Summary DataFrame
        """
        summary_rows = []

        for col in question_columns:
            if col not in ground_truth_df.columns or col not in synthetic_df.columns:
                continue

            gt_data = ground_truth_df[col].dropna()
            syn_data = synthetic_df[col].dropna()

            summary_rows.append({
                'Column': col,
                'GT_Count': len(gt_data),
                'Syn_Count': len(syn_data),
                'GT_Mean': gt_data.mean() if pd.api.types.is_numeric_dtype(gt_data) else None,
                'Syn_Mean': syn_data.mean() if pd.api.types.is_numeric_dtype(syn_data) else None,
                'GT_Std': gt_data.std() if pd.api.types.is_numeric_dtype(gt_data) else None,
                'Syn_Std': syn_data.std() if pd.api.types.is_numeric_dtype(syn_data) else None,
            })

        return pd.DataFrame(summary_rows)
