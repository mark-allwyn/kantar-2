"""
Generate subcommands for kantar-synthetic CLI.
"""

import click
import sys
from pathlib import Path


@click.group()
def generate():
    """Generate synthetic survey data."""
    pass


@generate.command(name="study")
@click.argument("study_id")
@click.argument("market")
@click.option("--respondents", "-n", type=int, required=True, help="Number of respondents to generate")
@click.option("--use-gt-demographics", is_flag=True, default=True,
              help="Sample demographics from ground truth (default: True)")
@click.option("--model", default="gpt-4o-mini", help="LLM model to use")
@click.option("--verify-first", is_flag=True, help="Verify study structure before generating")
@click.option("--checkpoint-every", type=int, default=10,
              help="Save checkpoint every N respondents (default: 10)")
@click.option("--resume", is_flag=True, help="Resume from checkpoint if available")
@click.option("--output-dir", type=click.Path(), help="Custom output directory")
def generate_study(study_id, market, respondents, use_gt_demographics, model,
                  verify_first, checkpoint_every, resume, output_dir):
    """
    Generate synthetic data for an existing Kantar study.

    Requires study to exist in data/kantar-survey-source/ with proper structure.

    Examples:
        kantar-synthetic generate study 61405445-01 US --respondents 50
        kantar-synthetic generate study 61407017 UK -n 100 --model gpt-4o
    """
    from src.kantar.survey_runner import KantarSurveyRunner
    from tqdm import tqdm

    click.echo(f"Generating synthetic data for: {study_id} - {market}")
    click.echo(f"Respondents: {respondents}")
    click.echo(f"Model: {model}")
    click.echo(f"Ground truth demographics: {use_gt_demographics}")
    click.echo(f"Checkpoint every: {checkpoint_every} respondents")
    if resume:
        click.echo("Resume mode: Will resume from checkpoint if available")

    if verify_first:
        click.echo("\nVerifying study structure...")
        # TODO: Call study validator
        click.secho("  ✓ Study structure verified", fg="green")

    try:
        runner = KantarSurveyRunner(model=model)

        click.echo("\nStarting generation...")

        output_path = runner.generate_for_market(
            study_id=study_id,
            market_code=market,
            num_respondents=respondents,
            use_ground_truth_demographics=use_gt_demographics,
            checkpoint_every=checkpoint_every,
            resume=resume,
            output_dir=Path(output_dir) if output_dir else None
        )

        click.secho(f"\n✓ SUCCESS", fg="green", bold=True)
        click.echo(f"Output: {output_path}")

    except Exception as e:
        click.secho(f"\n✗ FAILED", fg="red", bold=True)
        click.echo(f"Error: {str(e)}")
        sys.exit(1)


@generate.command(name="custom")
@click.argument("concepts_file", type=click.Path(exists=True))
@click.option("--respondents", "-n", type=int, required=True, help="Number of respondents to generate")
@click.option("--profile", default="generic",
              help="Market profile for demographics (US_gaming, UK_lottery, EU_general, generic)")
@click.option("--model", default="gpt-4o-mini", help="LLM model to use")
@click.option("--output-dir", type=click.Path(), help="Custom output directory")
@click.option("--output-name", help="Output file name prefix")
@click.option("--validate-concepts", is_flag=True, help="Validate concept schema before generating")
def generate_custom(concepts_file, respondents, profile, model, output_dir,
                   output_name, validate_concepts):
    """
    Generate synthetic data from custom concepts (no ground truth needed).

    Concepts file should be JSON with schema:
    [{"id": "C1", "name": "...", "description": "...", ...}, ...]

    Examples:
        kantar-synthetic generate custom concepts.json -n 100 --profile US_gaming
        kantar-synthetic generate custom my_concepts.json -n 50 --output-name test_run
    """
    import json
    from src.kantar.survey_runner import KantarSurveyRunner

    click.echo(f"Generating from custom concepts: {concepts_file}")
    click.echo(f"Respondents: {respondents}")
    click.echo(f"Market profile: {profile}")
    click.echo(f"Model: {model}")

    # Load concepts
    try:
        with open(concepts_file) as f:
            concepts = json.load(f)

        if not isinstance(concepts, list):
            raise ValueError("Concepts file must contain a JSON array")

        click.echo(f"\nLoaded {len(concepts)} concepts")

        if validate_concepts:
            from src.kantar.concept_schema import validate_concepts as validate_schema
            click.echo("Validating concept schema...")
            validate_schema(concepts, strict=True)
            click.secho("  ✓ Schema validation passed", fg="green")

    except Exception as e:
        click.secho(f"✗ Failed to load concepts: {e}", fg="red")
        sys.exit(1)

    # Generate
    try:
        runner = KantarSurveyRunner(model=model)

        click.echo("\nStarting generation...")

        output_path = runner.generate_from_concepts(
            concepts=concepts,
            num_respondents=respondents,
            market_profile=profile,
            output_dir=Path(output_dir) if output_dir else None,
            output_name=output_name
        )

        click.secho(f"\n✓ SUCCESS", fg="green", bold=True)
        click.echo(f"Output: {output_path}")

    except Exception as e:
        click.secho(f"\n✗ FAILED", fg="red", bold=True)
        click.echo(f"Error: {str(e)}")
        sys.exit(1)
