
from rich.table import Table
from SimbioReader.console import console
from SimbioReader.phases  import phases


def simbioPhases():
    tb=Table()
    tb.add_column('Phase')
    tb.add_column('SubPhase')
    tb.add_column('Start')
    tb.add_column('End')
    for item in phases:
        if not phases[item]['LPName'] == 'None':
            tb.add_row(phases[item]['LPName'], phases[item]
                    ['name'], phases[item]['start'], phases[item]['stop'])
        
    console.print(tb)
    
def hricFilters():
    pass

def stcFilters():
    pass