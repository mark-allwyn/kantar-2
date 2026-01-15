#!/usr/bin/env python3
"""
Generate fresh 50-respondent runs for all 4 studies.

This script generates complete synthetic datasets with all questions populated.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.kantar.survey_runner import KantarSurveyRunner

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Generate 50-respondent runs for all studies."""

    studies = [
        ("61405445-01", "iGaming Concept Evaluate"),
        ("61407017", "24 Ideas Screening"),
        ("61407069", "Tech-Enabled ScratchCards"),
        ("61407185", "Innovation Concepts 2025")
    ]

    runner = KantarSurveyRunner(model="gpt-4o-mini")

    results = {}

    for study_id, study_name in studies:
        logger.info(f"\n{'='*70}")
        logger.info(f"GENERATING: {study_id} - {study_name}")
        logger.info(f"{'='*70}\n")

        try:
            output_path = runner.generate_for_market(
                study_id=study_id,
                market_code="US",
                num_respondents=50,
                use_ground_truth_demographics=True  # Use actual demographics from ground truth
            )

            results[study_id] = {
                "status": "success",
                "output": str(output_path)
            }

            logger.info(f"\n✅ SUCCESS: {study_id}")
            logger.info(f"   Output: {output_path}")

        except Exception as e:
            logger.error(f"\n❌ FAILED: {study_id}")
            logger.error(f"   Error: {e}", exc_info=True)
            results[study_id] = {
                "status": "failed",
                "error": str(e)
            }

    # Final summary
    logger.info(f"\n{'='*70}")
    logger.info("GENERATION SUMMARY")
    logger.info(f"{'='*70}\n")

    successful = [sid for sid, r in results.items() if r["status"] == "success"]
    failed = [sid for sid, r in results.items() if r["status"] == "failed"]

    logger.info(f"Successful: {len(successful)}/{len(studies)} studies")
    logger.info(f"Failed: {len(failed)}/{len(studies)} studies")

    if successful:
        logger.info("\n✅ Successfully generated:")
        for study_id in successful:
            logger.info(f"   {study_id}: {results[study_id]['output']}")

    if failed:
        logger.info("\n❌ Failed:")
        for study_id in failed:
            logger.info(f"   {study_id}: {results[study_id]['error']}")

    logger.info(f"\n{'='*70}")
    logger.info("Next steps:")
    logger.info("1. Run validation: python scripts/validate_latest_runs.py")
    logger.info("2. Generate report: python scripts/generate_validation_presentation.py")
    logger.info(f"{'='*70}\n")

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
