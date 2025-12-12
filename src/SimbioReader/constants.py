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

<<<<<<< HEAD
VERSION = (0,6,0,'f',1)
=======
<<<<<<< HEAD
VERSION = (0,6,0,'d',1)
=======
VERSION = (0,5,11,'f',1)
>>>>>>> 4e9375c87b013a81d187dcf5f90a1bef117aa41a
>>>>>>> b335b6d87a999de6de2ed0b43e4df20cd4a95898

datamodel='1.22.0.0'

data_types = {
    "UnsignedLSB2": {'envi':2,'bits':16},
    "IEEE754LSBSingle":{'envi':4,'bits':32},
}
