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
from typing import List, Dict, Optional, Any
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
from .market_profiles import get_market_profile, list_market_profiles
from .concept_schema import validate_concepts, fill_concept_defaults
from .progress_tracker import GenerationProgressTracker
from .checkpoint_manager import CheckpointManager, create_job_id, create_job_id_custom

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
                           num_concepts_per_respondent: int = 3,
                           use_ground_truth_demographics: bool = False,
                           checkpoint_every: int = 10,
                           resume: bool = False) -> Path:
        """
        Generate synthetic data for a specific market.

        Args:
            study_id: Study ID (e.g., '61405445-01')
            market_code: Market code (e.g., 'US')
            num_respondents: Number of respondents (None = match ground truth)
            output_dir: Output directory (None = use default)
            num_concepts_per_respondent: Concepts per respondent (default: 3)
            use_ground_truth_demographics: Sample demographics from ground truth (default: False)
            checkpoint_every: Save checkpoint every N respondents (default: 10)
            resume: Resume from checkpoint if available (default: False)

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

        # Step 5: Extract demographics schema (MANDATORY in GT mode)
        logger.info("Extracting demographics schema from ground truth...")
        demographics_schema = ground_truth.get_demographics_schema()
        logger.info(f"Extracted schema with {len(demographics_schema.schema)} demographic fields")

        # Step 6: Initialize survey components
        logger.info("Initializing survey components...")
        gt_demographics = None
        if use_ground_truth_demographics:
            logger.info("Using ground truth demographics distributions for persona generation")
            gt_demographics = ground_truth.get_demographics_summary()

        self._initialize_components(
            ground_truth_demographics=gt_demographics,
            demographics_schema=demographics_schema
        )

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

        # Step 6: Setup checkpoint manager
        checkpoint_manager = CheckpointManager()
        job_id = create_job_id(study_id, market_code, num_respondents)

        # Check for existing checkpoint
        respondent_data_list = []
        start_index = 0

        if resume:
            checkpoint_data = checkpoint_manager.load_checkpoint(job_id)
            if checkpoint_data:
                logger.info(f"Resuming from checkpoint: {checkpoint_data['completed']}/{num_respondents} completed")
                respondent_data_list = checkpoint_data['respondent_data']
                start_index = len(respondent_data_list)
            else:
                logger.info("No checkpoint found, starting from beginning")

        # Step 7: Generate respondents
        logger.info(f"Generating synthetic respondents (starting from {start_index})...")

        generation_config = {
            'study_id': study_id,
            'market_code': market_code,
            'num_respondents': num_respondents,
            'num_concepts_per_respondent': num_concepts_per_respondent,
            'model': self.model,
            'use_ground_truth_demographics': use_ground_truth_demographics
        }

        with GenerationProgressTracker(
            total_respondents=num_respondents,
            description=f"Generating {market_code} respondents"
        ) as progress:
            # Update progress for already-completed respondents
            if start_index > 0:
                progress.update(start_index)

            for i in range(start_index, num_respondents):
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
                progress.update(1)

                # Save checkpoint
                if (i + 1) % checkpoint_every == 0:
                    checkpoint_manager.save_checkpoint(
                        job_id=job_id,
                        completed_respondents=respondent_data_list,
                        total_respondents=num_respondents,
                        generation_config=generation_config
                    )

        logger.info(f"Generated {len(respondent_data_list)} respondents")

        # Clean up checkpoint on successful completion
        checkpoint_manager.delete_checkpoint(job_id)

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

    def generate_from_concepts(self,
                               concepts: List[Dict],
                               num_respondents: int,
                               output_dir: Optional[Path] = None,
                               output_name: Optional[str] = None,
                               market_profile: str = 'generic',
                               custom_demographics: Optional[Dict] = None,
                               num_concepts_per_respondent: int = 3) -> Path:
        """
        Generate synthetic data from manually defined concepts (no ground truth needed).

        This method allows testing new concepts without requiring PPTX files or ground truth data.
        Uses market profiles or custom demographics for persona generation.

        Args:
            concepts: List of concept dictionaries with keys:
                     - id (required): Unique identifier
                     - name (required): Concept name
                     - description (required): Concept description
                     - price (optional): Price information
                     - features (optional): List of features
                     - occasion (optional): Usage occasion
                     - full_text (optional): Complete description
            num_respondents: Number of synthetic respondents to generate
            output_dir: Output directory (default: data/synthetic/concepts/)
            output_name: Output file name prefix (default: synthetic_concepts)
            market_profile: Market profile name for demographics (default: 'generic')
                          Options: 'US_gaming', 'UK_lottery', 'EU_general', 'generic'
            custom_demographics: Custom demographics dict (overrides market_profile)
            num_concepts_per_respondent: Concepts per respondent (default: 3)

        Returns:
            Path to generated Excel file

        Raises:
            ValueError: If concepts invalid or market_profile not found

        Example:
            >>> concepts = [
            ...     {
            ...         'id': 'NewConcept1',
            ...         'name': 'Premium Lottery',
            ...         'description': 'A lottery with enhanced odds',
            ...         'price': '$5',
            ...         'features': ['Better odds', 'Bigger prizes']
            ...     }
            ... ]
            >>> runner = KantarSurveyRunner()
            >>> output = runner.generate_from_concepts(
            ...     concepts=concepts,
            ...     num_respondents=50,
            ...     market_profile='US_gaming'
            ... )
        """
        logger.info("=" * 60)
        logger.info("GENERATING SURVEY DATA FROM CUSTOM CONCEPTS")
        logger.info("=" * 60)
        logger.info(f"Concepts: {len(concepts)}")
        logger.info(f"Respondents: {num_respondents}")
        logger.info(f"Market profile: {market_profile}")

        # Step 1: Validate concepts
        logger.info("Validating concept schema...")
        validate_concepts(concepts, strict=True)

        # Fill in default values for optional fields
        concepts = [fill_concept_defaults(c.copy()) for c in concepts]

        concept_names = [c['name'] for c in concepts]
        logger.info(f"Valid concepts: {concept_names}")

        # Step 2: Get demographics
        if custom_demographics:
            logger.info("Using custom demographics")
            demographics = custom_demographics
        else:
            logger.info(f"Loading market profile: {market_profile}")
            profile = get_market_profile(market_profile)
            demographics = profile['demographics']
            logger.info(f"Profile: {profile['name']} - {profile['description']}")

        # Step 3: Create demographics schema from profile
        logger.info("Creating demographics schema from market profile...")
        from .demographics_schema import DemographicsSchema
        demographics_schema = DemographicsSchema.from_profile(demographics)
        logger.info(f"Created schema with {len(demographics_schema.schema)} demographic fields")

        # Step 4: Initialize survey components
        logger.info("Initializing survey components...")
        self._initialize_components(
            ground_truth_demographics=None,
            custom_distributions=demographics,
            demographics_schema=demographics_schema
        )

        # Update survey engine with concepts
        self.survey_engine.concepts = concepts

        # Step 4: Generate respondents
        logger.info(f"Generating {num_respondents} synthetic respondents...")
        respondent_data_list = []

        with GenerationProgressTracker(
            total_respondents=num_respondents,
            description="Generating respondents"
        ) as progress:
            for i in range(num_respondents):
                # Generate persona
                persona = self.persona_generator.generate_persona()

                # Run survey
                respondent_data = self.survey_engine.run_survey_for_respondent(
                    persona=persona,
                    concepts_to_test=concepts,
                    randomize_concepts=True,
                    num_concepts_per_respondent=num_concepts_per_respondent
                )

                respondent_data_list.append(respondent_data)
                progress.update(1)

        logger.info(f"Generated {len(respondent_data_list)} respondents")

        # Step 5: Format output (no template - create natural column order)
        logger.info("Formatting output to Excel...")
        formatter = KantarExcelFormatter(
            template_path=None,  # No template needed
            concept_mapping={}   # No mapping needed
        )

        df = formatter.format_to_dataframe(respondent_data_list, concept_names)

        # Step 6: Save to Excel
        if output_dir is None:
            output_dir = Path("data/synthetic/concepts")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if output_name is None:
            output_name = "synthetic_concepts"
        output_file = output_dir / f"{output_name}_{num_respondents}resp_{timestamp}.xlsx"

        formatter.save_to_excel(df, str(output_file))
        logger.info(f"Saved to: {output_file}")

        # Also save metadata
        metadata = {
            'mode': 'custom_concepts',
            'num_respondents': num_respondents,
            'num_concepts': len(concepts),
            'concepts': concept_names,
            'concept_details': concepts,
            'market_profile': market_profile if not custom_demographics else 'custom',
            'demographics_source': 'custom' if custom_demographics else 'profile',
            'model': self.model,
            'num_concepts_per_respondent': num_concepts_per_respondent,
            'timestamp': timestamp,
            'synthetic_path': str(output_file)
        }

        import json
        metadata_file = output_dir / f"metadata_{output_name}_{timestamp}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved metadata to: {metadata_file}")

        logger.info("=" * 60)
        logger.info("GENERATION COMPLETE")
        logger.info("=" * 60)

        return output_file

    def _initialize_components(self,
                               ground_truth_demographics: Optional[Dict] = None,
                               custom_distributions: Optional[Dict] = None,
                               demographics_schema: Optional[Any] = None):
        """
        Initialize survey generation components.

        Args:
            ground_truth_demographics: Optional GT demographics distributions
            custom_distributions: Optional custom distributions (from profiles)
            demographics_schema: Optional DemographicsSchema for categorical validation
        """
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

        # Persona generator (with optional GT demographics, distributions, and schema)
        self.persona_generator = PersonaGenerator(
            ground_truth_demographics=ground_truth_demographics,
            custom_distributions=custom_distributions,
            demographics_schema=demographics_schema
        )


def main():
    """CLI entry point for testing."""
    import sys
    import argparse
    import json

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    parser = argparse.ArgumentParser(
        description='Generate synthetic Kantar survey data',
        epilog="""
Examples:
  # Generate from existing study
  python -m src.kantar.survey_runner --study 61405445-01 --market US --num-respondents 50

  # Generate from custom concepts (no ground truth needed)
  python -m src.kantar.survey_runner --concepts-file concepts.json --num-respondents 100 --market-profile US_gaming

  # List available market profiles
  python -m src.kantar.survey_runner --list-profiles
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--study', help='Study ID (e.g., 61405445-01) for ground truth mode')
    mode_group.add_argument('--concepts-file', help='JSON file with concept definitions (no ground truth mode)')
    mode_group.add_argument('--list-profiles', action='store_true', help='List available market profiles and exit')

    # Study mode arguments
    parser.add_argument('--market', help='Market code (e.g., US) - required for study mode')
    parser.add_argument('--all-markets', action='store_true', help='Generate for all markets in study')
    parser.add_argument('--use-gt-demographics', action='store_true',
                       help='Sample demographics from ground truth data')

    # Concepts mode arguments
    parser.add_argument('--market-profile', default='generic',
                       help='Market profile for demographics (default: generic). Options: US_gaming, UK_lottery, EU_general, generic')
    parser.add_argument('--output-name', help='Output file name prefix (default: synthetic_concepts)')

    # Common arguments
    parser.add_argument('--num-respondents', type=int, help='Number of respondents')
    parser.add_argument('--model', default='gpt-4o-mini', help='LLM model (default: gpt-4o-mini)')
    parser.add_argument('--output-dir', help='Output directory')

    args = parser.parse_args()

    # Handle --list-profiles
    if args.list_profiles:
        print("\n=== Available Market Profiles ===\n")
        profiles = list_market_profiles()
        for name, description in profiles.items():
            print(f"{name}:")
            print(f"  {description}\n")
        sys.exit(0)

    runner = KantarSurveyRunner(model=args.model)

    # Concepts mode (no ground truth)
    if args.concepts_file:
        if not args.num_respondents:
            print("Error: --num-respondents required for concepts mode")
            sys.exit(1)

        # Load concepts from JSON file
        concepts_path = Path(args.concepts_file)
        if not concepts_path.exists():
            print(f"Error: Concepts file not found: {concepts_path}")
            sys.exit(1)

        with open(concepts_path) as f:
            concepts = json.load(f)

        if not isinstance(concepts, list):
            print("Error: Concepts file must contain a JSON array of concept objects")
            sys.exit(1)

        print(f"\nLoaded {len(concepts)} concepts from {concepts_path}")

        output_file = runner.generate_from_concepts(
            concepts=concepts,
            num_respondents=args.num_respondents,
            output_dir=Path(args.output_dir) if args.output_dir else None,
            output_name=args.output_name,
            market_profile=args.market_profile
        )
        print(f"\n✓ Generated: {output_file}")

    # Study mode (with ground truth)
    elif args.study:
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
                output_dir=Path(args.output_dir) if args.output_dir else None,
                use_ground_truth_demographics=args.use_gt_demographics
            )
            print(f"\n✓ Generated: {output_file}")
        else:
            print("Error: Must specify either --market or --all-markets with --study")
            sys.exit(1)

    else:
        print("Error: Must specify either --study (ground truth mode) or --concepts-file (no ground truth mode)")
        print("Use --help for usage information or --list-profiles to see available market profiles")
        sys.exit(1)


if __name__ == "__main__":
    main()
