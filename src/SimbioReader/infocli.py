#!/usr/bin/env python3
import rich_click as click
from rich.console import Console
from functools import wraps
from SimbioReader.constants import FMODE, MSG, CONTEXT_SETTINGS, progEpilog, data_types, datamodel

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.FOOTER_TEXT = progEpilog

version='0.1.0'
update='2024-09-01'

def show_version():
    """Display version and exit"""
    console = Console()
    console.print(f"SimbioInfo version [blue bold]{version}[/]")
    console.print(f"Last Update [blue bold]{update}[/]")


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.option('--version', 'ver', is_flag=True, help='Show the version', default=False)
@click.pass_context
def cli(ctx,ver: bool):
    """Simbio Info CLI"""
    if ver:
        show_version()
        ctx.exit()
    pass


def common_options_sub(func):
    """Common options for the commands"""
    @wraps(func)
    @click.option('-a', '--all', is_flag=True, help='Show all the phases', default=False)
    @click.option('-d', '--date', type=str, help='Show the phases for the given date', default=None)
    @click.option('-n', '--name', type=str, help='Show the phase with the given name', default=None)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@cli.command()
@common_options_sub
@click.pass_context
def phases(ctx,all: bool, date: str, name: str):
    """Display required phase(s)"""
    from SimbioReader.simbioInfo import get_phase, Phase
    from dateutil.parser import parse
    console = Console()
    if not date and not name:
        all = True

    if date:
        try:
            ndt = parse(date, ignoretz=True)
        except Exception as e:
            console.print(f"{MSG.ERROR}Cant convert to date the string: {str(e)}")
            all = True
    if all:
        console.print(Phase.show_all())
    elif date:
        try:
            console.print(get_phase(dt=date).show())
        except ValueError as e:
            ctx.fail(str(e))
    elif name:
        try:
            console.print(get_phase(name=name).show())
        except ValueError as e:
            ctx.fail(str(e))


@cli.command()
@common_options_sub
def subphases(all: bool, date: str, name: str):
    """Display required subphase(s)"""
    from SimbioReader.simbioInfo import get_subphase, SubPhase
    from dateutil.parser import parse
    console = Console()
    if not date and not name:
        all = True
    if date:
        try:
            ndt = parse(date, ignoretz=True)
        except Exception as e:
            console.print(
                f"{MSG.ERROR}Cant convert to date the string: {str(e)}")
            all = True
    if all:
        console.print(SubPhase.show_all())
    elif date:
        console.print(get_subphase(dt=date).show())
    elif name:
        console.print(get_subphase(name=name).show())


@cli.command()
@click.option('-a', '--all', is_flag=True, help='Show all the tests', default=False)
@click.option('-d', '--date', type=str, help='Show the tests for the given date', default=None)
@click.option('-n', '--name', type=str, help='Show the tests for the given name', default=None)
@click.option('-p', '--phase', type=str, help='Show the tests for the given phase', default=None)
@click.option('-s', '--subphase', type=str, help='Show the tests for the given subphase', default=None)
@click.pass_context
def tests(ctx,all: bool = None, date: str = None, name: str = None, phase: str = None, subphase: str = None):
    """Display required test(s)"""
    from SimbioReader.simbioInfo import Test
    console = Console()
    if not date and not name and not phase and not subphase:
        all = True
    if all:
        console.print(Test.show_all())
    elif date:
        try:
            console.print(Test(dt=date).show())
        except ValueError as e:
            ctx.fail(str(e))
    elif name:
        # console.print(Test.show(key=name))
        try:
            console.print(Test(name, subphase=subphase).show())
        except:
            if not subphase:
                console.print(f"{MSG.WARNING}Test {name.title()} not found. Please try to specific a subphase.")
                ctx.exit()
            console.print(f"{MSG.WARNING}Test {name.title()} for subphase {subphase.upper()} not found.")
            console.print(Test.show_all(key=name))
    elif phase:
        console.print(Test.show_all(phase=phase))
    elif subphase:
        console.print(Test.show_all(subphase=subphase))


@cli.command("filters")
@click.argument('channel', required=True)
@click.option('-n', '--name', type=str, help='Show the filter for the given name', default=None)
@click.pass_context
def filters_act(ctx, channel: str,name:str):
    """Display the filters for the given channel"""
    from SimbioReader.simbioInfo import show_filters
    console = Console()
    if name:
        from SimbioReader.simbioInfo import Filter
        try:
            fil=Filter(channel,name)
            console.print(fil.show())
        except ValueError as e:
            ctx.fail(str(e))
    else:
        console.print(show_filters(channel))


if __name__ == "__main__":
    cli()