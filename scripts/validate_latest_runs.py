#!/usr/bin/env python3
"""
Validate the latest synthetic runs for all studies.

Runs validation comparing synthetic data to ground truth
for the most recent synthetic Excel files in each study.
"""

import sys
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.kantar.validation_runner import KantarValidationRunner

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Validate latest runs for all 4 studies."""

    studies = [
        "61405445-01",  # iGaming Concept Evaluate
        "61407017",     # 24 Ideas Screening
        "61407069",     # Tech-Enabled ScratchCards
        "61407185"      # Innovation Concepts 2025
    ]

    runner = KantarValidationRunner()

    results = {}

    for study_id in studies:
        logger.info(f"\n{'='*70}")
        logger.info(f"VALIDATING STUDY: {study_id}")
        logger.info(f"{'='*70}\n")

        try:
            # Find latest synthetic file
            synthetic_dir = Path("data/synthetic/kantar") / study_id / "US"

            if not synthetic_dir.exists():
                logger.warning(f"Directory not found: {synthetic_dir}")
                continue

            synthetic_files = list(synthetic_dir.glob("synthetic_*.xlsx"))
            if not synthetic_files:
                logger.warning(f"No synthetic files found in {synthetic_dir}")
                continue

            # Get the most recent file
            latest_file = max(synthetic_files, key=lambda p: p.stat().st_mtime)
            logger.info(f"Using latest file: {latest_file.name}")

            # Run validation
            result = runner.validate_market(
                study_id=study_id,
                market_code="US",
                synthetic_path=latest_file
            )

            results[study_id] = result

            # Print summary
            if 'aggregate_metrics' in result:
                agg = result['aggregate_metrics']
                logger.info(f"\n✅ VALIDATION COMPLETE for {study_id}")
                logger.info(f"   Mean KL Divergence: {agg['mean_kl_divergence']:.4f}")
                logger.info(f"   KS Similarity: {agg['ks_similarity']:.4f}")
                if agg.get('mean_correlation'):
                    logger.info(f"   Mean Correlation: {agg['mean_correlation']:.4f}")
                logger.info(f"   Questions Validated: {agg['questions_validated']}")

                # Success criteria
                if 'success_criteria' in result:
                    criteria = result['success_criteria']
                    logger.info(f"\n   Success Criteria:")
                    logger.info(f"   - KL < 0.20: {'✅' if criteria['kl_below_0_20'] else '❌'}")
                    logger.info(f"   - KS Sim > 0.85: {'✅' if criteria['ks_similarity_above_0_85'] else '❌'}")

        except Exception as e:
            logger.error(f"❌ FAILED to validate {study_id}: {e}", exc_info=True)
            results[study_id] = {"error": str(e)}

    # Final summary
    logger.info(f"\n{'='*70}")
    logger.info("VALIDATION SUMMARY")
    logger.info(f"{'='*70}\n")

    successful = [sid for sid, r in results.items() if 'aggregate_metrics' in r]
    failed = [sid for sid, r in results.items() if 'error' in r]

    logger.info(f"Successful: {len(successful)}/{len(studies)} studies")
    logger.info(f"Failed: {len(failed)}/{len(studies)} studies")

    if successful:
        logger.info("\n✅ Successfully validated:")
        for study_id in successful:
            agg = results[study_id]['aggregate_metrics']
            logger.info(f"   {study_id}: KL={agg['mean_kl_divergence']:.4f}, KS Sim={agg['ks_similarity']:.4f}")

    if failed:
        logger.info("\n❌ Failed:")
        for study_id in failed:
            logger.info(f"   {study_id}: {results[study_id]['error']}")

    logger.info(f"\n✅ Validation JSON files saved to: data/synthetic/kantar/*/US/")
    logger.info("You can now run statistical analysis and generate reports.")

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
