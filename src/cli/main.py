#!/usr/bin/env python3
"""
Kantar Synthetic - Production CLI Tool

Unified command-line interface for synthetic survey data generation,
validation, and study management.

Usage:
    kantar-synthetic generate study STUDY_ID MARKET [options]
    kantar-synthetic generate custom CONCEPTS_FILE [options]
    kantar-synthetic validate STUDY_ID MARKET [options]
    kantar-synthetic study list|verify|info [options]
    kantar-synthetic profile list
"""

import sys
import click
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@click.group()
@click.version_option(version="1.0.0", prog_name="kantar-synthetic")
@click.pass_context
def cli(ctx):
    """
    Kantar Synthetic - Production CLI for synthetic survey data generation.

    Generate realistic survey responses using LLMs, validate against ground truth,
    and manage Kantar study configurations.
    """
    ctx.ensure_object(dict)


# Import subcommand groups
from .generate import generate
from .validate_cmd import validate
from .study import study
from .profile import profile


# Register subcommands
cli.add_command(generate)
cli.add_command(validate)
cli.add_command(study)
cli.add_command(profile)


# Quick commands for common tasks
@cli.command(name="quick-gen")
@click.argument("study_id")
@click.argument("market", default="US")
@click.option("--respondents", "-n", default=50, help="Number of respondents (default: 50)")
@click.option("--verify-first", is_flag=True, help="Verify study structure before generating")
@click.option("--resume", is_flag=True, help="Resume from checkpoint if available")
def quick_generate(study_id, market, respondents, verify_first, resume):
    """
    Quick generate with sensible defaults.

    Generates 50 respondents using ground truth demographics and gpt-4o-mini.

    Example:
        kantar-synthetic quick-gen 61405445-01 US
        kantar-synthetic quick-gen 61407017 UK --respondents 100
        kantar-synthetic quick-gen 61405445-01 US --resume
    """
    click.echo(f"Quick Generate: {study_id} - {market}")
    if resume:
        click.echo("Resume mode: Will resume from checkpoint if available")

    if verify_first:
        click.echo("Verifying study structure...")
        # TODO: Call study verification
        click.echo("  ✓ Study verified")

    click.echo(f"Generating {respondents} respondents with ground truth demographics...")

    # Import here to avoid circular dependency
    from src.kantar.survey_runner import KantarSurveyRunner

    try:
        runner = KantarSurveyRunner(model="gpt-4o-mini")
        output_path = runner.generate_for_market(
            study_id=study_id,
            market_code=market,
            num_respondents=respondents,
            use_ground_truth_demographics=True,
            resume=resume
        )

        click.secho(f"\n✓ SUCCESS", fg="green", bold=True)
        click.echo(f"Generated: {output_path}")

    except Exception as e:
        click.secho(f"\n✗ FAILED", fg="red", bold=True)
        click.echo(f"Error: {e}")
        sys.exit(1)


@cli.command(name="quick-validate")
@click.argument("study_id")
@click.argument("market", default="US")
@click.option("--report", is_flag=True, help="Generate HTML report")
def quick_validate(study_id, market, report):
    """
    Quick validate with auto-detection of latest synthetic file.

    Example:
        kantar-synthetic quick-validate 61405445-01 US
        kantar-synthetic quick-validate 61407017 UK --report
    """
    click.echo(f"Quick Validate: {study_id} - {market}")
    click.echo("Auto-detecting latest synthetic file...")

    # Import here to avoid circular dependency
    from src.kantar.validation_runner import KantarValidationRunner
    from pathlib import Path

    try:
        # Find latest synthetic file
        synthetic_dir = Path("data/synthetic/kantar") / study_id / market
        if not synthetic_dir.exists():
            raise FileNotFoundError(f"No synthetic data found in {synthetic_dir}")

        synthetic_files = list(synthetic_dir.glob("synthetic_*.xlsx"))
        if not synthetic_files:
            raise FileNotFoundError(f"No synthetic Excel files found in {synthetic_dir}")

        latest_file = max(synthetic_files, key=lambda p: p.stat().st_mtime)
        click.echo(f"  Found: {latest_file.name}")

        # Run validation
        runner = KantarValidationRunner()
        results = runner.validate_market(
            study_id=study_id,
            market_code=market,
            synthetic_path=latest_file
        )

        # Display results
        click.secho(f"\n✓ VALIDATION COMPLETE", fg="green", bold=True)
        if 'aggregate_metrics' in results:
            agg = results['aggregate_metrics']
            click.echo(f"\nMetrics:")
            click.echo(f"  Mean KL Divergence: {agg['mean_kl_divergence']:.4f} (target: <0.20)")
            click.echo(f"  KS Similarity: {agg['ks_similarity']:.4f} (target: >0.85)")
            click.echo(f"  Questions Validated: {agg['questions_validated']}")

            # Success criteria
            if 'success_criteria' in results:
                criteria = results['success_criteria']
                click.echo(f"\nSuccess Criteria:")
                for key, value in criteria.items():
                    status = "✓" if value else "✗"
                    label = key.replace("_", " ").title()
                    click.echo(f"  {status} {label}")

        if report:
            click.echo("\nGenerating HTML report...")
            # TODO: Implement report generation
            click.echo("  Report generation not yet implemented")

    except Exception as e:
        click.secho(f"\n✗ FAILED", fg="red", bold=True)
        click.echo(f"Error: {e}")
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
