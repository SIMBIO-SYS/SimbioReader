from rich.console import Console
from SimbioReader.sr import SimbioReader, version
import rich_click as click
from SimbioReader.constants import CONTEXT_SETTINGS,datamodel
from rich_click import rich_config



def sh_version(ctx, self, value):
    """Display version and exit"""
    console = Console()
    console.print(f"SimbioReader version [blue bold]{version.short()}[/]")
    console.print(f"DataModel version [blue bold]{datamodel}[/]")
    ctx.exit()


@click.command(context_settings=CONTEXT_SETTINGS)
@rich_config(help_config={'header_text': f"SIMBIO-SYS Data Reader, version [blue]{version.short()}[/blue]"})
@click.argument('file', type=click.Path(exists=True), required=True)
@click.option('--hk', is_flag=True, help='Show the HouseKeeping', default=False)
@click.option('--detector', is_flag=True, help='Show the Detector', default=False)
@click.option('--data-structure', is_flag=True, help='Show the Data Structure', default=False)
@click.option('--all', 'all_info', is_flag=True, help='Show all the information', default=False)
@click.option('--filter', 'filter_flag', is_flag=True, help='Show the filters for the given channel', default=False)
@click.option('-d', '--debug', is_flag=True, help='Debug mode', default=False)
@click.option('-v', '--verbose', is_flag=True, help='Verbose mode', default=False)
@click.option('--version', is_flag=True, help='Show the version and exit', default=False,callback=sh_version)
def cli(file: str=None, hk: bool = False, detector: bool=False, data_structure: bool = False, all_info: bool = False, 
        filter_flag : bool =False, debug: bool = False, verbose: bool = False, version:bool = False):
    console = Console()
    dat = SimbioReader(file, console=console, debug=debug, verbose=verbose)
    console.print(dat.summary())