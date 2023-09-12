import logging
from dataclasses import dataclass
from os import path
from pathlib import Path



import numpy as np
import pandas as pd
from PIL import Image as im
from rich import print

from bin.SimbioReader.exceptions import SizeError
from xml.dom.minidom import parse
from re import sub
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text


def camel_case(s):
    s = sub(r"(_|-)+", " ", s).title().replace(" ", "")
    return ''.join([s[0].lower(), s[1:]])


def snake_case(s):
    return '_'.join(
        sub('([A-Z][a-z]+)', r' \1',
        sub('([A-Z]+)', r' \1',
        s.replace('-', ' '))).split()).lower()


class MSG:
    ERROR = "[red][ERROR][/red] "
    CRITICAL = "[red][CRITICAL][/red] "
    INFO = "[green][INFO][/green] "
    DEBUG = "[blue][DEBUG][/blue] "
    WARNING = "[yellow][WARNING][/yellow] "
    
class FMODE:
    READ = 'r'
    READ_BINARY = 'rb'
    WRITE = 'w'
    WRITE_BINARY = 'wb'
    APPEND = 'a'
    
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


@dataclass
class SimbioReader:
    ''' Read a Simbio file'''
    

    def __init__(self, fileName: Path, log: logging = None, 
                 debug: bool = False, verbose: bool = False,xml: bool=False):
        if type(fileName) is not Path:
            fileName = Path(fileName)
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
                    f"The file {self.fileName.stem} does not exist")
        if self.log:
            self.log.info(f"Reading {self.fileName}")
        # 
        if xml:
            if not path.exists(f"{self.fileName.parent}/{self.fileName.stem}.xml"):
                raise ValueError(
                    f"The file {self.fileName.stem}.{e} does not exist")
            img_data =xmlReader(self.fileName.with_suffix('.xml'),self.channel)
        else:
            if not path.exists(f"{self.fileName.parent}/{self.fileName.stem}.hdr"):
                raise ValueError(
                    f"The file {self.fileName.stem}{e} does not exist")
            img_data = hdr_readr(self.fileName.with_suffix('.hdr'))
        self.samples=img_data['samples']
        self.lines=img_data['lines']
        if self.channel == "VIHI":
            self.bands=img_data['bands']
        else:
            self.bands=1
        # f"{self.fileName.parent}/{self.fileName.stem}.hdr")
        df = pd.read_csv(self.fileName.with_suffix('.csv'), sep=',', header=0)
        # f"{self.fileName.parent}/{self.fileName.stem.replace('img','hk')}.csv", sep=',', header=0)
        for i in df.columns:
            if type(df[i].values[0]) is str:
                val=df[i].values[0].strip() 
            else:
                val=df[i].values[0]
            setattr(self, i.strip(), val)
        # self.scetConvert()
        if img_data['data_type'] == 2:
            data_type = np.int16
        if img_data['data_type'] == 5:
            data_type=np.float64
        for elemn in img_data.keys():
            setattr(self, elemn, img_data[elemn])
        if self.verbose:
            print(f"{MSG.INFO}Loading: {self.fileName}")
            if self.channel == 'VIHI':
                imgSize = img_data['samples']*img_data['lines']*img_data['bands']*16
                print(
                    f"{MSG.INFO}Image size: {img_data['samples']}x{img_data['lines']}x{img_data['bands']}")
            else:
                imgSize = img_data['samples'] * img_data['lines']*16
                print(
                    f"{MSG.INFO}Image size: {img_data['samples']}x{img_data['lines']}")
            print(f"{MSG.INFO}File size: {self.fileName.stat().st_size*8}")
            print(
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
            print(f"{MSG.INFO}Dimension of the old image array: {self.img.ndim}")
            # print(f"Size of the old image array: {self.img.size}")

    def Show(self):
        # print(self.__dict__)
        sep=' = '
        g=Table.grid()
        g.add_column()
        g.add_row(Panel(Text(self.channel,justify='center', style='magenta'),border_style='yellow',title="Channel"))
        tbs=Table.grid()
        tbs.add_column(style='yellow',justify='right')
        tbs.add_column()
        tbs.add_column(style='cyan',justify='left')
        tbs.add_row('samples',sep,str(self.samples))
        tbs.add_row('lines',sep,str(self.lines))
        tbs.add_row('bands',sep,str(self.bands))
        ps=Panel(tbs,title='image info',border_style='yellow',expand=False)
        g.add_row(ps)
        hk=Table.grid()
        hk.add_column(style='yellow', justify='right')
        hk.add_column()
        hk.add_column(style='cyan', justify='left')
        df = pd.read_csv(self.fileName.with_suffix('.csv'), sep=',', header=0)
        for i in df.columns:
            hk.add_row(i.strip(), sep, f"{df[i].values[0]}".strip())
        phk=Panel(hk,title='HouseKeeping',border_style='yellow',expand=False)
        
        print(Columns([g,phk], title=self.fileName.stem))
        pass

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
