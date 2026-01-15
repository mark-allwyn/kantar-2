"""
Profile management subcommands for kantar-synthetic CLI.
"""

import click
from tabulate import tabulate


@click.group()
def profile():
    """Manage market demographic profiles."""
    pass


@profile.command(name="list")
@click.option("--format", "output_format", type=click.Choice(["table", "simple"]),
              default="table", help="Output format")
def list_profiles(output_format):
    """
    List available market demographic profiles.

    Profiles define demographic distributions for custom generation mode.

    Example:
        kantar-synthetic profile list
    """
    from src.kantar.market_profiles import list_market_profiles

    try:
        profiles = list_market_profiles()

        if output_format == "simple":
            for name, description in profiles.items():
                click.echo(f"{name}: {description}")
        else:  # table format
            table_data = [[name, desc] for name, desc in profiles.items()]
            headers = ["Profile Name", "Description"]
            click.echo(tabulate(table_data, headers=headers, tablefmt="simple"))

    except Exception as e:
        click.secho(f"✗ Error listing profiles: {e}", fg="red")


@profile.command(name="show")
@click.argument("profile_name")
def show_profile(profile_name):
    """
    Show detailed information about a market profile.

    Example:
        kantar-synthetic profile show US_gaming
    """
    from src.kantar.market_profiles import get_market_profile
    import json

    try:
        profile = get_market_profile(profile_name)

        click.secho(f"\n{profile['name']}", fg="cyan", bold=True)
        click.echo(f"{profile['description']}\n")

        click.echo("Demographics Configuration:")
        click.echo(json.dumps(profile['demographics'], indent=2))

    except ValueError as e:
        click.secho(f"✗ {e}", fg="red")
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
