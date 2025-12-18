#!/usr/bin/env python3
"""
Run Full Synthetic Survey Pipeline

This script runs the complete pipeline from start to finish.
"""

import sys
import argparse
from pathlib import Path
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

from src.persona.generator import PersonaGenerator
from src.llm.client import LLMClient
from src.ssr.embeddings import EmbeddingService
from src.ssr.rating_engine import RatingEngine
from src.scales.registry import create_default_scales
from src.survey.question_handler import QuestionHandler
from src.survey.survey_engine import SurveyEngine
from src.output.excel_formatter import ExcelFormatter
from src.logic.conditional_logic import create_standard_survey_logic


def main():
    parser = argparse.ArgumentParser(description='Run synthetic survey generation pipeline')
    parser.add_argument('-n', '--respondents', type=int, default=50,
                       help='Number of respondents to generate (default: 50)')
    parser.add_argument('-c', '--concepts', type=str,
                       help='Path to concepts JSON file')
    parser.add_argument('-o', '--output', type=str,
                       help='Output file path (default: auto-generated)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed (default: 42)')
    parser.add_argument('--questions', type=str, nargs='+',
                       help='Specific questions to ask (default: all)')
    parser.add_argument('--concepts-per-resp', type=int, default=3,
                       help='Number of concepts per respondent (default: 3)')
    parser.add_argument('--model', type=str, default='gpt-4o-mini',
                       help='LLM model to use (default: gpt-4o-mini)')
    parser.add_argument('--parallel', type=int, default=5,
                       help='Number of parallel workers (default: 5)')

    args = parser.parse_args()

    print("="*80)
    print("SYNTHETIC SURVEY RESPONDENT SYSTEM")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  Respondents: {args.respondents}")
    print(f"  Concepts per Respondent: {args.concepts_per_resp}")
    print(f"  Random Seed: {args.seed}")
    print(f"  Model: {args.model}")
    print(f"  Parallel Workers: {args.parallel}")
    print(f"  Questions: {args.questions if args.questions else 'All'}")

    # Load concepts
    if args.concepts:
        concepts_file = Path(args.concepts)
    else:
        concepts_file = Path('data/parsed/concepts.json')

    if not concepts_file.exists():
        print(f"\n❌ ERROR: Concepts file not found: {concepts_file}")
        print("   Run notebook 01 first to parse concepts, or provide --concepts path")
        return 1

    with open(concepts_file, 'r') as f:
        concepts = json.load(f)
    print(f"  Concepts: {len(concepts)}")

    # Initialize components
    print("\n" + "="*80)
    print("Initializing Components")
    print("="*80)

    persona_generator = PersonaGenerator(random_seed=args.seed)
    print("  ✓ Persona generator")

    llm_client = LLMClient(model=args.model, temperature=0.5)
    print(f"  ✓ LLM client ({args.model})")

    embedding_service = EmbeddingService(model_id="text-embedding-3-small")
    print("  ✓ Embedding service")

    scale_registry = create_default_scales()
    print(f"  ✓ Scale registry ({len(scale_registry.scales)} scales)")

    rating_engine = RatingEngine(scale_registry, embedding_service)
    print("  ✓ Rating engine")

    # Preload anchors
    print("\n  Preloading anchor embeddings...")
    rating_engine.preload_scales()
    print("  ✓ Anchors preloaded")

    question_handler = QuestionHandler(llm_client, rating_engine)
    print("  ✓ Question handler")

    survey_logic = create_standard_survey_logic()
    print("  ✓ Survey logic")

    survey_engine = SurveyEngine(
        question_handler=question_handler,
        survey_logic=survey_logic,
        concepts=concepts
    )
    print("  ✓ Survey engine")

    # Run survey
    print("\n" + "="*80)
    print("Generating Synthetic Data")
    print("="*80)
    print(f"\nGenerating responses for {args.respondents} respondents...")
    print("This may take several minutes...\n")

    respondent_data_list = survey_engine.run_full_study(
        n_respondents=args.respondents,
        persona_generator=persona_generator,
        concepts=concepts,
        questions_to_ask=args.questions,
        randomize_concepts=True,
        num_concepts_per_respondent=args.concepts_per_resp,
        show_progress=True,
        max_workers=args.parallel
    )

    valid = [r for r in respondent_data_list if not r.metadata.get('screened_out')]
    screened = [r for r in respondent_data_list if r.metadata.get('screened_out')]

    print(f"\n✓ Generated data:")
    print(f"  Valid: {len(valid)}")
    print(f"  Screened: {len(screened)}")

    # Export
    print("\n" + "="*80)
    print("Exporting to Excel")
    print("="*80)

    if args.output:
        output_file = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path('data/synthetic')
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f'synthetic_data_{args.respondents}resp_{timestamp}.xlsx'

    formatter = ExcelFormatter()
    df = formatter.format_and_save(
        respondent_data_list=respondent_data_list,
        output_path=str(output_file)
    )

    print(f"\n✓ Saved: {output_file}")
    print(f"  Rows: {len(df)}")
    print(f"  Columns: {len(df.columns)}")

    # Save metadata
    metadata = {
        'generation_timestamp': datetime.now().isoformat(),
        'n_respondents': args.respondents,
        'n_concepts': len(concepts),
        'concepts_per_respondent': args.concepts_per_resp,
        'questions_asked': args.questions or 'all',
        'random_seed': args.seed,
        'valid_respondents': len(valid),
        'screened_respondents': len(screened),
        'output_file': str(output_file),
        'models': {
            'llm': args.model,
            'embedding': 'text-embedding-3-small',
            'temperature': 0.5
        },
        'parallel_workers': args.parallel
    }

    metadata_file = output_file.parent / f'metadata_{output_file.stem}.json'
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"✓ Saved metadata: {metadata_file}")

    print("\n" + "="*80)
    print("COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("  1. Run notebook 07 to validate against ground truth")
    print("  2. Review validation metrics")
    print("  3. Adjust and re-run if needed")

    return 0


if __name__ == '__main__':
    sys.exit(main())
