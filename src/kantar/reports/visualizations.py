"""Visualization generator for validation reports."""

from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class VisualizationGenerator:
    """Generates visualization plots for validation reports."""

    def __init__(self, report, output_dir: Path):
        self.report = report
        self.output_dir = Path(output_dir) / "plots"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(self) -> dict:
        """Generate all visualization plots. Returns dict of plot names to paths."""
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import seaborn as sns
            import pandas as pd
            import numpy as np
        except ImportError:
            logger.warning("matplotlib/seaborn not installed, skipping plots")
            return {}

        plots = {}

        # Metrics dashboard
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
            fig.suptitle(f'Validation Metrics - {self.report.study_id} {self.report.market}', fontsize=16)

            # KL Divergence distribution
            kl_values = [q['kl_divergence'] for q in self.report.question_metrics if q.get('kl_divergence')]
            if kl_values:
                ax1.hist(kl_values, bins=20, color='steelblue', edgecolor='black')
                ax1.axvline(0.20, color='red', linestyle='--', label='Threshold (0.20)')
                ax1.set_title('KL Divergence Distribution')
                ax1.set_xlabel('KL Divergence')
                ax1.set_ylabel('Frequency')
                ax1.legend()

            # KS Statistics
            ks_values = [q['ks_statistic'] for q in self.report.question_metrics if q.get('ks_statistic')]
            if ks_values:
                ax2.hist(ks_values, bins=20, color='coral', edgecolor='black')
                ax2.set_title('KS Statistic Distribution')
                ax2.set_xlabel('KS Statistic')
                ax2.set_ylabel('Frequency')

            # Correlation scatter
            corr_values = [q['correlation'] for q in self.report.question_metrics if q.get('correlation')]
            if corr_values:
                ax3.scatter(range(len(corr_values)), corr_values, alpha=0.6)
                ax3.axhline(0.85, color='red', linestyle='--', label='Threshold (0.85)')
                ax3.set_title('Question Correlations')
                ax3.set_xlabel('Question Index')
                ax3.set_ylabel('Correlation')
                ax3.legend()

            # Summary metrics
            agg = self.report.aggregate_metrics
            metric_names = ['Mean KL', 'KS Similarity', 'Mean Corr']
            metric_values = [
                agg.get('mean_kl_divergence', 0),
                agg.get('ks_similarity', 0),
                agg.get('mean_correlation', 0) if agg.get('mean_correlation') else 0
            ]
            ax4.bar(metric_names, metric_values, color=['steelblue', 'coral', 'green'])
            ax4.set_title('Aggregate Metrics')
            ax4.set_ylabel('Value')
            ax4.set_ylim(0, 1)

            plt.tight_layout()
            dashboard_path = self.output_dir / 'metrics_dashboard.png'
            plt.savefig(dashboard_path, dpi=150, bbox_inches='tight')
            plt.close()
            plots['metrics_dashboard'] = dashboard_path

        except Exception as e:
            logger.warning(f"Could not generate dashboard: {e}")

        return plots
