#! /usr/bin/env python3
from datetime import datetime

from dateutil.parser import parse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from SimbioReader.phases import phases
from SimbioReader.subphases import subphases
from SimbioReader.tests import tests

dateFormat = "%Y-%m-%d %H:%M:%S"
console = Console()


class Phase:
    """
    Represents a phase, defined by a name or a date.

    Attributes:
        name (str): The name of the phase.
        start (datetime): The start time of the phase.
        end (datetime): The end time of the phase.
        extended_name (str): The extended name of the phase (LPName).
    """
    def __init__(self, name:str=None, dt:datetime|str=None):
        """
        Initializes a Phase object.

        Args:
            name (str, optional): The name of the phase. Defaults to None.
            dt (datetime | str, optional): The date used to determine the phase. Defaults to None.

        Raises:
            ValueError: If neither name nor dt is provided, or if no phase is found.
        """
        if name:
            phase_data = phases.get(name)
            if not phase_data:
                raise ValueError(f"Phase '{name}' not found.")
        elif dt:
            if isinstance(dt, str):
                dt = parse(dt,ignoretz=True)
            phase_data = self._find_phase_by_date(dt)
            if not phase_data:
                raise ValueError("No phase found for the given date.")
        else:
            raise ValueError("You must provide a phase name or a date.")
        
        self.name = phase_data["name"]
        self.start = parse(phase_data["start"],ignoretz=True)
        self.end = parse(phase_data["end"],ignoretz=True)
        self.extended_name = phase_data["LPName"]

    def _find_phase_by_date(self, dt):
        """
        Finds a phase by a given date.

        Args:
            dt (datetime): The date to find the corresponding phase.

        Returns:
            dict | None: The phase data if found, otherwise None.
        """
        for phase_name, phase_data in phases.items():
            start = parse(phase_data["start"],ignoretz=True)
            end = parse(phase_data["end"],ignoretz=True)
            if start <= dt <= end:
                return phase_data
        return None

    def __str__(self)-> str:
        """
        Returns a string representation of the phase.

        Returns:
            str: The string representation of the phase.
        """
        return f"Phase {self.name}"

    def __repr__(self) -> str:
        """
        Returns the official string representation of the phase.

        Returns:
            str: The string representation of the phase.
        """
        return self.__str__()

    @staticmethod
    def show_all()->Table:
        """
        Displays a table of all phases with their names and start/end times.

        Returns:
            rich.table.Table: A table displaying all phases.
        """
        tb = Table(style="yellow")
        tb.add_column('Phase Name')
        tb.add_column('Start Time')
        tb.add_column('End Time')
        for phase_name, phase_data in phases.items():
            if phase_name == "None":
                continue
            tb.add_row(f"{phase_data['LPName']} ({phase_name})",
                       parse(phase_data['start']).strftime(dateFormat),
                       parse(phase_data['end']).strftime(dateFormat))
        return tb
    
    def show(self):
        """
        Displays a table showing the details of this phase.

        Returns:
            rich.table.Table: A table displaying the phase details.
        """
        tb = Table(style="yellow")
        tb.add_column('Phase Name')
        tb.add_column('Start Time')
        tb.add_column('End Time')
        tb.add_row(f"{self.extended_name} ({self.name})",
                   self.start.strftime(dateFormat),
                   self.end.strftime(dateFormat))
        return tb

# Funzione di utilità per ottenere una fase


def get_phase(name:str=None, dt:datetime| str=None)->Phase:
    """
    Utility function to obtain a Phase object by name or date.

    Args:
        name (str, optional): The name of the phase. Defaults to None.
        dt (datetime | str, optional): The date used to determine the phase. Defaults to None.

    Returns:
        Phase: The corresponding Phase object.
    """
    if isinstance(dt, str):
        dt = parse(dt, ignoretz=True)
    return Phase(name=name, dt=dt)



class SubPhase:
    """
    Represents a subphase, which is a subdivision of a phase.

    Attributes:
        name (str): The name of the subphase.
        start (datetime): The start time of the subphase.
        end (datetime): The end time of the subphase.
        phase (Phase): The parent phase of the subphase.
        extended_name (str): The extended name of the subphase (LPName).
    """
    
    def __init__(self, name:str=None , dt:datetime | str = None):
        """
        Initializes a SubPhase object.

        Args:
            name (str, optional): The name of the subphase. Defaults to None.
            dt (datetime | str, optional): The date used to determine the subphase. Defaults to None.

        Raises:
            ValueError: If neither name nor dt is provided, or if no subphase is found.
        """
        if name:
            subphase_data = subphases.get(name)
            if not subphase_data:
                raise ValueError(f"SubPhase {name} not found.")
        elif dt:
            if isinstance(dt, str):
                dt = parse(dt,ignoretz=True)
            subphase_data = self._find_subphase_by_date(dt)
            if not subphase_data:
                raise ValueError("No subphase found for the given date.")
        else:
            raise ValueError("You must provide a subphase name or a date.")
        self.name = subphase_data['name']
        self.start = parse(subphase_data['start'])
        self.end = parse(subphase_data['end'])
        self.phase = Phase(subphase_data['phase'])
        self.extended_name = subphase_data['LPName']

    def _find_subphase_by_date(self, dt):
        """
        Finds a subphase by a given date.

        Args:
            dt (datetime): The date to find the corresponding subphase.

        Returns:
            dict | None: The subphase data if found, otherwise None.
        """
        for subphase_name, subphase_data in subphases.items():
            start = parse(subphase_data["start"],ignoretz=True)
            end = parse(subphase_data["end"],ignoretz=True)
            if start <= dt <= end:
                return subphase_data
        return None
    
    def __str__(self) -> str:
        """
        Returns a string representation of the subphase.

        Returns:
            str: The string representation of the subphase.
        """
        return f"SubPhase {self.name}"

    def __repr__(self) -> str:
        """
        Returns the official string representation of the subphase.

        Returns:
            str: The string representation of the subphase.
        """
        return self.__str__()
    
    @staticmethod
    def show_all() -> Table:
        """
        Displays a table of all subphases with their names, phases, and start/end times.

        Returns:
            rich.table.Table: A table displaying all subphases.
        """
        tb = Table(style="yellow")
        tb.add_column('SubPhase Name')
        tb.add_column('Extended Name')
        tb.add_column('Phase')
        tb.add_column('Start Time')
        tb.add_column('End Time')
        for phase_name, phase_data in subphases.items():
            if phase_name == "None":
                continue
            tb.add_row(phase_name,
                       phase_data['LPName'],
                       phase_data['phase'],
                       parse(phase_data['start']).strftime(dateFormat),
                       parse(phase_data['end']).strftime(dateFormat))
        return tb
    
    def show(self) -> Table:
        """
        Displays a table showing the details of this subphase.

        Returns:
            rich.table.Table: A table displaying the subphase details.
        """
        tb = Table(style="yellow")
        tb.add_column('SubPhase Name')
        tb.add_column('Extended Name')
        tb.add_column('Phase')
        tb.add_column('Start Time')
        tb.add_column('End Time')
        tb.add_row(self.name,
                   self.extended_name,
                   self.phase.name,
                   self.start.strftime(dateFormat),
                   self.end.strftime(dateFormat))
        return tb

def get_subphase(name:str=None, dt:datetime|str =None)->SubPhase:
    """
    Utility function to obtain a SubPhase object by name or date.

    Args:
        name (str, optional): The name of the subphase. Defaults to None.
        dt (datetime | str, optional): The date used to determine the subphase. Defaults to None.

    Returns:
        SubPhase: The corresponding SubPhase object.
    """
    if isinstance(dt, str):
        dt = parse(dt, ignoretz=True)
    return SubPhase(name=name, dt=dt)

def get_subphases_by_phase(phase_name:str)->list[str]|str:
    """
    Returns a list of subphases for a given phase.

    Args:
        phase_name (str): The name of the phase.

    Returns:
        list[str] | str: A list of subphases if more than one, or a single subphase name if only one.
    
    Raises:
        ValueError: If no subphases are found for the given phase.
    """
    elem=[subphase_name for subphase_name, subphase_data in subphases.items() if subphase_data['phase'] == phase_name]
    if len(elem)==1:
        return elem[0]
    elif len(elem)==0:
        raise ValueError(f"No subphases found for the phase {phase_name}")
    else:
        return elem
    
def compare_str(str1:str, str2:str)->bool:
    """
    Compares two strings to see if the first string (or its components if split by spaces) is contained within the second string.

    Args:
        str1 (str): The first string to compare.
        str2 (str): The second string to compare against.

    Returns:
        bool: True if str1 is contained within str2, otherwise False.
    """
    if ' ' in str1:
        pieces = str1.split(' ')
        return all(piece.lower() in str2.lower() for piece in pieces)
    else:
        return str1.lower() in str2.lower()
     
class Test:
    """
    Represents a test, associated with a specific subphase.

    Attributes:
        name (str): The name of the test.
        start (datetime): The start time of the test.
        end (datetime): The end time of the test.
        subphase (str): The subphase associated with the test.
    """
    
    def __init__(self, name:str=None, dt:datetime|str=None, subphase:str=None):
        """
        Initializes a Test object.

        Args:
            name (str, optional): The name of the test. Defaults to None.
            dt (datetime | str, optional): The date used to determine the test. Defaults to None.
            subphase (str, optional): The subphase associated with the test. Required if name is provided. Defaults to None.

        Raises:
            ValueError: If neither name nor dt is provided, or if no test is found, or if multiple tests are found without a detailed name.
        """
        if name:
            test_data = tests.get(name)
            if not test_data:
                if not subphase:
                    raise ValueError(f"To search a Test by name a subphase name is required.")
                sub_list = get_test_by_subphase(subphase)
                if not sub_list:
                    raise ValueError(f"Test {name} not found.")
                else:
                    
                    itm=[tests[testname] for testname in sub_list if compare_str(name, tests[testname]['name'])]
                    if len(itm)>1:
                        raise ValueError(f"Multiple tests found for the subphase {subphase}. Please provide detaile the test name.")
                    elif len(itm)==1:
                        test_data = itm[0]
                    else:
                        raise ValueError(f"Test {name} not found.")

        elif dt:
            if isinstance(dt, str):
                dt = parse(dt,ignoretz=True)
            test_data = self._find_test_by_date(dt)
            if not test_data:
                raise ValueError("No test found for the given date.")
        else:
            raise ValueError("You must provide a test name or a date.")
        self.name = test_data['name']
        self.start = parse(test_data['start'])
        self.end = parse(test_data['end'])
        self.subphase = test_data['subphase']
        
    def _find_test_by_date(self, dt):
        """
        Finds a test by a given date.

        Args:
            dt (datetime): The date to find the corresponding test.

        Returns:
            dict | None: The test data if found, otherwise None.
        """
        for test_name, test_data in tests.items():
            start = parse(test_data["start"], ignoretz=True)
            end = parse(test_data["end"], ignoretz=True)
            # console.print(f"Start: {start}, End: {end}, Date: {dt}")
            if start <= dt <= end:
                return test_data
        return None
    
    def __str__(self) -> str:
        """
        Returns a string representation of the test.

        Returns:
            str: The string representation of the test.
        """
        return f"Test {self.name} on {self.subphase}"
    
    def __repr__(self) -> str:
        """
        Returns the official string representation of the test.

        Returns:
            str: The string representation of the test.
        """
        return self.__str__()
    
    def show(self) -> Table:
        """
        Displays a table showing the details of this test.

        Returns:
            rich.table.Table: A table displaying the test details.
        """
        tb = Table(style="yellow")
        tb.add_column('Test Name')
        tb.add_column('SubPhase')
        tb.add_column('Start Time')
        tb.add_column('End Time')
        tb.add_row(self.name,self.subphase,self.start.strftime(dateFormat),self.end.strftime(dateFormat))
        return tb
    
    @staticmethod
    def show_all(phase:str=None,subphase:str=None,key:str=None,date:datetime|str=None) -> Table:
        """
        Displays a table showing all tests that match the provided filters.

        Args:
            phase (str, optional): The phase to filter tests by. Defaults to None.
            subphase (str, optional): The subphase to filter tests by. Defaults to None.
            key (str, optional): A keyword to search within test names. Defaults to None.
            date (datetime | str, optional): A date to filter tests by. Defaults to None.

        Returns:
            rich.table.Table: A table displaying the filtered tests.
        """
        tb = Table(style="yellow")
        tb.add_column('Test Name')
        tb.add_column('SubPhase')
        tb.add_column('Start Time')
        tb.add_column('End Time')
        console.print(f"Phase: {phase}, SubPhase: {subphase}, Key: {key}, Date: {date}")
        if date:
            if isinstance(date, str):
                date = parse(date, ignoretz=True)
        for test_name, test_data in tests.items():
            if subphase and not test_data['subphase'].lower() == subphase.lower():
                continue

            if not date and key:
                if not compare_str(key, test_data['name']):
                    continue    

            if date :
                start = parse(test_data['start'], ignoretz=True)
                end = parse(test_data['end'], ignoretz=True)
                if not start <=date <=end:
                    continue
            if phase:
                if not test_data['subphase'].lower() in get_subphases_by_phase(phase):
                    continue
            tb.add_row(test_data['name'],
                       test_data['subphase'],
                       parse(test_data['start']).strftime(dateFormat),
                       parse(test_data['end']).strftime(dateFormat))
        return tb

def get_test_by_subphase(subphase:str)->list[str] | None:
    """
    Returns a list of tests for a given subphase.

    Args:
        subphase (str): The name of the subphase.

    Returns:
        list[str] | None: A list of test names, or None if no tests are found.
    """
    elem= [test_name for test_name, test_data in tests.items() if test_data['subphase'].lower() == subphase.lower()]
    if len(elem)==0:
        return None
    elif len(elem)==1:
        return elem[0]
    else:
        return elem
        

class Filter:
    """
    Represents a filter for a specific channel, either 'HRIC' or 'STC'.
    
    Attributes:
        channel (str): The channel associated with the filter.
        name (str): The name of the filter.
        Other attributes dynamically assigned based on filter data.
    """
    
    def __init__(self, channel: str, name: str):
        """
        Initializes a Filter object based on the specified channel and filter name.

        Args:
            channel (str): The channel for which the filter is associated. Must be 'HRIC' or 'STC'.
            name (str): The name of the filter to initialize.
        
        Raises:
            ValueError: If the channel is invalid, or if no/multiple filters are found with the given name.
        """
        if channel.lower() == "hric":
            from SimbioReader.filters import hricFilters
            flt = hricFilters
        elif channel.lower() == "stc":
            from SimbioReader.filters import stcFilters
            flt = stcFilters
        else:
            raise ValueError("Invalid channel.")
        itm = [elem for elem in flt.values() if elem['name'].lower() == name.lower()]
        if len(itm) == 0:
            raise ValueError(f"No filter found with the name {name}.")
        elif len(itm) > 1:
            raise ValueError(
                "Multiple filters found. Please provide a detailed filter name.")
        elif len(itm) == 1:
            itm = itm[0]

        for key, value in itm.items():
            setattr(self, key, value)
        if 'name' not in self.__dict__:
            raise ValueError("Filter not found.")

    def __str__(self):
        """
        Returns a string representation of the Filter object.

        Returns:
            str: A string in the format 'Filter <name>'.
        """
        return f"Filter {self.name}"

    def __repr__(self):
        """
        Returns a string representation for debugging purposes.

        Returns:
            str: A string in the format 'Filter <name>'.
        """
        return self.__str__()

    def show(self)->Panel:
        """
        Displays the filter's data in a formatted table.

        Returns:
            Panel: A rich Panel object containing a table with the filter's attributes and values.
        """
        tb = Table.grid()
        tb.add_column(style='yellow')
        sep = ' = '
        for key, value in self.__dict__.items():
            tb.add_row(key.title(), sep, value)
        return Panel(tb, title='Filter',
                     border_style='yellow', expand=False)


def show_filters(channel: str) -> Table:
    """
    Displays all filters for a specified channel in a table.

    Args:
        channel (str): The channel for which to show filters. Must be 'HRIC' or 'STC'.

    Raises:
        ValueError: If the channel is invalid.

    Returns:
        Table: A rich Table object with all filters for the specified channel.
    """
    if channel.lower() == "hric":
        from SimbioReader.filters import hricFilters
        flt = hricFilters
    elif channel.lower() == "stc":
        from SimbioReader.filters import stcFilters
        flt = stcFilters
    else:
        raise ValueError("Invalid channel.")
    tb = Table(style="yellow")
    elem = next(iter(flt.values()))
    mask = {"desc": "Description"}
    for item in elem.keys():
        tb.add_column(item.title() if item not in ['desc'] else mask[item])

    for name, item in flt.items():
        tb.add_row(*[item[key] for key in elem.keys()])

    return tb
