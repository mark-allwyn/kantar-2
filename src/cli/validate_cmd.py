"""
Validate subcommands for kantar-synthetic CLI.
"""

import click
import sys
from pathlib import Path


@click.group()
def validate():
    """Validate synthetic data against ground truth."""
    pass


@validate.command(name="study")
@click.argument("study_id")
@click.argument("market")
@click.option("--synthetic", type=click.Path(exists=True),
              help="Path to synthetic Excel file (auto-detect if omitted)")
@click.option("--ground-truth", type=click.Path(exists=True),
              help="Path to ground truth Excel file (auto-discover if omitted)")
@click.option("--report", is_flag=True, help="Generate HTML validation report")
@click.option("--report-format", type=click.Choice(["html", "json"]), default="html",
              help="Report format (default: html)")
@click.option("--output-dir", type=click.Path(), help="Custom output directory for reports")
def validate_study(study_id, market, synthetic, ground_truth, report, report_format, output_dir):
    """
    Validate synthetic data against ground truth for a Kantar study.

    If --synthetic is not provided, uses the most recent synthetic file.
    If --ground-truth is not provided, auto-discovers from study catalog.

    Examples:
        kantar-synthetic validate study 61405445-01 US
        kantar-synthetic validate study 61407017 UK --report
        kantar-synthetic validate study 61405445-01 US --synthetic path/to/file.xlsx
    """
    from src.kantar.validation_runner import KantarValidationRunner

    click.echo(f"Validating: {study_id} - {market}")

    # Auto-detect synthetic file if not provided
    if not synthetic:
        click.echo("Auto-detecting latest synthetic file...")
        synthetic_dir = Path("data/synthetic/kantar") / study_id / market

        if not synthetic_dir.exists():
            click.secho(f"✗ No synthetic data directory found: {synthetic_dir}", fg="red")
            sys.exit(1)

        synthetic_files = list(synthetic_dir.glob("synthetic_*.xlsx"))
        if not synthetic_files:
            click.secho(f"✗ No synthetic Excel files found in {synthetic_dir}", fg="red")
            sys.exit(1)

        synthetic = max(synthetic_files, key=lambda p: p.stat().st_mtime)
        click.echo(f"  Found: {synthetic.name}")

    try:
        runner = KantarValidationRunner()

        click.echo("\nRunning validation...")

        results = runner.validate_market(
            study_id=study_id,
            market_code=market,
            synthetic_path=Path(synthetic),
            ground_truth_path=Path(ground_truth) if ground_truth else None
        )

        # Display results
        click.secho(f"\n✓ VALIDATION COMPLETE", fg="green", bold=True)

        if 'aggregate_metrics' in results:
            agg = results['aggregate_metrics']

            click.echo(f"\nAggregate Metrics:")
            click.echo(f"  Mean KL Divergence:  {agg['mean_kl_divergence']:.4f} (target: <0.20)")
            click.echo(f"  KS Similarity:       {agg['ks_similarity']:.4f} (target: >0.85)")

            if agg.get('mean_correlation'):
                click.echo(f"  Mean Correlation:    {agg['mean_correlation']:.4f} (target: >0.85)")

            click.echo(f"  Questions Validated: {agg['questions_validated']}")

        # Success criteria
        if 'success_criteria' in results:
            criteria = results['success_criteria']
            click.echo(f"\nSuccess Criteria:")

            for key, value in criteria.items():
                status = "✓" if value else "✗"
                color = "green" if value else "red"
                label = key.replace("_", " ").title()
                click.secho(f"  {status} {label}", fg=color)

        # Save location
        if 'validation_file' in results:
            click.echo(f"\nValidation results saved to:")
            click.echo(f"  {results['validation_file']}")

        if report:
            click.echo(f"\nGenerating {report_format.upper()} report...")
            # TODO: Implement report generation
            click.echo("  Report generation not yet implemented")

    except Exception as e:
        click.secho(f"\n✗ VALIDATION FAILED", fg="red", bold=True)
        click.echo(f"Error: {str(e)}")
        sys.exit(1)
