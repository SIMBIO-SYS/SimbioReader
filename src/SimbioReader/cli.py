from rich.console import Console
from SimbioReader.sr import SimbioReader,version
import rich_click as click
from SimbioReader.constants import CONTEXT_SETTINGS,datamodel, progEpilog
from rich_click import rich_config
from pathlib import Path
# from semantic_version_tools import Vers
# from importlib.metadata import version as get_version



__version__ = version.full()

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.FOOTER_TEXT = progEpilog

def sh_version(ctx, self, value):
    """Display version and exit"""
    console = Console()
    console.print(f"SimbioReader version [blue bold]{version.short()}[/]")
    console.print(f"DataModel version [blue bold]{datamodel}[/]")
    ctx.exit()


@click.command(context_settings=CONTEXT_SETTINGS)
@rich_config(help_config={'header_text': f"SIMBIO-SYS Data Reader, version [blue]{version.short()}[/blue]"})
@click.argument('file', type=click.Path(exists=True,path_type=Path), required=True)
@click.option('--hk', is_flag=True, help='Show the HouseKeeping', default=False)
@click.option('--detector', is_flag=True, help='Show the Detector', default=False)
@click.option('--data-structure', is_flag=True, help='Show the Data Structure', default=False)
@click.option('--all', 'all_info', is_flag=True, help='Show all the information', default=False)
@click.option('--filters', 'filter_flag', is_flag=True, help='Show the filters for the given channel', default=False)
@click.option('-d', '--debug', is_flag=True, help='Debug mode', default=False)
@click.option('-v', '--verbose', is_flag=True, help='Verbose mode', default=False)
@click.option('-s','--summarize', is_flag=True, help='Show only the summary', default=False)
@click.option('--version', is_flag=True, help='Show the version and exit', default=False,)
@click.pass_context
def cli(ctx, file:Path, hk: bool = False, detector: bool=False, data_structure: bool = False, all_info: bool = False, 
        filter_flag : bool =False, debug: bool = False, verbose: bool = False, version:bool=False, summarize: bool = False):
    console = Console()
    if version:
        sh_version(ctx, cli, version)
    dat = SimbioReader(file, console=console, debug=debug, verbose=verbose)
    if summarize:
        console.print(dat.summary())
    else:
        console.print(dat.show(hk=hk, detector=detector,
                    data_structure=data_structure, filters=filter_flag, all_info=all_info))