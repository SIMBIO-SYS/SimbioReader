from importlib.metadata import metadata
from pathlib import Path

import rich_click as click
from rich.console import Console
from rich.table import Table

from SimbioReader.constants import (
    CONTEXT_SETTINGS,
    PSA_DATAMODEL_COMPATIBILITY,
    SIMBIO_DATAMODEL_COMPATIBILITY,
    progEpilog,
)
from SimbioReader.sr import SimbioReader
from SimbioReader.sr import version as code_version

__version__ = code_version.full()


click.rich_click.TEXT_MARKUP = "rich"
click.rich_click.FOOTER_TEXT = progEpilog


@click.group(
    context_settings=CONTEXT_SETTINGS,
    invoke_without_command=True,
)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Read SIMBIO-SYS products and inspect mission reference data."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
def version() -> None:
    """Show code and compatible data-model versions."""
    version_table = Table.grid(padding=(0, 2))
    version_table.add_column(style="bold")
    version_table.add_column()
    version_table.add_row(
        "SimbioReader version:",
        f"[bold blue]{__version__}[/bold blue]",
    )
    version_table.add_row("", "")
    version_table.add_row("[bold]Data-model compatibility:[/bold]", "")
    version_table.add_row(
        "PDS Information Model:",
        (
            f"{PSA_DATAMODEL_COMPATIBILITY['version']} "
            f"({PSA_DATAMODEL_COMPATIBILITY['coded']})"
        ),
    )
    version_table.add_row(
        "SIMBIO-SYS Data Model:",
        (
            f"{SIMBIO_DATAMODEL_COMPATIBILITY['version']} "
            f"({SIMBIO_DATAMODEL_COMPATIBILITY['coded']})"
        ),
    )
    Console().print(version_table)


@cli.command()
def about() -> None:
    """Display package and author information."""
    package = metadata("SimbioReader")
    about_table = Table.grid(padding=(0, 2))
    about_table.add_column(style="bold")
    about_table.add_column()
    about_table.add_row("Package:", package["Name"])
    about_table.add_row("Version:", package["Version"])
    about_table.add_row("Description:", package["Summary"])
    about_table.add_row("Author:", package["Author"])
    about_table.add_row("Author email:", package["Author-email"])
    about_table.add_row(
        "Repository:",
        "https://github.com/SIMBIO-SYS/SimbioReader",
    )
    Console().print(about_table)


@cli.command()
@click.option(
    "--kind",
    type=click.Choice(
        ["phases", "subphases", "tests", "all"],
        case_sensitive=False,
    ),
    default="all",
    show_default=True,
    help="Select the mission information to display.",
)
@click.option("-d", "--date", type=str, help="Select entries by date.")
@click.option("-n", "--name", type=str, help="Select an entry by name.")
@click.option("--phase", type=str, help="Filter tests by mission phase.")
@click.option("--subphase", type=str, help="Filter tests by mission subphase.")
def phases(
    kind: str,
    date: str | None,
    name: str | None,
    phase: str | None,
    subphase: str | None,
) -> None:
    """Display mission phases, subphases, and test campaigns."""
    from SimbioReader.simbioInfo import Phase, SubPhase, Test

    console = Console()
    try:
        if kind in {"phases", "all"}:
            console.print(
                Phase(name=name, dt=date).show() if name or date else Phase.show_all()
            )

        if kind in {"subphases", "all"}:
            subphase_name = name if kind == "subphases" else subphase
            console.print(
                SubPhase(name=subphase_name, dt=date).show()
                if subphase_name or date
                else SubPhase.show_all()
            )

        if kind in {"tests", "all"}:
            if kind == "tests" and (name or date):
                console.print(Test(name=name, dt=date, subphase=subphase).show())
            else:
                console.print(
                    Test.show_all(
                        phase=phase,
                        subphase=subphase,
                        key=name if kind == "tests" else None,
                        date=date,
                    )
                )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command("filters")
@click.argument(
    "channel",
    type=click.Choice(["HRIC", "STC"], case_sensitive=False),
    required=False,
)
@click.option("-n", "--name", type=str, help="Show one filter by name.")
def filters(channel: str | None, name: str | None) -> None:
    """Display filter information for HRIC or STC."""
    from SimbioReader.simbioInfo import Filter, show_filters

    console = Console()
    normalized_channel = channel.upper() if channel else None
    normalized_name = name.strip().casefold().replace("-", "") if name else None

    if normalized_name is None:
        channels = (normalized_channel,) if normalized_channel else ("HRIC", "STC")
        for instrument in channels:
            try:
                console.print(f"[bold]{instrument}[/bold]")
                console.print(show_filters(instrument))
            except ValueError as exc:
                raise click.ClickException(str(exc)) from exc
        return

    channels = (normalized_channel,) if normalized_channel else ("HRIC", "STC")
    matches = []
    for instrument in channels:
        try:
            matches.append(
                (
                    instrument,
                    Filter(instrument, normalized_name).show(),
                )
            )
        except ValueError:
            continue

    if not matches:
        scope = normalized_channel or "HRIC and STC"
        assert name is not None
        raise click.ClickException(f"Filter '{name.strip()}' not found for {scope}.")

    for instrument, result in matches:
        console.print(f"[bold]{instrument}[/bold]")
        console.print(result)


@cli.command()
@click.argument(
    "file",
    type=click.Path(exists=True, path_type=Path),
)
@click.option("--hk", is_flag=True, help="Show housekeeping information.")
@click.option("--detector", is_flag=True, help="Show detector information.")
@click.option(
    "--data-structure",
    is_flag=True,
    help="Show data-structure information.",
)
@click.option(
    "--all",
    "all_info",
    is_flag=True,
    help="Show all available information.",
)
@click.option(
    "--filters",
    "filter_flag",
    is_flag=True,
    help="Show product filter information.",
)
@click.option("-d", "--debug", is_flag=True, help="Enable debug mode.")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose mode.")
@click.option(
    "-s",
    "--summarize",
    is_flag=True,
    help="Show only the product summary.",
)
@click.option(
    "--no-symbols",
    is_flag=True,
    help="Keep unit names instead of converting them to symbols.",
)
def info(
    file: Path,
    hk: bool,
    detector: bool,
    data_structure: bool,
    all_info: bool,
    filter_flag: bool,
    debug: bool,
    verbose: bool,
    summarize: bool,
    no_symbols: bool,
) -> None:
    """Display information from a PDS4 product."""
    console = Console()
    product = SimbioReader(
        file,
        console=console,
        debug=debug,
        verbose=verbose,
    )
    if summarize:
        console.print(product.summary())
        return

    console.print(
        product.show(
            hk=hk,
            detector=detector,
            data_structure=data_structure,
            filters=filter_flag,
            all_info=all_info,
            no_symbols=no_symbols,
        )
    )
