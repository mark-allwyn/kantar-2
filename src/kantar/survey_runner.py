"""
Survey runner for Kantar markets.

Orchestrates the complete pipeline:
1. Load concepts from PPTX
2. Load ground truth for demographics
3. Generate synthetic respondents
4. Format output to match Kantar Excel structure
"""

import random
from pathlib import Path
from typing import List, Dict, Optional
import logging
from datetime import datetime

from ..parsers.concept_parser import Concept
from ..persona.generator import PersonaGenerator
from ..survey.survey_engine import SurveyEngine
from ..survey.question_handler import QuestionHandler
from ..ssr.rating_engine import RatingEngine
from ..ssr.embeddings import EmbeddingService
from ..scales.registry import create_default_scales
from ..llm.client import LLMClient
from .study_catalog import StudyCatalog
from .data_loader import GroundTruthLoader
from .concept_extractor import ConceptExtractor
from .column_mapper import ColumnMapper
from .excel_formatter import KantarExcelFormatter

logger = logging.getLogger(__name__)


class KantarSurveyRunner:
    """
    Orchestrates synthetic survey generation for Kantar markets.
    """

    def __init__(self,
                 model: str = "gpt-4o-mini",
                 embedding_model: str = "text-embedding-3-small"):
        """
        Initialize the survey runner.

        Args:
            model: LLM model for response generation
            embedding_model: Model for embeddings
        """
        self.model = model
        self.embedding_model = embedding_model

        # Initialize components
        self.catalog = StudyCatalog()
        self.concept_extractor = ConceptExtractor(model="gpt-4o")  # Use GPT-4 for extraction
        self.ground_truth_loader = GroundTruthLoader()
        self.column_mapper = ColumnMapper()

        # These will be initialized per-run
        self.llm_client = None
        self.embedding_service = None
        self.rating_engine = None
        self.question_handler = None
        self.survey_engine = None
        self.persona_generator = None

    def generate_for_market(self,
                           study_id: str,
                           market_code: str,
                           num_respondents: Optional[int] = None,
                           output_dir: Optional[Path] = None,
                           num_concepts_per_respondent: int = 3) -> Path:
        """
        Generate synthetic data for a specific market.

        Args:
            study_id: Study ID (e.g., '61405445-01')
            market_code: Market code (e.g., 'US')
            num_respondents: Number of respondents (None = match ground truth)
            output_dir: Output directory (None = use default)
            num_concepts_per_respondent: Concepts per respondent (default: 3)

        Returns:
            Path to generated Excel file

        Raises:
            ValueError: If study or market not found
        """
        logger.info(f"Starting generation for {study_id} - {market_code}")

        # Step 1: Load study and market info
        study = self.catalog.get_study(study_id)
        if not study:
            raise ValueError(f"Study not found: {study_id}")

        market = study.get_market(market_code)
        if not market or not market.is_complete:
            raise ValueError(f"Market not found or incomplete: {market_code}")

        # Step 2: Extract concepts from PPTX
        logger.info("Extracting concepts from PPTX...")
        concepts = self.concept_extractor.extract_from_pptx(market.pptx_files[0])
        concept_names = [c.name for c in concepts]
        logger.info(f"Extracted {len(concepts)} concepts: {concept_names}")

        # Step 3: Load ground truth for demographics and concept mapping
        logger.info("Loading ground truth data...")
        ground_truth = self.ground_truth_loader.load(market.excel_files[0])

        # Determine number of respondents
        if num_respondents is None:
            num_respondents = ground_truth.respondent_count
        logger.info(f"Generating {num_respondents} respondents")

        # Step 4: Match concept names to ground truth
        logger.info("Matching concept names...")
        concept_mapping = self.column_mapper.match_concept_names(
            concept_names,
            ground_truth.concept_names
        )

        # Step 5: Initialize survey components
        logger.info("Initializing survey components...")
        self._initialize_components()

        # Convert concepts to dict format
        concept_dicts = [
            {
                'id': c.id,
                'name': c.name,
                'description': c.description,
                'full_text': c.full_text,
                'price': c.price,
                'features': c.features,
                'occasion': c.occasion
            }
            for c in concepts
        ]

        # Update survey engine with concepts
        self.survey_engine.concepts = concept_dicts

        # Step 6: Generate respondents
        logger.info("Generating synthetic respondents...")
        respondent_data_list = []

        for i in range(num_respondents):
            if (i + 1) % 10 == 0:
                logger.info(f"  Generated {i + 1}/{num_respondents} respondents")

            # Generate persona
            persona = self.persona_generator.generate_persona()

            # Run survey
            respondent_data = self.survey_engine.run_survey_for_respondent(
                persona=persona,
                concepts_to_test=concept_dicts,
                randomize_concepts=True,
                num_concepts_per_respondent=num_concepts_per_respondent
            )

            respondent_data_list.append(respondent_data)

        logger.info(f"Generated {len(respondent_data_list)} respondents")

        # Step 7: Format output using Kantar formatter
        logger.info("Formatting output to Kantar Excel structure...")
        formatter = KantarExcelFormatter(
            template_path=market.excel_files[0],
            concept_mapping=concept_mapping
        )

        df = formatter.format_to_dataframe(respondent_data_list, concept_names)

        # Step 8: Save to Excel
        if output_dir is None:
            output_dir = Path("data/synthetic/kantar") / study.study_id / market_code
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"synthetic_{market_code}_{num_respondents}resp_{timestamp}.xlsx"

        formatter.save_to_excel(df, str(output_file))
        logger.info(f"Saved to: {output_file}")

        # Also save metadata
        metadata = {
            'study_id': study_id,
            'study_name': study.study_name,
            'market_code': market_code,
            'num_respondents': num_respondents,
            'num_concepts': len(concepts),
            'concepts': concept_names,
            'concept_mapping': concept_mapping,
            'model': self.model,
            'num_concepts_per_respondent': num_concepts_per_respondent,
            'timestamp': timestamp,
            'ground_truth_path': str(market.excel_files[0]),
            'synthetic_path': str(output_file)
        }

        import json
        metadata_file = output_dir / f"metadata_{market_code}_{timestamp}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved metadata to: {metadata_file}")

        return output_file

    def generate_for_study(self,
                          study_id: str,
                          num_respondents: Optional[int] = None,
                          output_dir: Optional[Path] = None) -> Dict[str, Path]:
        """
        Generate synthetic data for all markets in a study.

        Args:
            study_id: Study ID
            num_respondents: Number of respondents per market
            output_dir: Output directory

        Returns:
            Dict mapping market code to output file path
        """
        study = self.catalog.get_study(study_id)
        if not study:
            raise ValueError(f"Study not found: {study_id}")

        logger.info(f"Generating data for study: {study.study_name}")
        logger.info(f"Markets: {study.complete_markets}")

        results = {}

        for market_code in study.complete_markets:
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing market: {market_code}")
            logger.info(f"{'='*60}\n")

            try:
                output_file = self.generate_for_market(
                    study_id=study_id,
                    market_code=market_code,
                    num_respondents=num_respondents,
                    output_dir=output_dir
                )
                results[market_code] = output_file
                logger.info(f"✓ {market_code}: SUCCESS")

            except Exception as e:
                logger.error(f"✗ {market_code}: FAILED - {e}")
                results[market_code] = None

        # Summary
        logger.info(f"\n{'='*60}")
        logger.info("GENERATION SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Study: {study.study_name}")
        logger.info(f"Total markets: {len(study.complete_markets)}")
        logger.info(f"Successful: {sum(1 for v in results.values() if v is not None)}")
        logger.info(f"Failed: {sum(1 for v in results.values() if v is None)}")

        return results

    def _initialize_components(self):
        """Initialize survey generation components."""
        # LLM client
        self.llm_client = LLMClient(model=self.model)

        # Embedding service
        self.embedding_service = EmbeddingService(model_id=self.embedding_model)

        # Scale registry
        scale_registry = create_default_scales()

        # Rating engine
        self.rating_engine = RatingEngine(
            scale_registry=scale_registry,
            embedding_service=self.embedding_service
        )

        # Question handler
        self.question_handler = QuestionHandler(
            llm_client=self.llm_client,
            rating_engine=self.rating_engine
        )

        # Survey engine
        self.survey_engine = SurveyEngine(
            question_handler=self.question_handler,
            concepts=[]
        )

        # Persona generator
        self.persona_generator = PersonaGenerator()


def main():
    """CLI entry point for testing."""
    import sys
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    parser = argparse.ArgumentParser(description='Generate synthetic Kantar survey data')
    parser.add_argument('--study', required=True, help='Study ID (e.g., 61405445-01)')
    parser.add_argument('--market', help='Market code (e.g., US)')
    parser.add_argument('--all-markets', action='store_true', help='Generate for all markets')
    parser.add_argument('--num-respondents', type=int, help='Number of respondents')
    parser.add_argument('--model', default='gpt-4o-mini', help='LLM model')
    parser.add_argument('--output-dir', help='Output directory')

    args = parser.parse_args()

    runner = KantarSurveyRunner(model=args.model)

    if args.all_markets:
        results = runner.generate_for_study(
            study_id=args.study,
            num_respondents=args.num_respondents,
            output_dir=Path(args.output_dir) if args.output_dir else None
        )
    elif args.market:
        output_file = runner.generate_for_market(
            study_id=args.study,
            market_code=args.market,
            num_respondents=args.num_respondents,
            output_dir=Path(args.output_dir) if args.output_dir else None
        )
        print(f"\n✓ Generated: {output_file}")
    else:
        print("Error: Must specify either --market or --all-markets")
        sys.exit(1)


if __name__ == "__main__":
    main()
