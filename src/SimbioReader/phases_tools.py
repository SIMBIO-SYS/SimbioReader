#! /usr/bin/env python3
from datetime import datetime

from dateutil.parser import parse
from rich.console import Console
from rich.table import Table

from SimbioReader.phases import phases
from SimbioReader.subphases import subphases
from SimbioReader.tests import tests

dateFormat = "%Y-%m-%d %H:%M:%S"
console = Console()


class Phase:
    def __init__(self, name:str=None, dt:datetime|str=None):
        if name:
            phase_data = phases.get(name)
            if not phase_data:
                raise ValueError(f"Phase {name} not found.")
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
        for phase_name, phase_data in phases.items():
            start = parse(phase_data["start"],ignoretz=True)
            end = parse(phase_data["end"],ignoretz=True)
            if start <= dt <= end:
                return phase_data
        return None

    def __str__(self):
        return f"Phase {self.name}"

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def show():
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

# Funzione di utilità per ottenere una fase


def get_phase(name:str=None, dt:datetime| str=None)->Phase:
    if isinstance(dt, str):
        dt = parse(dt, ignoretz=True)
    return Phase(name=name, dt=dt)



class SubPhase:
    def __init__(self, name:str=None , dt:datetime | str = None):
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
        for subphase_name, subphase_data in subphases.items():
            start = parse(subphase_data["start"],ignoretz=True)
            end = parse(subphase_data["end"],ignoretz=True)
            if start <= dt <= end:
                return subphase_data
        return None
    
    def __str__(self):
        return f"SubPhase {self.name}"

    def __repr__(self) -> str:
        return self.__str__()
    
    @staticmethod
    def show():
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

def get_subphase(name:str=None, dt:datetime|str =None)->SubPhase:
    if isinstance(dt, str):
        dt = parse(dt, ignoretz=True)
    return SubPhase(name=name, dt=dt)

def get_subphases_by_phase(phase_name:str)->list[str]|str:
    elem=[subphase_name for subphase_name, subphase_data in subphases.items() if subphase_data['phase'] == phase_name]
    if len(elem)==1:
        return elem[0]
    elif len(elem)==0:
        raise ValueError(f"No subphases found for the phase {phase_name}")
    else:
        return elem
    
def compare_str(str1:str, str2:str)->bool:
    if ' ' in str1:
        pieces = str1.split(' ')
        return all(piece.lower() in str2.lower() for piece in pieces)
    else:
        return str1.lower() in str2.lower()
     
class Test:
    
    def __init__(self, name:str=None, dt:datetime|str=None, subphase:str=None):
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
        for test_name, test_data in tests.items():
            start = parse(test_data["end"], ignoretz=True)
            end = parse(test_data["end"], ignoretz=True)
            if start <= dt <= end:
                return test_data
        return None
    
    def __str__(self) -> str:
        return f"Test {self.name} on {self.subphase}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def show(self):
        tb = Table(style="yellow")
        tb.add_column('Test Name')
        tb.add_column('SubPhase')
        tb.add_column('Start Time')
        tb.add_column('End Time')
        tb.add_row(self.name,self.subphase,self.start.strftime(dateFormat),self.end.strftime(dateFormat))
        return tb
    
    @staticmethod
    def show_all(phase:str=None,subphase:str=None,key:str=None,date:datetime|str=None):
        tb = Table(style="yellow")
        tb.add_column('Test Name')
        tb.add_column('SubPhase')
        tb.add_column('Start Time')
        tb.add_column('End Time')
        if date:
            if isinstance(date, str):
                date = parse(date, ignoretz=True)
        for test_name, test_data in tests.items():
            if subphase and not test_data['subphase'].lower() == subphase.lower():
                continue

            if not date and not compare_str(key, test_data['name']):
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
    elem= [test_name for test_name, test_data in tests.items() if test_data['subphase'].lower() == subphase.lower()]
    if len(elem)==0:
        return None
    elif len(elem)==1:
        return elem[0]
    else:
        return elem
        


