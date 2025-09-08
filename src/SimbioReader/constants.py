class MSG:
    ERROR = "[red][ERROR][/red] "
    CRITICAL = "[red][CRITICAL][/red] "
    INFO = "[green][INFO][/green] "
    DEBUG = "[blue][DEBUG][/blue] "
    WARNING = "[yellow][WARNING][/yellow] "
    TODO = "[yellow][TODO][/yellow] "


class FMODE:
    READ = 'r'
    READ_BINARY = 'rb'
    WRITE = 'w'
    WRITE_BINARY = 'wb'
    APPEND = 'a'


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
progEpilog = "- For any information or suggestion please contact " \
    "[bold magenta]Romolo.Politi@inaf.it[/bold magenta]"

VERSION = (0,4,3,'d',1)

datamodel='1.15.0.0'

data_types = {
    "UnsignedLSB2": {'envi':2,'bits':16},
    "IEEE754LSBSingle":{'envi':4,'bits':32},
}

label_types = ['.xml','.lblx']