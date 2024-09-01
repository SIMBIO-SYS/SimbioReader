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
        for item, item_data in flt.items():
            if item_data['name'] == name:
                for key, value in item_data.items():
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
        sep= '='
        for key, value in self.__dict__.items():
            tb.add_row(key, sep, value)
        tb.add_column('Filter Name')
        tb.add_column('Description')
        tb.add_column('Type')
        tb.add_column('Value')
        tb.add_row(self.name,self.desc,self.type,self.value)
        return Panel(tb,title='Filter',
                     border_style='yellow', expand=True)
        
    


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