import hashlib
from datetime import datetime
from pathlib import Path
from xml.dom.minidom import Document, Element, parse, parseString

import numpy as np
import pandas as pd
from dateutil import parser
from PIL import Image as im
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from update_checker import UpdateChecker

from SimbioReader.constants import MSG, data_types
from SimbioReader.exceptions import SizeError
from SimbioReader.filters_tools import Filter
from SimbioReader.tools import (camel_case, gen_filename, getElement, getValue,
                                lidUpdate, lvidUpdate, pretty_print, updateXML)
from SimbioReader.version import version

__version__ = version.full()

class Detector:
    """
    A class representing a detector in a SIMBIO-SYS image.

    This class extracts and initializes various attributes related to a detector
    in a SIMBIO-SYS image, such as the first line, first sample, and number of lines.

    Args:
        dat (Element): An XML Element containing the detector information.

    Attributes:
        first_line (int): The first line number of the detector.
        first_sample (int): The first sample number of the detector.
        lines (int): The number of lines in the detector.
    """
    def __init__(self,dat:Element) -> None:
        detector = getElement(dat, 'img:Subframe')
        self.first_line = int(getValue(detector,'img:first_line'))
        self.first_sample = int(getValue(detector,'img:first_sample'))
        self.lines = int(getValue(detector,'img:lines'))
        self.samples = int(getValue(detector,'img:samples'))
        self.line_fov = float(getValue(detector,'img:line_fov'))
        self.sample_fov = float(getValue(detector,'img:sample_fov'))

    
    def __str__(self) -> str:
        """
        Returns a string representation of the Detector object.

        Returns:
            str: A string representation of the Detector object.
        """
        return f"Detector object"
    
    def __repr__(self) -> str:
        """
        Returns a string representation of the Detector object for debugging.

        Returns:
            str: A string representation of the Detector object.
        """
        return self.__str__()
    
    def show(self)-> Panel:
        """
        Displays the detector information in a formatted table.

        Returns:
            Panel: A Panel object containing the formatted detector information.
        """
        sep=' = '
        dt=Table.grid()
        dt.add_column(style='yellow',justify='right')
        dt.add_column()
        dt.add_column(style='cyan',justify='left')
        dt.add_row('First Line',sep,str(self.first_line))
        dt.add_row('First Sample',sep,str(self.first_sample))
        dt.add_row('Lines',sep,str(self.lines))
        dt.add_row('Samples',sep,str(self.samples))
        dt.add_row('Line FOV',sep,str(self.line_fov))
        dt.add_row('Sample FOV',sep,str(self.sample_fov))
        return Panel(dt,title='Detector',border_style='yellow',expand=False)
 

class DataStructure:
    """
    A class representing the data structure of a SIMBIO-SYS file.

    This class extracts and initializes various attributes related to the data 
    structure of a SIMBIO-SYS file, such as creation time, file size, and axes 
    configuration, based on an XML Element.

    Args:
        dat (Element): An XML Element containing the data structure information.
        channel (str): The channel identifier (e.g., 'HRIC', 'STC', 'VIHI').

    Attributes:
        creation_time (datetime): The creation time of the file.
        file_size (int): The size of the file.
        md5 (str): The MD5 checksum of the file.
        axes (int): The number of axes in the data structure.
        band (int): The band information (default is 1).
        data_type (str): The type of data (e.g., 'UnsignedLSB2', 'IEEE754LSBSingle').

    """
    
    def __init__(self, dat:Element, channel:str):
        # fao=getElement(dat,'File_Area_Observational')
        fl=getElement(dat,'File')
        self.creation_time = parser.parse(getValue(fl,'creation_date_time'))
        self.file_size = int(getValue(fl,'file_size'))
        self.md5 = getValue(fl,'md5_checksum')
        self.axes = int(getValue(dat,'axes'))
        self.band= None
        if self.axes == 3 and channel != 'vihi':
            raise ValueError("The number of axes is wrong for the channel")
        for i in range(self.axes):
            axis = getElement(dat,'Axis_Array',i)
            setattr(self,getValue(axis,'axis_name').lower(),int(getValue(axis,'elements')))
        if self.axes == 3:
            dat=getElement(dat,'Array_3D_Spectrum')
        elif self.axes == 2:
            dat=getElement(dat,'Array_2D_Image')
        self.data_type = getValue(dat,'data_type')
        if self.band is None:
            self.band = 1
        
        
    def __str__(self)->str:
        """
        Returns a string representation of the Datastructure.

        Returns:
            str: A string in the format 'DataStructure Object'.
        """
        return f"DataStructure object"
    
    def __repr__(self) -> str:
        """
        Returns a string representation for debugging purposes.

        Returns:
            str: A string in the format 'DataStructure Object'.
        """
        return self.__str__()
    
    def show(self):
        """
        Displays the data structure information in a formatted table.

        Returns:
            Panel: A rich Panel object containing the formatted table of data structure information.
        """
        sep=' = '
        dt=Table.grid()
        dt.add_column(style='yellow',justify='right')
        dt.add_column()
        dt.add_column(style='cyan',justify='left')
        for item in self.__dict__:
            dt.add_row(item,sep,str(self.__dict__[item]))
        # dt.add_row('Creation Time',sep,datetime.strftime(self.creation_time,"%Y-%m-%d"))
        # dt.add_row('File Size',sep,str(self.file_size))
        # dt.add_row('MD5 Checksum',sep,self.md5)
        # dt.add_row('Axes',sep,str(self.axes))
        return Panel(dt,title='Data Structure',border_style='yellow',expand=False)
        

class HK:
    """
    A class representing housekeeping data for a SIMBIO-SYS image.

    This class initializes various attributes from a pandas DataFrame containing
    housekeeping data and provides methods to display this information.

    Args:
        df (pd.DataFrame): A pandas DataFrame containing housekeeping data.

    Attributes:
        df (pd.DataFrame): The DataFrame containing housekeeping data.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initializes the HK object by extracting information from the DataFrame.

        Args:
            df (pd.DataFrame): A pandas DataFrame containing housekeeping data.
        """
        self.df = df
        for i in df.columns:
            if type(df[i].values[0]) is str:
                val = df[i].values[0].strip()
            else:
                val = df[i].values[0]
            setattr(self, i.strip().lower(), val)

    def show(self) -> Panel:
        """
        Displays the housekeeping information in a formatted table.

        Returns:
            Panel: A Panel object containing the formatted housekeeping information.
        """
        sep = " = "
        dt = Table.grid()
        dt.add_column(style="yellow", justify="right")
        dt.add_column()
        dt.add_column(style="cyan", justify="left")
        for i in self.df.columns:
            dt.add_row(
                " ".join(i.split("_")).title(), sep, f"{self.df[i].values[0]}".strip()
            )
        return Panel(dt, title="HouseKeeping", border_style="yellow", expand=False)

    def __str__(self) -> str:
        """
        Returns a string representation of the HK object.

        Returns:
            str: A string representation of the HK object.
        """
        return f"HK object"

    def __repr__(self) -> str:
        """
        Returns a string representation of the HK object for debugging.

        Returns:
            str: A string representation of the HK object.
        """
        return self.__str__()


class Target:
    def __init__(self, name: str, target_type: str):
        self.name = name
        self.target_type = target_type

        # other attributes will be added after the integration of the observation log in the PDS label

    def show(self):
        sep = " =  "
        tb = Table.grid()
        tb.add_column(style="yellow", justify="right")
        tb.add_column()
        tb.add_column()
        tb.add_row("Name", sep, self.name)
        tb.add_row("Type", sep, self.target_type)
        return Panel(tb, title="Target Info", border_style="blue", expand=False)

    def __str__(self):
        return f"Target(name={self.name}, type={self.target_type})"

    def __repr__(self):
        return self.__str__()

class SimbioObject:
    def __init__(self, file_name: str,  channel: str,
                 imaging: Element, geometry: Element,file_obs: Element, filter_name: str= None,console: Console = None, debug:bool=False, verbose:bool=False):
        if console is None:
            self.console = Console()
        else:
            self.console = console
        self.file_name = Path(file_name)
        self.filter_name = filter_name
        self.channel = channel
        self.imaging = imaging
        self.geometry = geometry
        self.debug=debug
        self.exposure_time = getValue(imaging, "img:exposure_duration")
        subFrame = getElement(imaging, "img:Subframe")
        self.firstLine = int(getValue(subFrame, 'img:first_line'))
        self.firstSample = int(getValue(subFrame, 'img:first_sample'))
        self.lines = int(getValue(subFrame, 'img:lines'))
        self.samples = int(getValue(subFrame, 'img:samples'))
        self.lineFov = float(getValue(subFrame, 'img:line_fov'))
        self.sampleFov = float(getValue(subFrame, 'img:sample_fov'))
        self.data_stucture = DataStructure(file_obs, self.channel)
        self.samples=self.data_stucture.sample
        self.lines=self.data_stucture.line
        self.bands=self.data_stucture.band
        if self.channel.upper() != 'VIHI':
            flt = getElement(imaging, 'img:Optical_Filter')
            self.filter=Filter(channel=self.channel,name=getValue(flt,'img:filter_name'))
        self.detector = Detector(imaging)
        if self.data_stucture.data_type == "UnsignedLSB2":
            dtype = np.int16
        elif self.data_stucture.data_type == "IEEE754LSBSingle":
            dtype = np.float32
        
        if verbose:
            console.print(f"{MSG.INFO}Loading: {self.file_name}")
            if self.data_stucture.axes == 3:
                console.print(f"{MSG.INFO}Image size: {self.samples}x{self.lines}x{self.bands}")
                imgSize = self.samples*self.lines*self.bands*data_types[self.data_stucture.data_type]['bits']
            else:
                console.print(f"{MSG.INFO}Image size: {self.samples}x{self.lines}")
                imgSize = self.samples*self.lines*data_types[self.data_stucture.data_type]['bits']
            
            console.print(f"{MSG.INFO}File size: {self.file_name.stat().st_size*8}")
            console.print(
                f"{MSG.INFO}Computed File Size: {imgSize}")
            if self.file_name.stat().st_size*8 != imgSize:
                raise SizeError(self.file_name.stat().st_size *
                                8,imgSize)
        #print(img_data['samples'],img_data['lines'],img_data['bands'])
        if self.data_stucture.axes == 3:
            self.img = np.fromfile(self.file_name, dtype=dtype,
                               count=self.samples*self.lines*self.bands)
        else:
            self.img = np.fromfile(self.file_name, dtype=dtype,
                                   count=self.samples*self.lines)
        if self.data_stucture.axes == 3: 
            if self.lines==1:
                self.img.shape = ( self.samples,self.bands)
            else:
                self.img.shape = (self.lines,self.samples, self.bands )
        else:
            self.img.shape = (self.samples, self.lines)
        if verbose:
            self.console.print(f"{MSG.INFO}Dimension of the old image array: {self.img.ndim}")
            # print(f"Size of the old image array: {self.img.size}")


    def show(self)->Panel:
        sep = " =  "
        tb = Table.grid()
        tb.add_column(style="yellow", justify="right")
        tb.add_column()
        tb.add_column()
        tb.add_row("File Name", sep, str(self.file_name))
        tb.add_row("Filter Name", sep, self.filter_name)
        tb.add_row("Channel", sep, self.channel.upper())
        tb.add_row("Exposure Time (s)", sep, str(self.exposure_time))
        pl=Panel(tb, title="Simbio Filter General Info", border_style="cyan", expand=False)
        return Panel(Columns([pl,self.filter.show(),self.data_stucture.show(),self.detector.show()]), title=f"Filter {self.filter_name.upper()} Info", border_style="magenta", expand=False)        

    def __str__(self):
        return f"Filter(name={self.filter_name})"

    def __repr__(self):
        return self.__str__()
    
    def savePreview(self,img_type:str='png',quality:int=100, outFolder:Path=None, tree:Document=None)->str|None:
        new_filename=gen_filename(self.file_name)
        if img_type in ['png','tif']:
            data = im.fromarray(self.img)
            image_file= f"{outFolder}/{new_filename}.{img_type}"
            if self.debug:
                self.console.print(
                    f"{MSG.DEBUG}Saving image {Path(image_file).name} with quality {quality}"
                )
            if 'cal' in self.file_name.stem:
                data.convert('RGB').save(image_file, quality=quality)
            else:
                data.save(image_file, quality=quality)
            if tree:
                fab=tree.createElement("File_Area_Browse")
                fl=tree.createElement("File")
                fln=tree.createElement("file_name")
                fln.appendChild(tree.createTextNode(f"{new_filename}.{img_type}"))
                fl.appendChild(fln)
                fl_ct=tree.createElement("creation_date_time")
                creatTime=datetime.now()
                fl_ct.appendChild(tree.createTextNode(creatTime.strftime("%Y-%m-%d")))
                fl.appendChild(fl_ct)
                fl_fs=tree.createElement("file_size")
                fl_fs.appendChild(tree.createTextNode(str(Path(image_file).stat().st_size)))
                fl_fs.setAttribute("unit","byte")
                fl.appendChild(fl_fs)
                fl_md5=tree.createElement("md5_checksum")
                fl_md5.appendChild(tree.createTextNode(hashlib.md5(
                    open(image_file, 'rb').read()).hexdigest()))
                fl.appendChild(fl_md5)
                fab.appendChild(fl)



                enc_img=tree.createElement("Encoded_Image")
                enc_offset=tree.createElement("offset")
                enc_offset.appendChild(tree.createTextNode("0"))
                enc_offset.setAttribute("unit","byte")
                enc_stid=tree.createElement("encoding_standard_id")
                enc_stid.appendChild(tree.createTextNode("PNG"))
                enc_img.appendChild(enc_offset)
                enc_img.appendChild(enc_stid)

                fab.appendChild(enc_img)
                return fab
        elif img_type == 'jpg':
            data = im.fromarray(self.img,mode='L')
            # print(data.getpixel((50,50)))
            data.save(f"{outFolder}/{new_filename}.{img_type}",
                      quality=quality)
        # print(self.img[0,0])
    
class Data:
    def __init__(
        self,
        channel: str,
        level: str,
        source_path: Path,
        file_obs: list,
        imaging: list,
        geometry: list,
        debug: bool = False,
        verbose: bool = False,
        console=None,
    ):
        if console is None:
            self.console = Console()
        else:
            self.console = console
        self.channel = channel
        if self.channel == 'vihi':
            self.segments = []
            self.seg_number=0
        else:
            self.filters =[]
        
        self.items_number = len(file_obs)
        
        self.level = level
        for i, fo in enumerate(file_obs):
            file_name = source_path.joinpath(getValue(fo, "file_name"))
            if verbose or debug:
                self.console.print(
                    f"{MSG.INFO}Processing file {i+1}/{self.items_number}: {file_name.name}"
                )
            if not file_name.exists():
                raise FileNotFoundError(f"The data file {file_name} does not exist.")
            if file_name.suffix.lower() == ".csv":

                # read CSV file
                if verbose or debug:
                    self.console.print(
                        f"{MSG.INFO}Reading CSV file: {file_name}"
                    )
                df = pd.read_csv(file_name, sep=",", header=0)
                self.hk = HK(df)
            elif file_name.suffix.lower() in [".qub", ".dat"]:
                if channel in ["stc", "hric"]:
                    filter = getValue(imaging[i], "img:filter_name")
                    self.filters.append(filter.lower())
                    setattr(self, f"filter_{filter.lower()}", SimbioObject(file_name,filter_name=filter,channel=channel,imaging=imaging[i],geometry=geometry[i],file_obs=file_obs[i],console=self.console,debug=debug,verbose=verbose   ))

                    if debug:
                        self.console.print(
                            f"{MSG.DEBUG}Found filter: {filter}"
                        )
                    pass
                else:
                    self.seg_number +=1
                    self.segments.append(f"segment_{self.seg_number:03}")
                    setattr(self, f"segment_{self.seg_number:03}", SimbioObject(file_name,channel=channel,imaging=imaging[i],geometry=geometry[i],file_obs=file_obs[i],console=self.console,debug=debug,verbose=verbose   ))
                    pass
    
    def savePreview(self,img_type:str='png',quality:int=100, outFolder:Path=None,tree:Document=None)->str|None:
        if self.channel == 'vihi':
            seg_prevs=[]
            for item in self.segments:
                disp=getattr(self,f'{item}')
                seg_prevs.append(disp.savePreview(img_type=img_type,quality=quality,outFolder=outFolder,tree=tree) )
            return seg_prevs
        else:
            filter_prevs=[]
            for item in self.filters:
                disp=getattr(self,f'filter_{item.lower()}')
                filter_prevs.append(disp.savePreview(img_type=img_type,quality=quality,outFolder=outFolder,tree=tree) )
            return filter_prevs


    def __str__(self):
        return f"Data(channel={self.channel}, level={self.level}, items_number={self.items_number})"

    def __repr__(self):
        return self.__str__()


class SimbioReader:
    def __init__(
        self, file_path: Path, debug: bool = False, verbose: bool = False, console=None, updateCheck: bool = True
    ):
        # Initialize the SimbioReader with a file path and optional console for output
        self.pdsLabel: Path = None
        self.debug=debug
        if console is None:
            self.console = Console()
        else:
            self.console = console
        if updateCheck:
            checker = UpdateChecker()
            result = checker.check('SimbioReader', version.short())
            if result:
                # TODO: Check this part after the delivery on pypi.org
                self.console.print(result)

        if debug:
            self.console.print(
                f"{MSG.DEBUG}Initializing SimbioReader with file path: {file_path}"
            )
        # Check the filename extension
        if isinstance(file_path, str):
            file_path = Path(file_path)
            
        self.pdsLabel = self.label_name(file_path)

        # check if the file exists
        if debug:
            self.console.print(
                f"{MSG.DEBUG}Checking if file exists: {self.pdsLabel}"
            )
        if self.pdsLabel is None or not self.pdsLabel.exists():
            # self.console.print(f"[red]Error:[/red] The file {self.pdsLabel} does not exist.")
            raise FileNotFoundError(f"The file {self.pdsLabel} does not exist.")

        if verbose or debug:
            self.console.print(
                f"{MSG.INFO}Reading PDS label file: {self.pdsLabel}"
            )
        label = parse(self.pdsLabel.as_posix())
        self.channel = getValue(label, "psa:identifier").lower()
        if self.channel not in ["stc", "hric", "vihi"]:
            raise ValueError(f"Unknown channel '{self.channel}' found in label.")
        self.level = getValue(label, "processing_level").lower()
        self.lid = getValue(label, "logical_identifier")
        self.version = getValue(label, "version_id")
        self.title = getValue(label, "title")
        self.dataModelVersion = getValue(label, "information_model_version")
        mission_phase=getElement(label,"psa:Mission_Phase")
        self.phaseName = getValue(mission_phase, 'psa:name')
        if debug:
            self.console.print(
                f"{MSG.DEBUG}Initialized SimbioReader with channel: {self.title}, version: {self.level}, Datamodel: {self.dataModelVersion}"
            )

        # Observation Time

        obsArea = getElement(label, "Observation_Area")
        timeCoords = getElement(obsArea, "Time_Coordinates")
        self.startTime = parser.parse(getValue(timeCoords, "start_date_time"),ignoretz=True)
        self.stopTime = parser.parse(getValue(timeCoords, "stop_date_time"),ignoretz=True)

        self.start_scet = getValue(label, "psa:spacecraft_clock_start_count")
        self.stop_scet = getValue(label, "psa:spacecraft_clock_start_count")
        if debug:
            self.console.print(
                f"{MSG.DEBUG}Observation start time: {self.startTime}, stop time: {self.stopTime}"
            )
            self.console.print(
                f"{MSG.DEBUG}Spacecraft clock start count: {self.start_scet}, stop count: {self.stop_scet}"
            )

        # Target Information
        targetInfo = getElement(obsArea, "Target_Identification")
        self.target = Target(
            name=getValue(targetInfo, "name"), target_type=getValue(targetInfo, "type")
        )

        if debug:
            self.console.print(f"{MSG.DEBUG}Target information: {self.target}")

        # Read the channels data
        self.data = Data(
            channel=self.channel,
            level=self.level,
            source_path=self.pdsLabel.parent,
            file_obs=label.getElementsByTagName("File_Area_Observational"),
            imaging=label.getElementsByTagName("img:Imaging"),
            geometry=label.getElementsByTagName("geom:Geometry"),
            debug=debug,
            verbose=verbose,
            console=self.console,
        )

    @property
    def lvid(self) -> str:
        """Returns the LIDVID of the SIMBIO-SYS file.

        Returns:
            str: The LIDVID of the SIMBIO-SYS file.
        """

        return f"{self.lid}::{self.version}"

    def label_name(self, file_path: Path) -> None:
        if file_path.is_dir():
            lst = list(file_path.glob("*.lblx"))
            if len(lst) == 0:
                # self.console.print(f"[red]Error:[/red] No .lblx files found in directory {file_path}.")
                raise FileNotFoundError(
                    f"No .lblx files found in directory {file_path}."
                )
            elif len(lst) > 1:
                # self.console.print(f"[red]Error:[/red] Multiple .lblx files found in directory {file_path}. Please specify a single file.")
                raise FileExistsError(
                    f"Multiple .lblx files found in directory {file_path}. Please specify a single file."
                )
            else:
                return lst[0]
        elif file_path.is_file():
            if not file_path.suffix == ".lblx":
                if self.debug:
                    self.console.print(
                        f"{MSG.WARNING}The file {file_path} does not have a .lblx extension."
                    )
                if "_cal_" in file_path.stem:

                    parts = file_path.stem.split("_")
                    if len(parts) == 12:
                        pdsLabel = f"{('_').join(parts[:-4])}__{'_'.join(parts[-2:])}.lblx"
                    else:
                        pdsLabel = f"{('_').join(parts[:-5])}__{'_'.join(parts[-2:])}.lblx"
                    return file_path.parent.joinpath(pdsLabel)
                else:
                    if file_path.with_suffix('.lblx').exists():
                        return file_path.with_suffix('.lblx')
            else:
                return file_path

    def __str__(self) -> str:
        return f"SimbioReader(channel={self.channel}, level={self.level}, lid={self.lid}, version={self.version})"

    def __repr__(self) -> str:
        return self.__str__()

    def show(self) -> Panel:
        dt = Table.grid()
        dt.add_column(style="yellow", justify="right")
        dt.add_column()
        dt.add_column(style="cyan", justify="left")

        sep = " = "
        dt.add_row("Channel", sep, self.channel.upper())
        dt.add_row("Processing Level", sep, self.level)
        dt.add_row("Mission Phase", sep, self.phaseName)
        dt.add_row("Logical Identifier", sep, self.lid)
        dt.add_row("Version", sep, self.version)
        dt.add_row("Title", sep, self.title)
        dt.add_row("Data Model Version", sep, self.dataModelVersion)
        dt.add_row("Observation Start Time", sep, self.startTime.isoformat())
        dt.add_row("Observation Stop Time", sep, self.stopTime.isoformat())
        dt.add_row("Spacecraft Clock Start Count", sep, self.start_scet)
        dt.add_row("Spacecraft Clock Stop Count", sep, self.stop_scet)

        return Panel(dt, title="SimbioReader Info", border_style="green", expand=False)

    def summary(self) -> Panel:
        filters=[]
        for item in self.data.filters:
            disp=getattr(self.data,f'filter_{item.lower()}')
            filters.append(disp.show())
        col = Columns(
            [self.show(), self.target.show(), self.data.hk.show(),*filters], expand=True
        )

        return Panel(
            col, title=f"SimbioReader Summary: {self.pdsLabel.stem}", border_style="green", expand=False
        )
    

    
    def __getattr__(self, name:str):
        if name.startswith('segment') and self.channel in ['stc','hric']:
            self.console.print(f"{MSG.ERROR}Attribute [blue]{name}[/blue] not available. The current Channel id is {self.channel.upper()}.")
        elif name.startswith('segment') and self.channel == 'vihi':
            self.console.print(f"{MSG.ERROR}Segment {name} not available.")
        elif name.startswith('filter') and self.channel == 'vihi':
            self.console.print(f"{MSG.ERROR}Attribute [blue]{name}[/blue] not available. The current Channel id is {self.channel.upper()}.") 

        return None
    
    def get_filter_by_file(self,file_name:Path)->SimbioObject|None:
        if isinstance(file_name,str):
            file_name=Path(file_name)
        for item in self.data.filters:
            disp=getattr(self.data,f'filter_{item.lower()}')
            if disp.file_name.name == file_name.name:
                return disp
        return None
    
    def get_segment_by_file(self,file_name:Path)->SimbioObject|None:
        if isinstance(file_name,str):
            file_name=Path(file_name)
        for item in self.data.segments:
            disp=getattr(self.data,f'{item}')
            if disp.file_name.name == file_name.name:
                return disp
        return None



        
    def savePreview(self,img_type:str='png',quality:int=100, outFolder:Path=None, template:Path=None, description:str = "This is the first version.")->str|None:
        """Saves a preview image of the loaded data.

        Args:
            img_type: The desired image format. Supported formats are 'png', 'tif', and 'jpg'. Defaults to 'png'.
            quality: The quality of the saved image (applicable for 'png' and 'jpg' formats only). Ranges from 0 (worst) to 100 (best). Defaults to 100.
            out_folder: The output folder path where the preview image will be saved. Defaults to the same directory as the original Simbio file.
            template: name of the PDS4 template that will be generated. If None no template will be written. If the template is not none the img_type
                    is forced to png

        Raises:
            ValueError: If the provided image format is not supported.
            TypeError: If the `out_folder` argument is not a `Path` object.
        """
        if self.debug:
            self.console.print(
                f"{MSG.DEBUG}Saving preview image with type: {img_type}, for {self.pdsLabel.name}"
            )
        if template:
            img_type = 'png'
        if outFolder is None:
            dest = self.pdsLabel.parent
        else:
            if type(outFolder) is not Path:
                outFolder = Path(outFolder)
            dest=outFolder
            if dest.exists() is False:
                dest.mkdir(parents=True, exist_ok=True)
        # ret=self.data.savePreview(img_type=img_type,quality=quality,outFolder=dest)
        if 'vihi' in self.channel:
            self.console.print('VIHI')
        if template:
            if not isinstance(template,Path):
                    template = Path(template)
            if not template.exists():
                raise FileNotFoundError(f"The template {template.name} was not found")
            new_filename=gen_filename(self.pdsLabel)
            new_label=dest.joinpath(new_filename).with_suffix(".lblx")
            # template.rename(new_label)
            # from xml.dom.minidom import parse, parseString, Element
            tree = parse(template.as_posix())
            for item in tree.getElementsByTagName("File_Area_Browse"):
                item.parentNode.removeChild(item)
            
            if 'cal' in Path(new_filename).stem:
                calib=True
            else:
                calib=False
            new_lid=lidUpdate(tree, new_label,calib=calib)
            creatTime=datetime.now()
            updateXML(tree, "modification_date", creatTime.strftime("%Y-%m-%d"), idx=0)
            file_version=new_filename.split('__')[1].split('.')[0]
            file_version=file_version.replace('_','.')
            updateXML(tree,"version_id",file_version, idx=0)
            updateXML(tree,"version_id",file_version, idx=1)
            updateXML(tree,"description",description, idx=0)
            lvidUpdate(tree,new_label, file_version)
            ret=self.data.savePreview(img_type=img_type,quality=quality,outFolder=dest, tree=tree)
            br=getElement(tree,"Product_Browse")
            for item in ret:
                br.appendChild(item)
       
            dom2 = parseString(pretty_print(tree))
            with open(new_label, "w") as xmlFile:
                dom2.writexml(xmlFile, encoding="utf-8")
            return f"{new_lid}::{file_version}"
        else:
            ret=self.data.savePreview(img_type=img_type,quality=quality,outFolder=dest)
    
    def image(self)->im:
        """Returns a PIL Image object representing the loaded image data.

        This method returns a Pillow (PIL Fork) Image object containing the image data
        loaded from the Simbio file. The image data is assumed to be a single-band
        or multi-band array, depending on the channel type.

        Returns:
            A PIL Image object representing the loaded image data.

        Raises:
            ValueError: If the loaded image data cannot be converted to a PIL Image
            object due to unsupported data type or shape.
        """
        data = im.fromarray(self.img)
        return data

