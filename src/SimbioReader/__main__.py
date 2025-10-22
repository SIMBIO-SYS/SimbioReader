import copy
import logging
from datetime import datetime
from os import path
from pathlib import Path
from xml.dom.minidom import Element, parse
from shutil import copyfile

import numpy as np
import pandas as pd
import rich_click as click
from PIL import Image as im
from rich import print
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich_click import rich_config
from update_checker import UpdateChecker

from SimbioReader.constants import (CONTEXT_SETTINGS, FMODE, MSG, data_types,
                                    datamodel, progEpilog)
from SimbioReader.exceptions import SizeError
from SimbioReader.filters_tools import Filter
from SimbioReader.tools import (getElement, getValue, snake_case,gen_filename, lidUpdate, updateXML, lvidUpdate, pretty_print)
from SimbioReader.version import version

# from functools import wraps

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.FOOTER_TEXT = progEpilog




__version__ = version.full()

    
def hdr_readr(file_name:Path):
    with open(file_name, FMODE.READ) as f:
        lines = f.readlines()
    img_data = {}
    info = ['samples', 'lines', 'bands', 'data type', 'Integration Time',
            'Compression Box', 'IBR', 'Start pixel row',
            'Start pixel col', 'Stop pixel row', 'Stop pixel col',
            'Binning W1']
    for line in lines:
        sect = line.split('=')
        if sect[0].strip() in info:

            if sect[0].strip() == 'Integration Time':
                img_data[snake_case(sect[0].strip())] = float(sect[-1].strip())
            elif sect[0].strip() == 'Compression Box':
                img_data[snake_case(sect[0].strip())] = sect[-1].strip()
            elif sect[0].strip() == 'data type':
                img_data[snake_case(sect[0].strip())] = int(sect[-1].strip())
            else:
                img_data[sect[0].strip()] = int(sect[-1].split('(')[0].strip())
    return img_data


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
    
    def __init__(self,df:pd.DataFrame):
        """
        Initializes the HK object by extracting information from the DataFrame.

        Args:
            df (pd.DataFrame): A pandas DataFrame containing housekeeping data.
        """
        self.df=df
        for i in df.columns:
            if type(df[i].values[0]) is str:
                val = df[i].values[0].strip()
            else:
                val = df[i].values[0]
            setattr(self, i.strip().lower(), val)
            
    def Show(self) -> Panel:
        """
        Displays the housekeeping information in a formatted table.

        Returns:
            Panel: A Panel object containing the formatted housekeeping information.
        """
        sep=' = '
        dt=Table.grid()
        dt.add_column(style='yellow',justify='right')
        dt.add_column()
        dt.add_column(style='cyan',justify='left')
        for i in self.df.columns:
            dt.add_row(' '.join(i.split('_')).title(),sep,f"{self.df[i].values[0]}".strip())
        return Panel(dt,title='HouseKeeping',border_style='yellow',expand=False)
    
    def __str__(self)->str:
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
        detector = getElement(dat, 'img:Detector')
        self.first_line = int(getValue(detector,'img:first_line'))
        self.first_sample = int(getValue(detector,'img:first_sample'))
        self.lines = int(getValue(detector,'img:lines'))
    
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
    
    def Show(self)-> Panel:
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
        return Panel(dt,title='Detector',border_style='yellow',expand=False)
    
class SubFrame:
    """
    A class representing a subframe of a SIMBIO-SYS image.

    This class extracts and initializes various attributes related to a subframe
    of a SIMBIO-SYS image, such as the first line, first sample, number of lines,
    number of samples, and field of view.

    Args:
        dat (Element): An XML Element containing the subframe information.

    Attributes:
        first_line (int): The first line number of the subframe.
        first_sample (int): The first sample number of the subframe.
        lines (int): The number of lines in the subframe.
        samples (int): The number of samples in the subframe.
        line_fov (float): The line field of view of the subframe.
        sample_fov (float): The sample field of view of the subframe.
    """
    def __init__(self, dat:Element) -> None:
        subFrame = getElement(dat, 'img:Subframe')
        self.first_line = int(getValue(subFrame,'img:first_line'))
        self.first_sample = int(getValue(subFrame,'img:first_sample'))
        self.lines = int(getValue(subFrame,'img:lines'))
        self.samples = int(getValue(subFrame,'img:samples'))
        self.line_fov = float(getValue(subFrame,'img:line_fov'))
        self.sample_fov = float(getValue(subFrame,'img:sample_fov'))
    
    def __str__(self):
        """
        Returns a string representation of the Subframe object.

        Returns:
            str: A string in the format 'SubFrame object'.
        """
        return f"SubFrame object"
    
    def __repr__(self) -> str:
        """
        Returns a string representation for debugging purposes.

        Returns:
            str: A string in the format 'SubFrame object'.
        """
        return self.__str__()
    

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
        fao=getElement(dat,'File_Area_Observational')
        fl=getElement(fao,'File')
        self.creation_time = datetime.strptime(getValue(fl,'creation_date_time'),"%Y-%m-%d")
        self.file_size = int(getValue(fl,'file_size'))
        self.md5 = getValue(fl,'md5_checksum')
        self.axes = int(getValue(fao,'axes'))
        self.band= None
        if self.axes == 3 and channel != 'VIHI':
            raise ValueError("The number of axes is wrong for the channel")
        for i in range(self.axes):
            axis = getElement(fao,'Axis_Array',i)
            setattr(self,getValue(axis,'axis_name').lower(),int(getValue(axis,'elements')))
        if self.axes == 3:
            dat=getElement(fao,'Array_3D_Spectrum')
        elif self.axes == 2:
            dat=getElement(fao,'Array_2D_Image')
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
    
    def Show(self):
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
        

class SimbioReader:
    """
        SimbioReader class for reading and processing SIMBIO-SYS data files.

        This class provides methods to read SIMBIO-SYS data files (STC, HRIC, VIHI channels),
        extract metadata, and access image data. It also offers functionalities
        for displaying information and saving image previews.

        Args:
            fileName (Path): Path to the Simbio data file.
            log (logging.Logger, optional): Logging object for recording messages. Defaults to None.
            debug (bool, optional): Flag to enable debug messages. Defaults to False.
            verbose (bool, optional): Flag to enable verbose messages. Defaults to False.
            console (Console, optional): Console object for printing messages. Defaults to None.
            updateCheck (bool, optional): Flag to check for updates on class initialization. Defaults to True.

        Attributes:
            fileName (Path): Path to the Simbio data file.
            log (logging.Logger, optional): Logging object for recording messages. Defaults to None.
            debug (bool, optional): Flag to enable debug messages. Defaults to False.
            verbose (bool, optional): Flag to enable verbose messages. Defaults to False.
            console (Console, optional): Console object for printing messages. Defaults to None.
            updateCheck (bool, optional): Flag to check for updates on class initialization. Defaults to True.
            channel (str): Channel type of the Simbio data (STC, HRIC, VIHI).
            pdsLabel (Path, optional): Path to the PDS4 label file.
            hk (HK, optional): Instance of the HK class containing housekeeping data (if available).
            title (str): Title of the Simbio data acquisition.
            dataModelVersion (str): Data model version of the Simbio data.
            startTime (datetime): Start time of the Simbio data acquisition.
            stopTime (datetime): Stop time of the Simbio data acquisition.
            level (str): Processing level of the Simbio data.
            tarName (str): Name of the target observed in the Simbio data.
            tarType (str): Type of the target observed in the Simbio data.
            startScet (str): Start spacecraft clock count of the Simbio data acquisition.
            stopScet (str): Stop spacecraft clock count of the Simbio data acquisition.
            phaseName (str): Mission phase name associated with the Simbio data acquisition.
            exposure (float): Exposure duration of the Simbio data acquisition (in seconds).
            firstLine (int): First line number of the image data.
            firstSample (int): First sample number of the image data.
            lines (int): Number of lines in the image data.
            samples (int): Number of samples in the image data.
            lineFov (float): Line field of view of the image data (in units).
            sampleFov (float): Sample field of view of the image data (in units).
            filter (Filter, optional): Instance of the Filter class containing filter information (if applicable).
            data_structure (DataStructure): Instance of the DataStructure class containing information about the data structure.
            img (np.ndarray): NumPy array containing the image data.
        """
    

    def __init__(self, fileName: Path, log: logging = None, 
                 debug: bool = False, verbose: bool = False,
                 console:Console=None, updateCheck:bool = True):

        if console is None:
            # from rich.console import Console
            self.console=Console()
        else:
            self.console=console
        if updateCheck:
            checker = UpdateChecker()
            result = checker.check('SimbioReader', version.short())
            if result:
                # TODO: Check this part after the delivery on pypi.org
                self.console.print(result)
                
        self._dateformat = "%Y-%m-%dT%H:%M:%S.%fZ"
        if not isinstance(fileName, Path):
            fileName = Path(fileName).resolve()
        if 'stc' in fileName.stem:
            self.channel = "STC"
        elif 'hric' in fileName.stem:
            self.channel = "HRIC"
        elif 'vihi' in fileName.stem:
            self.channel = "VIHI"
        else:
            raise ValueError('The file is not a Simbio file')
        
        self.fileName = fileName.absolute()
        self.log = log
        self.debug = debug
        self.verbose = verbose
        if self.fileName.suffix in ['.dat','.qub']:
            if self.fileName.with_suffix('.lblx').exists():
                self.pdsLabel=self.fileName.with_suffix('.lblx')
            else:
                raise ValueError("The PDS4 label is not present. it's impossible read the data file")
        if self.fileName.suffix == '.qub' and self.channel != 'VIHI':
            raise ValueError("The file is not a Simbio file or the filename is not well formatted")
        if self.fileName.suffix == '.lblx':
            if self.fileName.with_suffix('.dat').exists():
                self.pdsLabel=copy.copy(self.fileName)
                self.fileName=self.fileName.with_suffix('.dat')
            elif self.fileName.with_suffix('.qub').exists():
                self.pdsLabel=copy.copy(self.fileName)
                self.fileName=self.fileName.with_suffix('.qub')
            else:
                raise ValueError("The PDS4 data file is not present. it's impossible read the data file")
        
        self.read()

    def read(self):
        """Reads and processes the SIMBIO-SYS file, extracting metadata and image data.

        Raises:
            ValueError: If the file is not a valid SIMBIO-SYS file, PDS4 label is missing,
                        or data file is not found.
            SizeError: If the computed file size based on image data and data type
                        does not match the actual file size.
        """
        message = f"Reading {self.fileName}"
        if self.log:
            self.log.info(message)
        if self.verbose:
            self.console.print(f"{MSG.INFO}{message}")
                
        # Check the existence of the ausiliary files        
        if not self.fileName.with_suffix('.csv').exists():
            message = f"The HK file do not exists"
            if self.log:
                self.log.warning(message)
            if self.verbose:
                self.console.print(f"{MSG.WARNING}{message}")
        else:
            if self.verbose:
                self.console.print(f"{MSG.INFO}Read the HK from the csv")
            df = pd.read_csv(self.fileName.with_suffix('.csv'), sep=',', header=0)
            self.hk = HK(df)
            
        doc= parse(self.pdsLabel.as_posix())
        idArea = getElement(doc, 'Identification_Area')
        self.title = getValue(idArea, 'title')
        self.dataModelVersion = getValue(idArea, 'information_model_version')
        self.version =getValue(idArea, 'version_id')
        self.lid = getValue(idArea, 'logical_identifier')
        # TODO: Check on the datamodel version
        
        obsArea = getElement(doc, 'Observation_Area')
        timeCoords = getElement(obsArea, 'Time_Coordinates')
        self.startTime = datetime.strptime(getValue(timeCoords, 'start_date_time'),self._dateformat)
        self.stopTime = datetime.strptime(getValue(timeCoords, 'stop_date_time'),self._dateformat)
        
        primResSum = getElement(obsArea, 'Primary_Result_Summary')
        self.level = getValue(primResSum, 'processing_level')
        
        targetInfo = getElement(obsArea, 'Target_Identification')
        self.tarName = getValue(targetInfo, 'name')
        self.tarType = getValue(targetInfo, 'type')
        
        missionArea = getElement(doc, 'Mission_Area')
        missionInfo = getElement(missionArea, 'psa:Mission_Information')
        self.startScet = getValue(missionInfo, 'psa:spacecraft_clock_start_count')
        self.stopScet = getValue(missionInfo, 'psa:spacecraft_clock_stop_count')
        mission_phase=getElement(doc,"psa:Mission_Phase")
        self.phaseName = getValue(
            mission_phase, 'psa:name')
        
        discArea = getElement(doc, 'Discipline_Area')
        
        expInfo = getElement(discArea, 'img:Exposure')
        self.exposure = float(getValue(expInfo, 'img:exposure_duration'))/1000.
        
        subFrame = getElement(discArea, 'img:Subframe')
        self.firstLine = int(getValue(subFrame, 'img:first_line'))
        self.firstSample = int(getValue(subFrame, 'img:first_sample'))
        self.lines = int(getValue(subFrame, 'img:lines'))
        self.samples = int(getValue(subFrame, 'img:samples'))
        self.lineFov = float(getValue(subFrame, 'img:line_fov'))
        self.sampleFov = float(getValue(subFrame, 'img:sample_fov'))
        
        if self.channel != 'VIHI':
            flt = getElement(discArea, 'img:Optical_Filter')
            self.filter=Filter(channel=self.channel,name=getValue(flt,'img:filter_name'))
        
        
        self.data_stucture = DataStructure(doc, self.channel)
        self.samples=self.data_stucture.sample
        self.lines=self.data_stucture.line
        self.bands=self.data_stucture.band
        
        self.detector = Detector(doc)
        
        if self.data_stucture.data_type == "UnsignedLSB2":
            dtype = np.int16
        elif self.data_stucture.data_type == "IEEE754LSBSingle":
            dtype = np.float32

        if self.verbose:
            self.console.print(f"{MSG.INFO}Loading: {self.fileName}")
            if self.data_stucture.axes == 3:
                self.console.print(f"{MSG.INFO}Image size: {self.samples}x{self.lines}x{self.bands}")
                imgSize = self.samples*self.lines*self.bands*data_types[self.data_stucture.data_type]['bits']
            else:
                self.console.print(f"{MSG.INFO}Image size: {self.samples}x{self.lines}")
                imgSize = self.samples*self.lines*data_types[self.data_stucture.data_type]['bits']
            
            self.console.print(f"{MSG.INFO}File size: {self.fileName.stat().st_size*8}")
            self.console.print(
                f"{MSG.INFO}Computed File Size: {imgSize}")
            if self.fileName.stat().st_size*8 != imgSize:
                raise SizeError(self.fileName.stat().st_size *
                                8,imgSize)
        #print(img_data['samples'],img_data['lines'],img_data['bands'])
        if self.data_stucture.axes == 3:
            self.img = np.fromfile(self.fileName, dtype=dtype,
                               count=self.samples*self.lines*self.bands)
        else:
            self.img = np.fromfile(self.fileName, dtype=dtype,
                                   count=self.samples*self.lines)
        if self.data_stucture.axes == 3: 
            if self.lines==1:
                self.img.shape = ( self.samples,self.bands)
            else:
                self.img.shape = (self.lines,self.samples, self.bands )
        else:
            self.img.shape = (self.samples, self.lines)
        if self.verbose:
            self.console.print(f"{MSG.INFO}Dimension of the old image array: {self.img.ndim}")
            # print(f"Size of the old image array: {self.img.size}")

    @property
    def lvid(self)->str:
        """Returns the LIDVID of the SIMBIO-SYS file.

        Returns:
            str: The LIDVID of the SIMBIO-SYS file.
        """
    
        return f"{self.lid}::{self.version}"

    def Show(self, hk:bool=False, detector:bool=False, data_structure:bool=False, all_info:bool=False)->Columns:
        """Displays information about the loaded SIMBIO-SYS file.

        Args:
            hk (bool, optional): If True, displays the housekeeping data. Defaults to False.
            detector (bool, optional): If True, displays the detector information. Defaults to False.
            data_structure (bool, optional): If True, displays the data structure information. Defaults to False.
            all_info (bool, optional): If True, displays all available information (equivalent to setting
                                        hk, detector, and data_structure to True). Defaults to False.

        Returns:
            Columns: A rich console object containing the formatted information tables.
        """
        sep=' = '
        sep2 = ' : '
        if all_info:
            hk=True
            detector=True
            data_structure=True
        
        info=Table.grid()
        info.add_column(style='yellow', justify='right')
        info.add_column()
        info.add_column(style='cyan', justify='left')
        info.add_row('Title',sep2,self.title)
        info.add_row('DataModel Version', sep2, self.dataModelVersion)
        info.add_row('Start Acquisition', sep2, datetime.strftime(self.startTime,self._dateformat))
        info.add_row('Stop Acquisition', sep2, datetime.strftime(self.stopTime, self._dateformat))
        info.add_row('Start Acquisition SCET',sep2, self.startScet)
        info.add_row("Stop Acquisition SCET", sep2, self.stopScet)
        info.add_row("Phase Name", sep2, self.phaseName)
        
        infoT=Table.grid()
        infoT.add_column()
        infoT.add_row(Panel(info,title='General Info',border_style='yellow',expand=False))
        
        g=Table.grid()
        g.add_column()
        g.add_row(Panel(Text(self.channel, justify='center', style='magenta'), border_style='yellow', title="Channel"))
        g.add_row(Panel(Text(self.level.upper(), justify='center',
                  style='magenta'), border_style='yellow', title="Level"))
        
        tbs=Table.grid()
        tbs.add_column(style='yellow',justify='right')
        tbs.add_column()
        tbs.add_column(style='cyan',justify='left')
        tbs.add_row('Samples',sep,str(self.samples))
        tbs.add_row('Lines',sep,str(self.lines))
        if self.channel == 'VIHI':
            tbs.add_row('Bands',sep,str(self.bands))
        tbs.add_section()
        tbs.add_row("First Line", sep, str(self.firstLine))
        tbs.add_row("First Sample", sep, str(self.firstSample))
        tbs.add_row('Line FOV',sep, str(self.lineFov))
        tbs.add_row('Sample FOV', sep, str(self.sampleFov))
        
        # g.add_row(Panel(tbs, title='Image Info',
        #           border_style='yellow', expand=True))
        
        t=Table.grid()
        t.add_column(style='yellow', justify='right')
        t.add_column()
        t.add_column(style='cyan', justify='left')
        t.add_row("Name",sep2,self.tarName)
        t.add_row("Type", sep2, self.tarType)
        
        g.add_row(Panel(t, title='Target Info',
                  border_style='yellow'))
        
        g.add_row(Panel(tbs, title='Image Info',
                  border_style='yellow', expand=True))
        
 

        # phk=Panel(hk,title='HouseKeeping',border_style='yellow',expand=False)
        show_list = [g, infoT]
        if hk :
            show_list.append(self.hk.Show())
        
        if detector:
            g.add_row(self.detector.Show())
            
        if data_structure:
            infoT.add_row(self.data_stucture.Show())
            
        if self.channel != 'VIHI':
            
            infoT.add_row(self.filter.show())
   
        return Columns(show_list, title=self.fileName.stem)
        pass

    def __str__(self)-> str:
        """
        Returns a string representation of the object.

        Returns:
            str: A string in the format 'SimbioReader object <version> - from file <fileName>'.
        """
        return f"SimbioReader object {version} - from file {self.fileName.stem}"
    
    def __repr__(self) -> str:
        """
        Returns a string representation for debugging purposes.

        Returns:
            str: A string in the format 'SimbioReader object <version> - from file <fileName>'.
        """
        return self.__str__()
 

        
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
        if template:
            img_type = 'png'
        if outFolder is None:
            dest = self.fileName.parent
        else:
            if type(outFolder) is not Path:
                outFolder = Path(outFolder)
            dest=outFolder
        if img_type in ['png','tif']:
            data = im.fromarray(self.img)
            # print(data.getpixel((50, 50)))
            new_filename=gen_filename(self.fileName)
            # data_filename=self.fileName.stem
            # new_filename=copy.copy(data_filename)
            # if 'raw' in data_filename:
            #     new_filename.replace('raw','browse_raw')
            image_file= f"{dest}/{new_filename}.{img_type}"
            if 'cal' in self.fileName.stem:
                data.convert('RGB').save(image_file, quality=quality)
            else:
                data.save(image_file, quality=quality)
            if template:
                if not isinstance(template,Path):
                    template = Path(template)
                if not template.exists():
                    raise FileNotFoundError(f"The template {template.name} was not found")
                new_label=f"{dest}/{new_filename}.lblx"
                template.rename(new_label)
                from xml.dom.minidom import parse, parseString, Element
                import hashlib
                tree = parse(new_label)
                if 'cal' in self.fileName.stem:
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
                lvidUpdate(tree,self.fileName, file_version)
                image_file= Path(image_file)
                updateXML(tree, 'file_name', image_file.name, idx=0)
                updateXML(tree, 'creation_date_time',
                    creatTime.strftime("%Y-%m-%d"), idx=0)
                updateXML(tree, 'file_size', image_file.stat().st_size, idx=0)
                updateXML(tree, 'md5_checksum', hashlib.md5(
                    open(image_file, 'rb').read()).hexdigest(), idx=0)
                dom2 = parseString(pretty_print(tree))
                with open(new_label, "w") as xmlFile:
                    dom2.writexml(xmlFile, encoding="utf-8")
                return f"{new_lid}::{file_version}"
        elif img_type == 'jpg':
            data = im.fromarray(self.img,mode='L')
            # print(data.getpixel((50,50)))
            data.save(f"{dest}/{self.fileName.stem}.{img_type}",
                      quality=quality)
        # print(self.img[0,0])
        pass
    
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
    console.print(dat.Show(hk=hk, detector=detector,
                  data_structure=data_structure, all_info=all_info))
    







# def common_options_sub(func):
#     """Common options for the commands"""
#     @wraps(func)
#     @click.option('-a', '--all', is_flag=True, help='Show all the phases', default=False)
#     @click.option('-d', '--date', type=str, help='Show the phase for the given date', default=None)
#     @click.option('-n', '--name', type=str, help='Show the phase for the given name', default=None)
#     def wrapper(*args, **kwargs):
#         return func(*args, **kwargs)
#     return wrapper

# @cli.command()
# @common_options_sub
# def phases(all:bool,date:str, name:str):
#     """Display required phase(s)"""
#     from SimbioReader.phases_tools import get_phase, Phase
#     console = Console()
#     if not date and not name:
#         all=True
#     if all:
#         console.print(Phase.show())
#     elif date:
#         console.print(get_phase(dt=date).show())
#     elif name:
#         console.print(get_phase(name=name).show())
        

# @cli.command()
# @common_options_sub
# def subphases(all: bool, date: str, name: str):
#     """Display required subphase(s)"""
#     from SimbioReader.phases_tools import get_subphase, SubPhase
#     console = Console()
#     if not date and not name:
#         all = True
#     if all:
#         console.print(SubPhase.show())
#     elif date:
#         console.print(get_subphase(dt=date).show())
#     elif name:
#         console.print(get_subphase(name=name).show())
        

# @cli.command()
# @click.option('-a', '--all', is_flag=True, help='Show all the phases', default=False)
# @click.option('-d', '--date', type=str, help='Show the phase for the given date', default=None)
# @click.option('-n', '--name', type=str, help='Show the phase for the given name', default=None)
# @click.option('-p', '--phase', type=str, help='Show the tests for the given phase', default=None)
# @click.option('-s', '--subphase', type=str, help='Show the tests for the given subphase', default=None)
# def test(all: bool=None, date: str=None, name: str=None,phase:str=None,subphase:str=None):
#     """Display required test(s)"""
#     from SimbioReader.phases_tools import Test
#     console = Console()
#     if not date and not name and not phase and not subphase:
#         all = True
#     if all:
#         console.print(Test.show_all())
#     elif date:
#         console.print(Test.show_all(date=date))
#     elif name:
#         # console.print(Test.show(key=name))
#         console.print(Test(name,subphase=subphase).show())
#     elif phase:
#         console.print(Test.show_all(phase=phase))
#     elif subphase:
#         console.print(Test.show_all(subphase=subphase))
        
# @cli.command("filters")
# @click.argument('channel', required=True)
# def filters_act(channel:str):
#     """Display the filters for the given channel"""
#     from SimbioReader.filters_tools import show_filters
#     console = Console()
#     console.print(show_filters(channel))
    
    

if __name__ == "__main__":
    cli()