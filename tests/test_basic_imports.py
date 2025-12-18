"""
Test Basic Imports and Module Structure

Run this first to verify all modules can be imported.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all modules can be imported"""
    errors = []

    # Test parsers
    try:
        from src.parsers.questionnaire_parser import QuestionnaireParser
        from src.parsers.concept_parser import ConceptParser
        from src.parsers.data_analyzer import DataAnalyzer
        print("✓ Parsers module")
    except Exception as e:
        errors.append(f"Parsers: {e}")
        print(f"✗ Parsers: {e}")

    # Test logic
    try:
        from src.logic.conditional_logic import SurveyLogic, create_standard_survey_logic
        print("✓ Logic module")
    except Exception as e:
        errors.append(f"Logic: {e}")
        print(f"✗ Logic: {e}")

    # Test scales
    try:
        from src.scales.scale import Scale, RatingResult
        from src.scales.registry import ScaleRegistry, create_default_scales
        print("✓ Scales module")
    except Exception as e:
        errors.append(f"Scales: {e}")
        print(f"✗ Scales: {e}")

    # Test SSR
    try:
        from src.ssr.embeddings import EmbeddingService
        from src.ssr.similarity import cosine_similarity
        from src.ssr.rating_engine import RatingEngine
        print("✓ SSR module")
    except Exception as e:
        errors.append(f"SSR: {e}")
        print(f"✗ SSR: {e}")

    # Test persona
    try:
        from src.persona.generator import PersonaGenerator, Persona
        print("✓ Persona module")
    except Exception as e:
        errors.append(f"Persona: {e}")
        print(f"✗ Persona: {e}")

    # Test LLM
    try:
        from src.llm.client import LLMClient
        from src.llm.prompts import PromptBuilder
        print("✓ LLM module")
    except Exception as e:
        errors.append(f"LLM: {e}")
        print(f"✗ LLM: {e}")

    # Test survey
    try:
        from src.survey.question_handler import QuestionHandler
        from src.survey.survey_engine import SurveyEngine
        print("✓ Survey module")
    except Exception as e:
        errors.append(f"Survey: {e}")
        print(f"✗ Survey: {e}")

    # Test output
    try:
        from src.output.excel_formatter import ExcelFormatter
        print("✓ Output module")
    except Exception as e:
        errors.append(f"Output: {e}")
        print(f"✗ Output: {e}")

    # Test validation
    try:
        from src.validation.metrics import ValidationMetrics
        print("✓ Validation module")
    except Exception as e:
        errors.append(f"Validation: {e}")
        print(f"✗ Validation: {e}")

    # Test visualization
    try:
        from src.visualization.comparison_plots import ComparisonVisualizer
        print("✓ Visualization module")
    except Exception as e:
        errors.append(f"Visualization: {e}")
        print(f"✗ Visualization: {e}")

    if errors:
        print(f"\n❌ {len(errors)} modules failed to import:")
        for error in errors:
            print(f"   {error}")
        return False
    else:
        print("\n✅ All modules imported successfully!")
        return True


if __name__ == '__main__':
    success = test_imports()
    sys.exit(0 if success else 1)
