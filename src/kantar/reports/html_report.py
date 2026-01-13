"""
HTML Report Generator for Kantar Validation Results.

Creates self-contained HTML reports with embedded CSS and optional visualizations.
"""

from pathlib import Path
from datetime import datetime
import base64
import logging

logger = logging.getLogger(__name__)


class HTMLReportGenerator:
    """Generates HTML validation reports."""

    def __init__(self, report, output_dir: Path):
        """
        Initialize HTML report generator.

        Args:
            report: ValidationReport instance
            output_dir: Output directory for report
        """
        self.report = report
        self.output_dir = Path(output_dir)

    def generate(self, include_plots: bool = True) -> Path:
        """
        Generate HTML report.

        Args:
            include_plots: Whether to include visualization plots

        Returns:
            Path to generated HTML file
        """
        # Generate plots if requested
        plot_paths = {}
        if include_plots:
            try:
                from .visualizations import VisualizationGenerator
                viz_gen = VisualizationGenerator(self.report, self.output_dir)
                plot_paths = viz_gen.generate_all()
                logger.info(f"Generated {len(plot_paths)} visualization plots")
            except Exception as e:
                logger.warning(f"Could not generate plots: {e}")

        # Build HTML
        html_content = self._build_html(plot_paths)

        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"validation_report_{timestamp}.html"

        with open(output_file, 'w') as f:
            f.write(html_content)

        return output_file

    def _build_html(self, plot_paths: dict) -> str:
        """Build complete HTML document."""
        stats = self.report.get_summary_stats()
        status = stats['overall_status']
        status_color = {'PASS': '#28a745', 'WARNING': '#ffc107', 'FAIL': '#dc3545'}.get(status, '#6c757d')

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Validation Report - {self.report.study_id} {self.report.market}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; border-bottom: 2px solid #eee; padding-bottom: 8px; }}
        .status-badge {{ display: inline-block; padding: 8px 16px; border-radius: 4px; color: white; font-weight: bold; background: {status_color}; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric-card {{ background: #f8f9fa; padding: 15px; border-radius: 6px; border-left: 4px solid #007bff; }}
        .metric-label {{ font-size: 12px; color: #666; text-transform: uppercase; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #333; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #007bff; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f8f9fa; }}
        .plot-container {{ margin: 20px 0; text-align: center; }}
        .plot-container img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; }}
        .issue-row {{ background: #fff3cd !important; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Validation Report</h1>
        <p><strong>Study:</strong> {self.report.study_id} | <strong>Market:</strong> {self.report.market}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Status:</strong> <span class="status-badge">{status}</span></p>

        <h2>Summary</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Quality Score</div>
                <div class="metric-value">{stats['quality_score']}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">GT Respondents</div>
                <div class="metric-value">{stats['gt_respondents']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Syn Respondents</div>
                <div class="metric-value">{stats['syn_respondents']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Questions Validated</div>
                <div class="metric-value">{stats['questions_validated']}</div>
            </div>
        </div>

        <h2>Aggregate Metrics</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
                <th>Threshold</th>
                <th>Status</th>
            </tr>
            <tr>
                <td>Mean KL Divergence</td>
                <td>{stats['mean_kl']}</td>
                <td>&lt; 0.20</td>
                <td>{'✓ PASS' if stats['mean_kl'] < 0.20 else '✗ FAIL'}</td>
            </tr>
            <tr>
                <td>KS Similarity</td>
                <td>{stats['ks_similarity']}</td>
                <td>&gt; 0.85</td>
                <td>{'✓ PASS' if stats['ks_similarity'] > 0.85 else '✗ FAIL'}</td>
            </tr>
            <tr>
                <td>Mean Correlation</td>
                <td>{stats['mean_correlation'] if stats['mean_correlation'] else 'N/A'}</td>
                <td>&gt; 0.85</td>
                <td>{'✓ PASS' if stats['mean_correlation'] and stats['mean_correlation'] > 0.85 else ('N/A' if not stats['mean_correlation'] else '✗ FAIL')}</td>
            </tr>
        </table>

        {self._build_top_issues_section()}
        {self._build_plots_section(plot_paths)}
        {self._build_question_details_section()}
    </div>
</body>
</html>"""
        return html

    def _build_top_issues_section(self) -> str:
        """Build top issues section."""
        issues = self.report.get_top_issues(5)
        if not issues:
            return ""

        rows = ""
        for issue in issues:
            kl = issue['kl_divergence']
            ks = issue.get('ks_statistic')
            corr = issue.get('correlation')

            ks_str = f"{ks:.3f}" if ks else 'N/A'
            corr_str = f"{corr:.3f}" if corr else 'N/A'

            rows += f"""
            <tr class="issue-row">
                <td>{issue['column']}</td>
                <td>{kl:.3f}</td>
                <td>{ks_str}</td>
                <td>{corr_str}</td>
            </tr>"""

        return f"""
        <h2>Top Issues</h2>
        <p>Questions with highest KL divergence (requiring attention):</p>
        <table>
            <tr>
                <th>Question</th>
                <th>KL Divergence</th>
                <th>KS Statistic</th>
                <th>Correlation</th>
            </tr>
            {rows}
        </table>"""

    def _build_plots_section(self, plot_paths: dict) -> str:
        """Build plots section with embedded images."""
        if not plot_paths:
            return ""

        sections = "<h2>Visualizations</h2>"

        for plot_name, plot_path in plot_paths.items():
            if plot_path.exists():
                # Embed image as base64
                with open(plot_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode()

                sections += f"""
                <div class="plot-container">
                    <h3>{plot_name.replace('_', ' ').title()}</h3>
                    <img src="data:image/png;base64,{img_data}" alt="{plot_name}">
                </div>"""

        return sections

    def _build_question_details_section(self) -> str:
        """Build detailed question metrics table."""
        if not self.report.question_metrics:
            return ""

        rows = ""
        for i, q in enumerate(self.report.question_metrics[:20]):  # Limit to first 20
            kl = q.get('kl_divergence')
            ks = q.get('ks_statistic')
            corr = q.get('correlation')

            row_class = 'issue-row' if kl and kl > 0.20 else ''

            kl_str = f"{kl:.3f}" if kl else 'N/A'
            ks_str = f"{ks:.3f}" if ks else 'N/A'
            corr_str = f"{corr:.3f}" if corr else 'N/A'

            rows += f"""
            <tr class="{row_class}">
                <td>{i+1}</td>
                <td>{q['column'][:50]}...</td>
                <td>{kl_str}</td>
                <td>{ks_str}</td>
                <td>{corr_str}</td>
            </tr>"""

        return f"""
        <h2>Question Details</h2>
        <p>Top 20 questions by order:</p>
        <table>
            <tr>
                <th>#</th>
                <th>Question</th>
                <th>KL Div</th>
                <th>KS Stat</th>
                <th>Correlation</th>
            </tr>
            {rows}
        </table>"""
