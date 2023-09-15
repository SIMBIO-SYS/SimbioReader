import logging
from dataclasses import dataclass
from os import path
from pathlib import Path
from re import sub
from xml.dom.minidom import parse

import numpy as np
import pandas as pd
from PIL import Image as im
from rich import print
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from update_checker import UpdateChecker

from SimbioReader.constants import FMODE, MSG
from SimbioReader.exceptions import SizeError
from SimbioReader.tools import getElement, getValue
from SimbioReader.version import version


def camel_case(s):
    s = sub(r"(_|-)+", " ", s).title().replace(" ", "")
    return ''.join([s[0].lower(), s[1:]])


def snake_case(s):
    return '_'.join(
        sub('([A-Z][a-z]+)', r' \1',
        sub('([A-Z]+)', r' \1',
        s.replace('-', ' '))).split()).lower()


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

def xmlReader(file_name:Path,channel:str):
    tree=parse(file_name.__str__())
    
    img_data = {}
    
    
    img_data["Integration_Time"] = float(tree.getElementsByTagName(
        "img:exposure_duration")[0].firstChild.data)/1000
    elem = tree.getElementsByTagName('Axis_Array')
    for item in elem:
        # print(item.getElementsByTagName('axis_name')
            #   [0].firstChild.data.lower())
        img_data[item.getElementsByTagName('axis_name')[0].firstChild.data.lower()+'s'] = \
            int(item.getElementsByTagName('elements')[0].firstChild.data)
    img_data['start_pixel_row'] = int(
        tree.getElementsByTagName('img:first_line')[0].firstChild.data)
    img_data['start_pixel_col'] = int(
        tree.getElementsByTagName('img:first_sample')[0].firstChild.data)
    # img_data['lines']=int(elem[0].firstChild.data)
    # img_data['samples']=int(elem[1].firstChild.data)
    
    # img_data['bands']=1
    dataType=tree.getElementsByTagName('data_type')[0].firstChild.data
    if dataType == 'UnsignedMSB2':
        img_data['data_type'] = 2
    elif dataType == 'IEEE754MSBDouble':
        img_data['data_type'] = 5
    # manca:
    #  - il dato della compressione
    #  - il dato dell'IBR
    #  - il dato della dimensione delle bande
    #  - il dato dello stop pixel row
    #  - il dato dello stop pixel col
    #  - il dato del binning W1
    #  - il dato del binning spettrale
    return img_data


# @dataclass
class SimbioReader:
    ''' Read a Simbio file'''
    

    def __init__(self, fileName: Path, log: logging = None, 
                 debug: bool = False, verbose: bool = False,
                 xml: bool=False, console:Console=None, updateCheck:bool = True):
        if console is None:
            from SimbioReader.console import console
            self.console=console
        else:
            self.console=console
        if updateCheck:
            checker = UpdateChecker()
            result = checker.check('SimbioReader', version.short())
            if result:
                # TODO: Check this part after the delivery on pypi.org
                self.console.print(result)
        if type(fileName) is not Path:
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
        self.read(xml)

    def read(self,xml:bool):
        ext = ['.dat', '.xml']
        for e in ext:
            if not self.fileName.with_suffix(e).exists():
                raise ValueError(
                    f"The file {self.fileName.stem} does not exist ({self.fileName.with_suffix(e)})")
        message = f"Reading {self.fileName}"
        if self.log:
            self.log.info(message)
        if self.verbose:
            self.console.print(f"{MSG.INFO}{message}")
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
            # f"{self.fileName.parent}/{self.fileName.stem.replace('img','hk')}.csv", sep=',', header=0)
            for i in df.columns:
                if type(df[i].values[0]) is str:
                    val = df[i].values[0].strip()
                else:
                    val = df[i].values[0]
                setattr(self, i.strip(), val)
            
        # 
        # if xml:
            # if not path.exists(f"{self.fileName.parent}/{self.fileName.stem}.xml"):
            #     raise ValueError(
            #         f"The file {self.fileName.stem}.{e} does not exist")
        img_data =xmlReader(self.fileName.with_suffix('.xml'),self.channel)
        doc = parse(self.fileName.with_suffix('.xml').__str__())
        idArea = getElement(doc, 'Identification_Area')
        self.title = getValue(idArea, 'title')
        self.dataModelVersion = getValue(idArea, 'information_model_version')
        # TODO: Check on the datamodel version
        
        obsArea = getElement(doc, 'Observation_Area')
        timeCoords = getElement(obsArea, 'Time_Coordinates')
        self.startTime = getValue(timeCoords, 'start_date_time')
        self.stopTime = getValue(timeCoords, 'stop_date_time')
        
        primResSum = getElement(obsArea, 'Primary_Result_Summary')
        self.level = getValue(primResSum, 'processing_level')
        
        targetInfo = getElement(obsArea, 'Target_Identification')
        self.tarName = getValue(targetInfo, 'name')
        self.tarType = getValue(targetInfo, 'type')
        
        missionArea = getElement(doc, 'Mission_Area')
        missionInfo = getElement(missionArea, 'psa:Mission_Information')
        self.startScet = getValue(
            missionInfo, 'psa:spacecraft_clock_start_count')
        self.stopScet = getValue(
            missionInfo, 'psa:spacecraft_clock_stop_count')
        self.phaseName = getValue(
            missionInfo, 'psa:mission_phase_name')
        
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
        
        
        # else:
        #     if not path.exists(f"{self.fileName.parent}/{self.fileName.stem}.hdr"):
        #         raise ValueError(
        #             f"The file {self.fileName.stem}{e} does not exist")
        #     img_data = hdr_readr(self.fileName.with_suffix('.hdr'))
        # self.samples=img_data['samples']
        # self.lines=img_data['lines']
        if self.channel == "VIHI":
            axis = getElement(doc, 'Array_3D_Spectrum')
            db = getElement(axis, 'Axis_Array',2)
            # self.bands=img_data['bands']
            self.bands = int(getValue(axis,'elements'))
        else:
            self.bands=1
        # f"{self.fileName.parent}/{self.fileName.stem}.hdr")
        
        # self.scetConvert()
        if img_data['data_type'] == 2:
            data_type = np.int16
        if img_data['data_type'] == 5:
            data_type=np.float64
        for elemn in img_data.keys():
            setattr(self, elemn, img_data[elemn])
        if self.verbose:
            self.console.print(f"{MSG.INFO}Loading: {self.fileName}")
            if self.channel == 'VIHI':
                imgSize = img_data['samples']*img_data['lines']*img_data['bands']*16
                self.console.print(
                    f"{MSG.INFO}Image size: {img_data['samples']}x{img_data['lines']}x{img_data['bands']}")
            else:
                imgSize = img_data['samples'] * img_data['lines']*16
                self.console.print(
                    f"{MSG.INFO}Image size: {img_data['samples']}x{img_data['lines']}")
            self.console.print(f"{MSG.INFO}File size: {self.fileName.stat().st_size*8}")
            self.console.print(
                f"{MSG.INFO}Computed File Size: {imgSize}")
            if self.fileName.stat().st_size*8 != imgSize:
                raise SizeError(self.fileName.stat().st_size *
                                8,imgSize)
        #print(img_data['samples'],img_data['lines'],img_data['bands'])
        if self.channel == "VIHI":
            self.img = np.fromfile(self.fileName, dtype=data_type,
                               count=img_data['samples']*img_data['lines']*img_data['bands'])
        else:
            self.img = np.fromfile(self.fileName, dtype=data_type,
                                   count=img_data['samples']*img_data['lines'])
        if self.channel == 'VIHI': 
            if self.lines==1:
                self.img.shape = ( self.samples,self.bands)
            else:
                self.img.shape = (self.samples, self.bands, self.lines)
        else:
            self.img.shape = (self.samples, self.lines)
        if self.verbose:
            self.console.print(f"{MSG.INFO}Dimension of the old image array: {self.img.ndim}")
            # print(f"Size of the old image array: {self.img.size}")

    def Show(self,prt=True):
        # print(self.__dict__)
        sep=' = '
        sep2 = ' : '
        
        info=Table.grid()
        info.add_column(style='yellow', justify='right')
        info.add_column()
        info.add_column(style='cyan', justify='left')
        info.add_row('Title',sep2,self.title)
        info.add_row('DataModel Version', sep2, self.dataModelVersion)
        info.add_row('Start Acquisition', sep2, self.startTime)
        info.add_row('Stop Acquisition', sep2, self.stopTime)
        info.add_row('Stort Acquisition SCET',sep2, self.startScet)
        info.add_row("Stop Acquisition SCET", sep2, self.stopScet)
        info.add_row("Phase Name", sep2, self.phaseName)
        
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
        
        hk=Table.grid()
        hk.add_column(style='yellow', justify='right')
        hk.add_column()
        hk.add_column(style='cyan', justify='left')
        df = pd.read_csv(self.fileName.with_suffix('.csv'), sep=',', header=0)
        for i in df.columns:
            hk.add_row(i.strip(), sep, f"{df[i].values[0]}".strip())
        infoP = Panel(info, title="General Info",
                      border_style='yellow', expand=False)
        phk=Panel(hk,title='HouseKeeping',border_style='yellow',expand=False)
        if prt:
            self.console.print(Columns([g, infoP, phk], title=self.fileName.stem))
        else:
            return Columns([g, infoP,  phk], title=self.fileName.stem)
        pass

    def __str__(self):
        return f"SimbioReader object {version} - from file {self.fileName.stem}"
    # def scetConvert(self):
    #     temp = divmod(self.ACQUISITION_TIME_SCET, 1)
    #     self.ACQUISITION_TIME_SCET = f"1/{int(temp[0])}:{int(temp[1]*2**16)}"
        
    def savePreview(self,img_type:str='png',quality:int=100, outFolder:Path=None):
  
        if outFolder is None:
            dest = self.fileName.parent
        else:
            if type(outFolder) is not Path:
                outFolder = Path(outFolder)
            dest=outFolder
        if img_type in ['png','tif']:
            data = im.fromarray(self.img)
            # print(data.getpixel((50, 50)))
            data.save(f"{dest}/{self.fileName.stem}.{img_type}",
                      quality=quality)
        elif img_type == 'jpg':
            data = im.fromarray(self.img,mode='L')
            # print(data.getpixel((50,50)))
            data.save(f"{dest}/{self.fileName.stem}.{img_type}",
                      quality=quality)
        # print(self.img[0,0])
        pass
    
    def image(self):
        data = im.fromarray(self.img)
        return data
