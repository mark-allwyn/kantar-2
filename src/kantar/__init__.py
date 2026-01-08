"""
Kantar survey data integration module.

Provides functionality for:
- Discovering and cataloging Kantar studies and markets
- Loading ground truth data
- Extracting concepts from PPTX presentations
- Generating synthetic survey responses
- Validating against ground truth
- Generating reports and dashboards
"""

__all__ = [
    'study_catalog',
    'data_loader',
    'concept_extractor',
    'column_mapper',
    'survey_runner',
    'validation_runner',
]
