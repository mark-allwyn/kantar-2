"""
Validation runner for Kantar synthetic data.

Runs validation metrics against ground truth and generates reports.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, List
import logging
import json
from datetime import datetime

from ..validation.metrics import ValidationMetrics
from .study_catalog import StudyCatalog
from .data_loader import GroundTruthLoader

logger = logging.getLogger(__name__)


class KantarValidationRunner:
    """
    Validation runner for Kantar markets and studies.

    Calculates validation metrics and generates reports comparing
    synthetic data to ground truth.
    """

    def __init__(self):
        """Initialize the validation runner."""
        self.catalog = StudyCatalog()
        self.ground_truth_loader = GroundTruthLoader()

    def validate_market(self,
                       study_id: str,
                       market_code: str,
                       synthetic_path: Path,
                       ground_truth_path: Optional[Path] = None) -> Dict:
        """
        Validate synthetic data for a single market.

        Args:
            study_id: Study ID
            market_code: Market code
            synthetic_path: Path to synthetic Excel file
            ground_truth_path: Path to ground truth (None = auto-discover)

        Returns:
            Dictionary with validation metrics

        Raises:
            FileNotFoundError: If files not found
            ValueError: If study/market not found
        """
        logger.info(f"Validating {study_id} - {market_code}")

        # Load ground truth if not provided
        if ground_truth_path is None:
            study = self.catalog.get_study(study_id)
            if not study:
                raise ValueError(f"Study not found: {study_id}")

            market = study.get_market(market_code)
            if not market or not market.excel_files:
                raise ValueError(f"Market not found: {market_code}")

            ground_truth_path = market.excel_files[0]

        # Load data
        logger.info(f"Loading ground truth: {ground_truth_path.name}")
        gt_df = pd.read_excel(ground_truth_path)

        logger.info(f"Loading synthetic: {synthetic_path.name}")
        if not synthetic_path.exists():
            raise FileNotFoundError(f"Synthetic file not found: {synthetic_path}")
        syn_df = pd.read_excel(synthetic_path)

        logger.info(f"Ground truth: {len(gt_df)} rows, {len(gt_df.columns)} columns")
        logger.info(f"Synthetic: {len(syn_df)} rows, {len(syn_df.columns)} columns")

        # Identify question columns (those with parentheses pattern)
        question_cols = [
            col for col in gt_df.columns
            if '(' in col and ')' in col and col in syn_df.columns
        ]
        logger.info(f"Found {len(question_cols)} question columns to validate")

        # NEW: Check categorical alignment (hard fail on mismatch)
        logger.info("Checking categorical alignment...")
        categorical_issues = self._check_categorical_alignment(gt_df, syn_df)
        if categorical_issues:
            error_msg = "CATEGORICAL VALUE MISMATCH DETECTED:\n"
            error_msg += "Synthetic data contains categorical values that don't exist in ground truth.\n\n"
            for field, issues in categorical_issues.items():
                error_msg += f"  {field}:\n"
                error_msg += f"    Invalid values: {issues['invalid_values']}\n"
                error_msg += f"    Valid GT values: {issues['valid_values']}\n\n"
            error_msg += "This indicates demographics generation is not using ground truth schema.\n"
            error_msg += "Check that demographics_schema was properly extracted and passed to PersonaGenerator."
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.info("  Categorical alignment check: PASSED")

        # Run validation metrics
        logger.info("Calculating validation metrics...")

        results = {
            'study_id': study_id,
            'market': market_code,
            'timestamp': datetime.now().isoformat(),
            'ground_truth_file': str(ground_truth_path),
            'synthetic_file': str(synthetic_path),
            'respondent_counts': {
                'ground_truth': len(gt_df),
                'synthetic': len(syn_df)
            },
            'column_counts': {
                'ground_truth': len(gt_df.columns),
                'synthetic': len(syn_df.columns),
                'common': len(set(gt_df.columns) & set(syn_df.columns)),
                'questions': len(question_cols)
            }
        }

        # Calculate metrics for each question
        question_metrics = []
        for i, col in enumerate(question_cols):
            if (i + 1) % 10 == 0:
                logger.info(f"  Progress: {i + 1}/{len(question_cols)} questions")

            try:
                # Get data for this column
                gt_col = gt_df[col].dropna()
                syn_col = syn_df[col].dropna()

                if len(gt_col) == 0 or len(syn_col) == 0:
                    continue

                # Calculate distributions
                gt_counts = gt_col.value_counts(normalize=True).sort_index()
                syn_counts = syn_col.value_counts(normalize=True).sort_index()

                # Align indices
                all_values = sorted(set(gt_counts.index) | set(syn_counts.index))
                gt_dist = np.array([gt_counts.get(v, 0) for v in all_values])
                syn_dist = np.array([syn_counts.get(v, 0) for v in all_values])

                # Calculate KL divergence
                kl = ValidationMetrics.kl_divergence(gt_dist, syn_dist)

                # Calculate KS statistic
                try:
                    ks_stat, ks_pval = ValidationMetrics.ks_statistic(
                        gt_col.values,
                        syn_col.values
                    )
                except:
                    ks_stat = None

                # Calculate correlation (if numeric)
                try:
                    # Try to convert to numeric
                    gt_numeric = pd.to_numeric(gt_col, errors='coerce').dropna()
                    syn_numeric = pd.to_numeric(syn_col, errors='coerce').dropna()
                    if len(gt_numeric) > 0 and len(syn_numeric) > 0:
                        corr = np.corrcoef(gt_numeric, syn_numeric)[0, 1]
                    else:
                        corr = None
                except:
                    corr = None

                question_metrics.append({
                    'column': col,
                    'kl_divergence': kl,
                    'ks_statistic': ks_stat,
                    'correlation': corr,
                    'gt_count': len(gt_col),
                    'syn_count': len(syn_col)
                })

            except Exception as e:
                logger.warning(f"Failed to validate {col}: {e}")
                continue

        results['question_metrics'] = question_metrics

        # Calculate aggregate metrics
        if question_metrics:
            kl_values = [m['kl_divergence'] for m in question_metrics if m['kl_divergence'] is not None]
            ks_values = [m['ks_statistic'] for m in question_metrics if m['ks_statistic'] is not None]
            corr_values = [m['correlation'] for m in question_metrics if m['correlation'] is not None]

            results['aggregate_metrics'] = {
                'mean_kl_divergence': sum(kl_values) / len(kl_values) if kl_values else None,
                'median_kl_divergence': sorted(kl_values)[len(kl_values)//2] if kl_values else None,
                'mean_ks_statistic': sum(ks_values) / len(ks_values) if ks_values else None,
                'ks_similarity': 1 - (sum(ks_values) / len(ks_values)) if ks_values else None,
                'mean_correlation': sum(corr_values) / len(corr_values) if corr_values else None,
                'questions_validated': len(question_metrics)
            }

            # Success criteria
            agg = results['aggregate_metrics']
            results['success_criteria'] = {
                'kl_below_0_20': agg['mean_kl_divergence'] < 0.20 if agg['mean_kl_divergence'] else False,
                'ks_similarity_above_0_85': agg['ks_similarity'] > 0.85 if agg['ks_similarity'] else False,
                'correlation_above_0_85': agg['mean_correlation'] > 0.85 if agg['mean_correlation'] else False
            }

        logger.info(f"Validation complete: {len(question_metrics)} questions validated")
        if results.get('aggregate_metrics'):
            agg = results['aggregate_metrics']
            logger.info(f"  Mean KL: {agg['mean_kl_divergence']:.3f}")
            logger.info(f"  KS Similarity: {agg['ks_similarity']:.3f}")
            if agg['mean_correlation']:
                logger.info(f"  Mean Correlation: {agg['mean_correlation']:.3f}")

        # Save results
        output_dir = synthetic_path.parent
        results_file = output_dir / f"validation_{market_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Add validation file path to results
        results['validation_file'] = str(results_file)

        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Saved validation results to: {results_file}")

        return results

    def validate_study(self,
                      study_id: str,
                      synthetic_dir: Optional[Path] = None) -> Dict:
        """
        Validate all markets in a study.

        Args:
            study_id: Study ID
            synthetic_dir: Directory containing synthetic data (None = auto)

        Returns:
            Dictionary with aggregated validation results
        """
        study = self.catalog.get_study(study_id)
        if not study:
            raise ValueError(f"Study not found: {study_id}")

        logger.info(f"Validating study: {study.study_name}")
        logger.info(f"Markets: {study.complete_markets}")

        if synthetic_dir is None:
            synthetic_dir = Path("data/synthetic/kantar") / study.study_id

        market_results = {}

        for market_code in study.complete_markets:
            logger.info(f"\n{'='*60}")
            logger.info(f"Validating market: {market_code}")
            logger.info(f"{'='*60}\n")

            try:
                # Find synthetic file for this market
                market_dir = synthetic_dir / market_code
                if not market_dir.exists():
                    logger.warning(f"No synthetic data found for {market_code}")
                    continue

                # Find most recent synthetic file
                synthetic_files = list(market_dir.glob("synthetic_*.xlsx"))
                if not synthetic_files:
                    logger.warning(f"No synthetic Excel files found in {market_dir}")
                    continue

                synthetic_file = max(synthetic_files, key=lambda p: p.stat().st_mtime)
                logger.info(f"Using synthetic file: {synthetic_file.name}")

                # Validate
                results = self.validate_market(
                    study_id=study_id,
                    market_code=market_code,
                    synthetic_path=synthetic_file
                )

                market_results[market_code] = results
                logger.info(f"✓ {market_code}: SUCCESS")

            except Exception as e:
                logger.error(f"✗ {market_code}: FAILED - {e}")
                market_results[market_code] = {'error': str(e)}

        # Aggregate results across markets
        logger.info(f"\n{'='*60}")
        logger.info("STUDY VALIDATION SUMMARY")
        logger.info(f"{'='*60}")

        study_results = {
            'study_id': study_id,
            'study_name': study.study_name,
            'timestamp': datetime.now().isoformat(),
            'markets': market_results,
            'summary': {
                'total_markets': len(study.complete_markets),
                'validated': len([r for r in market_results.values() if 'error' not in r]),
                'failed': len([r for r in market_results.values() if 'error' in r])
            }
        }

        # Calculate cross-market aggregates
        valid_results = [r for r in market_results.values() if 'aggregate_metrics' in r]
        if valid_results:
            kl_values = [r['aggregate_metrics']['mean_kl_divergence']
                        for r in valid_results
                        if r['aggregate_metrics'].get('mean_kl_divergence')]
            ks_sim_values = [r['aggregate_metrics']['ks_similarity']
                            for r in valid_results
                            if r['aggregate_metrics'].get('ks_similarity')]
            corr_values = [r['aggregate_metrics']['mean_correlation']
                          for r in valid_results
                          if r['aggregate_metrics'].get('mean_correlation')]

            study_results['cross_market_aggregates'] = {
                'mean_kl_divergence': sum(kl_values) / len(kl_values) if kl_values else None,
                'mean_ks_similarity': sum(ks_sim_values) / len(ks_sim_values) if ks_sim_values else None,
                'mean_correlation': sum(corr_values) / len(corr_values) if corr_values else None
            }

            logger.info(f"\nCross-Market Averages:")
            if kl_values:
                logger.info(f"  Mean KL Divergence: {study_results['cross_market_aggregates']['mean_kl_divergence']:.3f}")
            if ks_sim_values:
                logger.info(f"  Mean KS Similarity: {study_results['cross_market_aggregates']['mean_ks_similarity']:.3f}")
            if corr_values:
                logger.info(f"  Mean Correlation: {study_results['cross_market_aggregates']['mean_correlation']:.3f}")

        # Save study-level results
        output_file = synthetic_dir / f"study_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(study_results, f, indent=2)
        logger.info(f"\nSaved study validation results to: {output_file}")

        return study_results

    def _check_categorical_alignment(self, gt_df: pd.DataFrame, syn_df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Check if synthetic categorical values exist in ground truth.

        Args:
            gt_df: Ground truth DataFrame
            syn_df: Synthetic DataFrame

        Returns:
            Dict of issues: {field: {'invalid_values': [...], 'valid_values': [...]}}
            Empty dict if no issues found
        """
        issues = {}

        # Demographic columns to check
        demo_cols = {
            '(SEX_NONBINARY) SEX': 'Gender',
            '(AGEQUOTA) AGEBANDS': 'Age Bands',
            '(OCCUPATION_SCR) OCCUPATION SCREENER': 'Occupation',
            '(GROUPFMR) SAMPLE TYPE': 'Sample Type',
            '(BRDBUY) BRANDS BOUGHT': 'Brand Buyers'
        }

        for col, display_name in demo_cols.items():
            if col not in gt_df.columns or col not in syn_df.columns:
                continue

            gt_values = set(gt_df[col].dropna().unique())
            syn_values = set(syn_df[col].dropna().unique())

            invalid = syn_values - gt_values
            if invalid:
                issues[display_name] = {
                    'invalid_values': sorted(list(invalid)),
                    'valid_values': sorted(list(gt_values))
                }

        return issues


def main():
    """CLI entry point for testing."""
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    parser = argparse.ArgumentParser(description='Validate Kantar synthetic survey data')
    parser.add_argument('--study', required=True, help='Study ID')
    parser.add_argument('--market', help='Market code (optional, validates all if not specified)')
    parser.add_argument('--synthetic', help='Path to synthetic Excel file')
    parser.add_argument('--ground-truth', help='Path to ground truth Excel file')
    parser.add_argument('--generate-report', action='store_true',
                       help='Generate HTML validation report with visualizations')
    parser.add_argument('--no-plots', action='store_true',
                       help='Skip generating visualization plots (faster)')

    args = parser.parse_args()

    runner = KantarValidationRunner()

    if args.market and args.synthetic:
        # Validate single market
        results = runner.validate_market(
            study_id=args.study,
            market_code=args.market,
            synthetic_path=Path(args.synthetic),
            ground_truth_path=Path(args.ground_truth) if args.ground_truth else None
        )
        print(f"\n✓ Validation complete")
        print(f"  Mean KL: {results['aggregate_metrics']['mean_kl_divergence']:.3f}")
        print(f"  KS Similarity: {results['aggregate_metrics']['ks_similarity']:.3f}")

        # Generate report if requested
        if args.generate_report:
            from .reports import generate_validation_report
            validation_json = Path(results.get('validation_file', ''))
            if validation_json.exists():
                print(f"\n  Generating HTML report...")
                report_outputs = generate_validation_report(
                    validation_json,
                    include_plots=not args.no_plots
                )
                for report_type, report_path in report_outputs.items():
                    print(f"  Generated {report_type} report: {report_path}")
    else:
        # Validate entire study
        results = runner.validate_study(study_id=args.study)
        print(f"\n✓ Study validation complete")
        print(f"  Validated: {results['summary']['validated']}/{results['summary']['total_markets']} markets")


if __name__ == "__main__":
    main()
