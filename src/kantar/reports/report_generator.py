"""
Report Generator for Kantar Validation Results.

Loads validation JSON and generates formatted reports with metrics,
visualizations, and executive summaries.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ValidationReport:
    """Container for validation report data."""

    def __init__(self, validation_data: Dict[str, Any]):
        """
        Initialize report from validation JSON data.

        Args:
            validation_data: Parsed validation JSON dictionary
        """
        self.data = validation_data
        self.study_id = validation_data.get('study_id', 'Unknown')
        self.market = validation_data.get('market', 'Unknown')
        self.timestamp = validation_data.get('timestamp', datetime.now().isoformat())

        # Extract metrics
        self.respondent_counts = validation_data.get('respondent_counts', {})
        self.column_counts = validation_data.get('column_counts', {})
        self.question_metrics = validation_data.get('question_metrics', [])
        self.aggregate_metrics = validation_data.get('aggregate_metrics', {})
        self.success_criteria = validation_data.get('success_criteria', {})

    @classmethod
    def from_file(cls, json_path: Path) -> 'ValidationReport':
        """
        Load report from JSON file.

        Args:
            json_path: Path to validation JSON file

        Returns:
            ValidationReport instance
        """
        with open(json_path, 'r') as f:
            data = json.load(f)
        return cls(data)

    def get_overall_status(self) -> str:
        """
        Get overall validation status.

        Returns:
            'PASS', 'FAIL', or 'WARNING'
        """
        if not self.success_criteria:
            return 'UNKNOWN'

        criteria = self.success_criteria

        # All criteria must pass for PASS status
        if all(criteria.values()):
            return 'PASS'

        # If most criteria pass, it's a WARNING
        pass_count = sum(1 for v in criteria.values() if v)
        if pass_count >= len(criteria) / 2:
            return 'WARNING'

        return 'FAIL'

    def get_quality_score(self) -> float:
        """
        Calculate overall quality score (0-100).

        Returns:
            Quality score percentage
        """
        agg = self.aggregate_metrics

        if not agg:
            return 0.0

        # Weighted scoring
        scores = []

        # KL divergence (lower is better, threshold 0.20)
        if 'mean_kl_divergence' in agg and agg['mean_kl_divergence'] is not None:
            kl_score = max(0, 100 * (1 - agg['mean_kl_divergence'] / 0.20))
            scores.append(kl_score)

        # KS similarity (higher is better, threshold 0.85)
        if 'ks_similarity' in agg and agg['ks_similarity'] is not None:
            ks_score = 100 * (agg['ks_similarity'] / 0.85)
            scores.append(ks_score)

        # Correlation (higher is better, threshold 0.85)
        if 'mean_correlation' in agg and agg['mean_correlation'] is not None:
            corr_score = 100 * (agg['mean_correlation'] / 0.85)
            scores.append(corr_score)

        if not scores:
            return 0.0

        # Average of all scores, capped at 100
        return min(100.0, sum(scores) / len(scores))

    def get_top_issues(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Get top N questions with worst metrics.

        Args:
            top_n: Number of issues to return

        Returns:
            List of question metrics sorted by worst KL divergence
        """
        # Sort by KL divergence (higher is worse)
        sorted_questions = sorted(
            [q for q in self.question_metrics if q.get('kl_divergence') is not None],
            key=lambda x: x['kl_divergence'],
            reverse=True
        )

        return sorted_questions[:top_n]

    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Get summary statistics for the report.

        Returns:
            Dictionary of summary statistics
        """
        return {
            'study_id': self.study_id,
            'market': self.market,
            'timestamp': self.timestamp,
            'gt_respondents': self.respondent_counts.get('ground_truth', 0),
            'syn_respondents': self.respondent_counts.get('synthetic', 0),
            'questions_validated': len(self.question_metrics),
            'overall_status': self.get_overall_status(),
            'quality_score': round(self.get_quality_score(), 1),
            'mean_kl': round(self.aggregate_metrics.get('mean_kl_divergence', 0), 3),
            'ks_similarity': round(self.aggregate_metrics.get('ks_similarity', 0), 3),
            'mean_correlation': round(self.aggregate_metrics.get('mean_correlation', 0), 3) if self.aggregate_metrics.get('mean_correlation') else None
        }


class ReportGenerator:
    """Generator for validation reports."""

    def __init__(self, validation_json: Path):
        """
        Initialize report generator.

        Args:
            validation_json: Path to validation JSON file
        """
        self.validation_json = Path(validation_json)
        self.report = ValidationReport.from_file(self.validation_json)
        self.output_dir = self.validation_json.parent

    def generate_all(self, output_dir: Optional[Path] = None,
                    include_plots: bool = True) -> Dict[str, Path]:
        """
        Generate all report formats.

        Args:
            output_dir: Output directory (default: same as validation JSON)
            include_plots: Whether to generate visualization plots

        Returns:
            Dictionary mapping report type to output path
        """
        if output_dir:
            self.output_dir = Path(output_dir)

        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Generating reports for {self.report.study_id} - {self.report.market}")

        outputs = {}

        # Generate HTML report (main report)
        from .html_report import HTMLReportGenerator
        html_gen = HTMLReportGenerator(self.report, self.output_dir)
        html_path = html_gen.generate(include_plots=include_plots)
        outputs['html'] = html_path
        logger.info(f"Generated HTML report: {html_path}")

        return outputs
