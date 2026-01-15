"""
Study management subcommands for kantar-synthetic CLI.
"""

import click
import sys
from pathlib import Path
from tabulate import tabulate


@click.group()
def study():
    """Manage Kantar studies."""
    pass


@study.command(name="list")
@click.option("--format", "output_format", type=click.Choice(["table", "json", "simple"]),
              default="table", help="Output format")
@click.option("--complete-only", is_flag=True, help="Show only complete studies")
def list_studies(output_format, complete_only):
    """
    List all discovered Kantar studies.

    Shows study ID, name, markets, and completion status.

    Examples:
        kantar-synthetic study list
        kantar-synthetic study list --complete-only
        kantar-synthetic study list --format json
    """
    from src.kantar.study_catalog import StudyCatalog

    try:
        catalog = StudyCatalog()
        study_ids = catalog.list_studies()  # Returns list of study ID strings

        if not study_ids:
            click.echo("No studies found")
            return

        # Get full study objects
        studies = []
        for study_id in study_ids:
            study = catalog.get_study(study_id)
            if study:
                studies.append(study)

        if complete_only:
            studies = [s for s in studies if s.complete_markets]

        if not studies:
            click.echo("No complete studies found")
            return

        if output_format == "json":
            import json
            study_data = [
                {
                    "study_id": s.study_id,
                    "name": s.study_name,
                    "markets": list(s.markets.keys()),
                    "complete_markets": s.complete_markets
                }
                for s in studies
            ]
            click.echo(json.dumps(study_data, indent=2))

        elif output_format == "simple":
            for s in studies:
                markets_str = ", ".join(s.complete_markets) if s.complete_markets else "none"
                click.echo(f"{s.study_id}: {s.study_name} ({markets_str})")

        else:  # table format
            table_data = []
            for s in studies:
                markets_str = ", ".join(sorted(s.complete_markets)) if s.complete_markets else "-"
                total_markets = len(s.markets)
                complete_count = len(s.complete_markets)
                status = "✓" if complete_count > 0 else "✗"

                table_data.append([
                    status,
                    s.study_id,
                    s.study_name[:40],  # Truncate long names
                    f"{complete_count}/{total_markets}",
                    markets_str
                ])

            headers = ["", "Study ID", "Name", "Complete", "Markets"]
            click.echo(tabulate(table_data, headers=headers, tablefmt="simple"))
            click.echo(f"\nTotal studies: {len(studies)}")

    except Exception as e:
        click.secho(f"✗ Error listing studies: {e}", fg="red")
        sys.exit(1)


@study.command(name="info")
@click.argument("study_id")
def study_info(study_id):
    """
    Show detailed information about a specific study.

    Displays markets, file locations, concept counts, and more.

    Example:
        kantar-synthetic study info 61405445-01
    """
    from src.kantar.study_catalog import StudyCatalog

    try:
        catalog = StudyCatalog()
        study = catalog.get_study(study_id)

        if not study:
            click.secho(f"✗ Study not found: {study_id}", fg="red")
            sys.exit(1)

        click.secho(f"\n{study.study_name}", fg="cyan", bold=True)
        click.echo(f"Study ID: {study.study_id}")
        click.echo(f"Path: {study.path}")
        click.echo(f"\nMarkets: {len(study.markets)}")

        for market_code, market in study.markets.items():
            status = "✓" if market.is_complete else "✗"
            color = "green" if market.is_complete else "red"

            click.secho(f"\n  {status} {market_code}", fg=color, bold=True)

            if market.excel_files:
                click.echo(f"    Ground Truth:")
                for excel in market.excel_files:
                    click.echo(f"      {excel.name}")
            else:
                click.echo(f"    Ground Truth: None")

            if market.pptx_files:
                click.echo(f"    Concepts:")
                for pptx in market.pptx_files:
                    click.echo(f"      {pptx.name}")
            else:
                click.echo(f"    Concepts: None")

        click.echo(f"\nComplete Markets: {', '.join(study.complete_markets) if study.complete_markets else 'None'}")

    except Exception as e:
        click.secho(f"\n✗ Error: {e}", fg="red")
        sys.exit(1)


@study.command(name="verify")
@click.argument("study_id")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed verification output")
def verify_study(study_id, verbose):
    """
    Verify study structure and readiness for generation.

    Checks folder structure, file presence, and data extraction readiness.

    Example:
        kantar-synthetic study verify 61405445-01
        kantar-synthetic study verify 61407017 --verbose
    """
    click.echo(f"Verifying study: {study_id}\n")

    # TODO: Implement comprehensive study validation
    # This is a placeholder - will be implemented in study_validator.py

    click.secho("Study verification not yet fully implemented", fg="yellow")
    click.echo("\nBasic checks:")

    from src.kantar.study_catalog import StudyCatalog

    try:
        catalog = StudyCatalog()
        study = catalog.get_study(study_id)

        if not study:
            click.secho(f"✗ Study not found: {study_id}", fg="red")
            sys.exit(1)

        click.secho(f"✓ Study folder exists", fg="green")
        click.echo(f"  Path: {study.path}")

        click.echo(f"\nMarket Status:")
        for market_code in sorted(study.markets.keys()):
            market = study.markets[market_code]

            has_excel = len(market.excel_files) > 0
            has_pptx = len(market.pptx_files) > 0
            is_complete = market.is_complete

            if is_complete:
                click.secho(f"  ✓ {market_code}: Complete", fg="green")
                if verbose:
                    click.echo(f"      Excel: {len(market.excel_files)} file(s)")
                    click.echo(f"      PPTX:  {len(market.pptx_files)} file(s)")
            else:
                click.secho(f"  ✗ {market_code}: Incomplete", fg="red")
                if not has_excel:
                    click.echo(f"      Missing: Ground truth Excel file")
                if not has_pptx:
                    click.echo(f"      Missing: Concept PPTX file")

        complete_count = len(study.complete_markets)
        total_count = len(study.markets)

        click.echo(f"\nSummary: {complete_count}/{total_count} markets ready")

        if complete_count == 0:
            click.secho("\n✗ No markets are ready for generation", fg="red")
            sys.exit(1)
        elif complete_count < total_count:
            click.secho(f"\n⚠ Only {complete_count} markets ready", fg="yellow")
        else:
            click.secho(f"\n✓ All markets ready for generation", fg="green")

    except Exception as e:
        click.secho(f"\n✗ Verification failed: {e}", fg="red")
        sys.exit(1)
