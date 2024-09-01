from rich.table import Table
from rich.panel import Panel


class Filter:
    def __init__(self,channel:str, name:str):
        """Filter class"""
        if channel.lower() == "hric":
            from SimbioReader.filters import hricFilters
            flt=hricFilters
        elif channel.lower() == "stc":
            from SimbioReader.filters import stcFilters
            flt=stcFilters
        else:
            raise ValueError("Invalid channel.")
        itm = [elem for elem in flt.values() if elem['name']==name]
        if len(itm)==0:
            raise ValueError("No filters found.")
        elif len(itm)>1:
            raise ValueError("Multiple filters found. Please provide a detailed filter name.")
        elif len(itm)==1:
            itm=itm[0]
  
        for key, value in itm.items():
            setattr(self, key, value)      
        if 'name' not in self.__dict__:
            raise ValueError("Filter not found.")
        
    def __str__(self):
        return f"Filter {self.name}"
    
    def __repr__(self):
        return self.__str__()
    
    def show(self):
        """Show the filter data in a table"""
        tb = Table.grid()
        tb.add_column(style='yellow')
        sep= ' = '
        for key, value in self.__dict__.items():
            tb.add_row(key.title(), sep, value)
        return Panel(tb,title='Filter',
                     border_style='yellow', expand=False)
        
    


def show_filters(channel:str)->Table:
    if channel.lower() == "hric":
        from SimbioReader.filters import hricFilters
        flt=hricFilters
    elif channel.lower() == "stc":
        from SimbioReader.filters import stcFilters
        flt=stcFilters
    else:
        raise ValueError("Invalid channel.")
    tb = Table(style="yellow")
    elem=next(iter(flt.values()))
    mask = {"desc":"Description"}
    for item in elem.keys():
        tb.add_column(item.title() if item not in ['desc'] else mask[item])

    for name, item in flt.items():
        tb.add_row(*[item[key] for key in elem.keys()])
        
    return tb