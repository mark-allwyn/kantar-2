"""
Reporting module for Kantar survey validation.

Generates individual market reports, study-level aggregated reports,
and interactive dashboards for exploring validation results.
"""

from .report_generator import ReportGenerator, ValidationReport
from .html_report import HTMLReportGenerator
from .visualizations import VisualizationGenerator

__all__ = [
    'ReportGenerator',
    'ValidationReport',
    'HTMLReportGenerator',
    'VisualizationGenerator',
    'generate_validation_report'
]


def generate_validation_report(validation_json, output_dir=None, include_plots=True):
    """
    Generate validation report from JSON file.

    Args:
        validation_json: Path to validation JSON file
        output_dir: Output directory (default: same as JSON file)
        include_plots: Whether to generate visualization plots

    Returns:
        Dictionary mapping report type to output path
    """
    generator = ReportGenerator(validation_json)
    return generator.generate_all(output_dir=output_dir, include_plots=include_plots)
