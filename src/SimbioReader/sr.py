import hashlib
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

# from SimbioReader.version import version
from importlib.metadata import version as get_version
from pathlib import Path
from xml.dom.minidom import Document, Element, parse, parseString

import numpy as np
import pandas as pd
import pds4_tools
from dateutil import parser
from loguru import logger
from lxml import etree
from mystrtools import convert_case
from pds4_tools.reader.array_objects import ArrayStructure
from pds4_tools.reader.table_objects import TableStructure
from PIL import Image as im
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from semantic_version_tools import Vers

from SimbioReader.constants import MSG, data_types
from SimbioReader.exceptions import LoadingError, SizeError
from SimbioReader.filters_tools import Filter
from SimbioReader.tools import (
    gen_filename,
    getElement,
    getValue,
    lidUpdate,
    lvidUpdate,
    pretty_print,
    updateXML,
)
from SimbioReader.version_check import check_pypi_version

installed_version = get_version("SimbioReader")
version = Vers(installed_version)

__version__ = version.full()


class INSTRUMENT(StrEnum):
    STC = "STC"
    HRIC = "HRIC"
    VIHI = "VIHI"


instruments: list[INSTRUMENT] = [
    INSTRUMENT.STC,
    INSTRUMENT.VIHI,
    INSTRUMENT.HRIC,
]

# ============= To Check =====================


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

    def __init__(self, dat: Element) -> None:
        detector = getElement(dat, "img:Subframe")
        self.first_line = int(getValue(detector, "img:first_line"))
        self.first_sample = int(getValue(detector, "img:first_sample"))
        self.lines = int(getValue(detector, "img:lines"))
        self.samples = int(getValue(detector, "img:samples"))
        self.line_fov = float(getValue(detector, "img:line_fov"))
        self.sample_fov = float(getValue(detector, "img:sample_fov"))

    def __str__(self) -> str:
        """
        Returns a string representation of the Detector object.

        Returns:
            str: A string representation of the Detector object.
        """
        return "Detector object"

    def __repr__(self) -> str:
        """
        Returns a string representation of the Detector object for debugging.

        Returns:
            str: A string representation of the Detector object.
        """
        return self.__str__()

    def show(self, title="Detector") -> Panel:
        """
        Displays the detector information in a formatted table.

        Returns:
            Panel: A Panel object containing the formatted detector information.
        """
        sep = " = "
        dt = Table.grid()
        dt.add_column(style="yellow", justify="right")
        dt.add_column()
        dt.add_column(style="cyan", justify="left")
        dt.add_row("First Line", sep, str(self.first_line))
        dt.add_row("First Sample", sep, str(self.first_sample))
        dt.add_row("Lines", sep, str(self.lines))
        dt.add_row("Samples", sep, str(self.samples))
        dt.add_row("Line FOV", sep, str(self.line_fov))
        dt.add_row("Sample FOV", sep, str(self.sample_fov))
        return Panel(dt, title=title, border_style="yellow", expand=False)


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
                convert_case(i, "space").title(), sep, f"{self.df[i].values[0]}".strip()
            )
        return Panel(dt, title="HouseKeeping", border_style="yellow", expand=False)

    def __str__(self) -> str:
        """
        Returns a string representation of the HK object.

        Returns:
            str: A string representation of the HK object.
        """
        return "HK object"

    def __repr__(self) -> str:
        """
        Returns a string representation of the HK object for debugging.

        Returns:
            str: A string representation of the HK object.
        """
        return self.__str__()


# ================================

# TODO: Implemnt informatio after the improve of the target information
# Class used in 1.0


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


# ==============================================================


class SimbioObject:
    def __init__(
        self,
        file_name: str,
        channel: str,
        imaging: Element,
        geometry: Element,
        file_obs: Element,
        filter_name: Path | str | None = None,
        console: Console | None = None,
        debug: bool = False,
        verbose: bool = False,
    ):
        # Set the console
        self.console = console if console else Console()

        self.file_name = Path(file_name)
        self.filter_name = filter_name
        self.channel = channel
        self.imaging = imaging
        self.geometry = geometry
        self.debug = debug
        self.exposure_time = getValue(imaging, "img:exposure_duration")
        subFrame = getElement(imaging, "img:Subframe")
        self.firstLine = int(getValue(subFrame, "img:first_line"))
        self.firstSample = int(getValue(subFrame, "img:first_sample"))
        self.lines = int(getValue(subFrame, "img:lines"))
        self.samples = int(getValue(subFrame, "img:samples"))
        self.lineFov = float(getValue(subFrame, "img:line_fov"))
        self.sampleFov = float(getValue(subFrame, "img:sample_fov"))
        self.data_structure = DataStructure(file_obs, self.channel)
        self.samples = self.data_structure.sample
        self.lines = self.data_structure.line
        self.bands = self.data_structure.band
        if self.channel.upper() != "VIHI":
            flt = getElement(imaging, "img:Optical_Filter")
            self.filter = Filter(
                channel=self.channel, name=getValue(flt, "img:filter_name")
            )
        self.detector = Detector(imaging)
        if self.data_structure.data_type == "UnsignedLSB2":
            dtype = np.int16
        elif self.data_structure.data_type == "IEEE754LSBSingle":
            dtype = np.float32

        if verbose:
            console.print(f"{MSG.INFO}Loading: {self.file_name}")
            if self.data_structure.axes == 3:
                console.print(
                    f"{MSG.INFO}Image size: {self.samples}x{self.lines}x{self.bands}"
                )
                imgSize = (
                    self.samples
                    * self.lines
                    * self.bands
                    * data_types[self.data_structure.data_type]["bits"]
                )
            else:
                console.print(f"{MSG.INFO}Image size: {self.samples}x{self.lines}")
                imgSize = (
                    self.samples
                    * self.lines
                    * data_types[self.data_structure.data_type]["bits"]
                )

            console.print(f"{MSG.INFO}File size: {self.file_name.stat().st_size * 8}")
            console.print(f"{MSG.INFO}Computed File Size: {imgSize}")
            if self.file_name.stat().st_size * 8 != imgSize:
                raise SizeError(self.file_name.stat().st_size * 8, imgSize)
        # print(img_data['samples'],img_data['lines'],img_data['bands'])
        if self.data_structure.axes == 3:
            self.img = np.fromfile(
                self.file_name,
                dtype=dtype,
                count=self.samples * self.lines * self.bands,
            )
        else:
            self.img = np.fromfile(
                self.file_name, dtype=dtype, count=self.samples * self.lines
            )
        if self.data_structure.axes == 3:
            if self.lines == 1:
                self.img.shape = (self.samples, self.bands)
            else:
                self.img.shape = (self.lines, self.samples, self.bands)
        else:
            self.img.shape = (self.samples, self.lines)
        if verbose:
            self.console.print(
                f"{MSG.INFO}Dimension of the old image array: {self.img.ndim}"
            )
            # print(f"Size of the old image array: {self.img.size}")

    def show(self) -> Panel:
        sep = " =  "
        tb = Table.grid()
        tb.add_column(style="yellow", justify="right")
        tb.add_column()
        tb.add_column()
        tb.add_row("File Name", sep, str(self.file_name))
        tb.add_row("Filter Name", sep, self.filter_name)
        tb.add_row("Channel", sep, self.channel.upper())
        tb.add_row("Exposure Time (s)", sep, str(self.exposure_time))
        pl = Panel(
            tb, title="Simbio Filter General Info", border_style="cyan", expand=False
        )
        return Panel(
            Columns(
                [
                    pl,
                    self.filter.show(),
                    self.data_structure.show(),
                    self.detector.show(),
                ]
            ),
            title=f"Filter {self.filter_name.upper()} Info",
            border_style="magenta",
            expand=False,
        )

    def __str__(self):
        return f"Filter(name={self.filter_name})"

    def __repr__(self):
        return self.__str__()

    def savePreview(
        self,
        img_type: str = "png",
        quality: int = 100,
        outFolder: Path = None,
        tree: Document = None,
    ) -> str | None:
        new_filename = gen_filename(self.file_name)
        if img_type in ["png", "tif"]:
            data = im.fromarray(self.img)
            image_file = f"{outFolder}/{new_filename}.{img_type}"
            if self.debug:
                self.console.print(
                    f"{MSG.DEBUG}Saving image {Path(image_file).name} with quality {quality}"
                )
            if "cal" in self.file_name.stem:
                data.convert("RGB").save(image_file, quality=quality)
            else:
                data.save(image_file, quality=quality)
            if tree:
                fab = tree.createElement("File_Area_Browse")
                fl = tree.createElement("File")
                fln = tree.createElement("file_name")
                fln.appendChild(tree.createTextNode(f"{new_filename}.{img_type}"))
                fl.appendChild(fln)
                fl_ct = tree.createElement("creation_date_time")
                creatTime = datetime.now()
                fl_ct.appendChild(tree.createTextNode(creatTime.strftime("%Y-%m-%d")))
                fl.appendChild(fl_ct)
                fl_fs = tree.createElement("file_size")
                fl_fs.appendChild(
                    tree.createTextNode(str(Path(image_file).stat().st_size))
                )
                fl_fs.setAttribute("unit", "byte")
                fl.appendChild(fl_fs)
                fl_md5 = tree.createElement("md5_checksum")
                fl_md5.appendChild(
                    tree.createTextNode(
                        hashlib.md5(open(image_file, "rb").read()).hexdigest()
                    )
                )
                fl.appendChild(fl_md5)
                fab.appendChild(fl)

                enc_img = tree.createElement("Encoded_Image")
                enc_offset = tree.createElement("offset")
                enc_offset.appendChild(tree.createTextNode("0"))
                enc_offset.setAttribute("unit", "byte")
                enc_stid = tree.createElement("encoding_standard_id")
                enc_stid.appendChild(tree.createTextNode("PNG"))
                enc_img.appendChild(enc_offset)
                enc_img.appendChild(enc_stid)

                fab.appendChild(enc_img)
                return fab
        elif img_type == "jpg":
            data = im.fromarray(self.img, mode="L")
            # print(data.getpixel((50,50)))
            data.save(f"{outFolder}/{new_filename}.{img_type}", quality=quality)
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
        if self.channel == "vihi":
            self.segments = []
            self.seg_number = 0
        else:
            self.filters = []

        self.items_number = len(file_obs)

        self.level = level
        for i, fo in enumerate(file_obs):
            file_name = source_path.joinpath(getValue(fo, "file_name"))
            if verbose or debug:
                self.console.print(
                    f"{MSG.INFO}Processing file {i + 1}/{self.items_number}: {file_name.name}"
                )
            if not file_name.exists():
                raise FileNotFoundError(f"The data file {file_name} does not exist.")
            if file_name.suffix.lower() == ".csv":
                # read CSV file
                if verbose or debug:
                    self.console.print(f"{MSG.INFO}Reading CSV file: {file_name}")
                df = pd.read_csv(file_name, sep=",", header=0)
                self.hk = HK(df)
            elif file_name.suffix.lower() in [".qub", ".dat"]:
                if channel in ["stc", "hric"]:
                    filter = getValue(imaging[i], "img:filter_name")
                    self.filters.append(filter.lower())
                    setattr(
                        self,
                        f"filter_{filter.lower()}",
                        SimbioObject(
                            file_name,
                            filter_name=filter,
                            channel=channel,
                            imaging=imaging[i],
                            geometry=geometry[i],
                            file_obs=file_obs[i],
                            console=self.console,
                            debug=debug,
                            verbose=verbose,
                        ),
                    )

                    if debug:
                        self.console.print(f"{MSG.DEBUG}Found filter: {filter}")
                    pass
                else:
                    self.seg_number += 1
                    self.segments.append(f"segment_{self.seg_number:03}")
                    setattr(
                        self,
                        f"segment_{self.seg_number:03}",
                        SimbioObject(
                            file_name,
                            channel=channel,
                            imaging=imaging[i],
                            geometry=geometry[i],
                            file_obs=file_obs[i],
                            console=self.console,
                            debug=debug,
                            verbose=verbose,
                        ),
                    )
                    pass

    def savePreview(
        self,
        img_type: str = "png",
        quality: int = 100,
        outFolder: Path = None,
        tree: Document = None,
    ) -> str | None:
        if self.channel == "vihi":
            seg_prevs = []
            for item in self.segments:
                disp = getattr(self, f"{item}")
                seg_prevs.append(
                    disp.savePreview(
                        img_type=img_type,
                        quality=quality,
                        outFolder=outFolder,
                        tree=tree,
                    )
                )
            return seg_prevs
        else:
            filter_prevs = []
            for item in self.filters:
                disp = getattr(self, f"filter_{item.lower()}")
                filter_prevs.append(
                    disp.savePreview(
                        img_type=img_type,
                        quality=quality,
                        outFolder=outFolder,
                        tree=tree,
                    )
                )
            return filter_prevs

    def __str__(self):
        return f"Data(channel={self.channel}, level={self.level}, items_number={self.items_number})"

    def __repr__(self):
        return self.__str__()

@dataclass
class Compression:
    box:str
    rate:str
    ratio:str

@dataclass(slots=True, frozen=True)
class Simbio:
    channel: INSTRUMENT
    general_parameters: str
    compression: Compression | None = None
    
    _stc: str | None = None
    _vihi: str | None = None
    _hric: str | None = None

    def __post_init__(self) -> None:
        try:
            channel = INSTRUMENT(self.channel)
        except ValueError as exc:
            valid = ", ".join(instrument.value for instrument in INSTRUMENT)
            raise ValueError(
                f"Unknown instrument {self.channel!r}. Expected one of: {valid}."
            ) from exc

        object.__setattr__(self, "channel", channel)

        instrument_data = {
            INSTRUMENT.STC: self._stc,
            INSTRUMENT.HRIC: self._hric,
            INSTRUMENT.VIHI: self._vihi,
        }
        if instrument_data[channel] is None:
            raise ValueError(f"Data for instrument {channel.value} are required.")

        unexpected = [
            instrument.value
            for instrument, value in instrument_data.items()
            if instrument is not channel and value is not None
        ]
        if unexpected:
            names = ", ".join(unexpected)
            raise ValueError(
                f"Data for {names} cannot be provided when the instrument is "
                f"{channel.value}."
            )

    def _get_instrument_data(
        self,
        expected: INSTRUMENT,
        value: str | None,
    ) -> str:
        if self.channel is not expected:
            raise AttributeError(
                f"The {expected.value} data are not available. "
                f"The current instrument is {self.channel.value}."
            )
        assert value is not None
        return value

    @property
    def stc(self) -> str:
        return self._get_instrument_data(INSTRUMENT.STC, self._stc)

    @property
    def hric(self) -> str:
        return self._get_instrument_data(INSTRUMENT.HRIC, self._hric)

    @property
    def vihi(self) -> str:
        return self._get_instrument_data(INSTRUMENT.VIHI, self._vihi)



@dataclass
class TimeCoordinates:
    start_utc: datetime
    end_utc: datetime
    start_scet: str
    end_scet: str


@dataclass
class SoftwareContext:
    software_name: str
    version: str


@dataclass(slots=True, init=False, frozen=True)
class SimbioReader:
    console: Console
    # Data Files
    image_file: Path
    image_data: ArrayStructure
    lblx_file: Path
    csv_file: Path
    csv_data: TableStructure
    cube_file: Path
    cube_data: ArrayStructure

    # label values
    channel: INSTRUMENT
    title: str
    processing_level: str
    lid: str
    version_id: str
    information_model_version: str
    mission_phase: str

    time_coordinates: TimeCoordinates
    target: Target
    software_context: SoftwareContext
    simbio: Simbio

    debug: bool
    verbosity: int

    def __init__(
        self,
        file_path: Path,
        debug: bool = False,
        verbose: int = 0,
        console: Console | None = None,
        updateCheck: bool = True,
    ):
        logger.debug("Inizializing SimbioReader object")
        # Initialize the console
        object.__setattr__(self, "console", console if console else Console())

        # Set the debug and verbosity sttributes
        object.__setattr__(self, "debug", debug)
        object.__setattr__(self, "verbosity", verbose)

        # Initialize the SimbioReader with a file path and optional console for output

        if updateCheck:
            logger.debug("Check for updates on PyPi")
            result = check_pypi_version("SimbioReader", installed_version)
            if result and result.update_available:
                self.console.print(
                    f"{MSG.WARNING} Version {result.current} of SimbioReader is outdated. "
                    f"Version {result.latest} is available."
                )
            elif result and result.local_is_newer:
                self.console.print(
                    f"{MSG.INFO}Local version {result.current} of SimbioReader "
                    f"is newer than version {result.latest} available on PyPI.\n \t[yellow bold]This is a developing version [/]"
                )
        # Check the file existence
        file_path = Path(file_path)
        if not file_path.exists():
            message = f"The input file {file_path.name} does not exists"
            logger.critical(message)
            raise FileNotFoundError(message)

        # Check the input type
        if file_path.is_file():
            # Check the input file suffix
            match file_path.suffix:
                case ".lblx":
                    object.__setattr__(self, "lblx_file", file_path)
                case ".dat" | ".qub" | ".csv":
                    if file_path.with_suffix(".lblx").exists():
                        object.__setattr__(
                            self, "lblx_file", file_path.with_suffix(".lblx")
                        )
                    else:
                        message = f"No lblx file associated to {file_path.name}. Not valid PDS4 file"
                        logger.critical(message)
                        self.console.print(f"{MSG.CRITICAL}{message}")
                        raise ValueError(message)
                case _:
                    message = f"The {file_path.suffix} is not a valid suffix"
                    logger.critical(message)
                    self.console.print(f"{MSG.CRITICAL}{message}")
                    raise ValueError(message)
        elif file_path.is_dir():
            file_list = list(file_path.rglob("**/*.lblx"))
            match len(file_list):
                case 0:
                    message = (
                        "No lblx file found, not a valid PDS4 file found in the folder"
                    )
                    self.console.print(f"{MSG.CRITICAL}{message}")
                    logger.critical(message)
                    raise FileNotFoundError(message)
                case 1:
                    object.__setattr__(self, "lblx_file", file_list[0])
                case x if x > 1:
                    message = (
                        "Multiple lblx found in the folder. Please specify a lblx file"
                    )
                    self.console.print(f"{MSG.CRITICAL}{message}")
                    logger.critical(message)
                    raise ValueError(message)
            pass

        # Load the data
        try:
            data = pds4_tools.read(filename=str(self.lblx_file))
        except Exception as exc:
            message = f"Unable to read the PDS4 product: {exc}"
            raise LoadingError(self.lblx_file.name, message) from exc

        # Data summary
        message = f"Identified {len(data.structures)} in the product."
        logger.info(message)
        if self.verbosity > 0:
            self.console.print(f"{MSG.INFO}{message}")
        if self.verbosity > 1:
            for idx, item in enumerate(data.structures):
                self.console.print(f"\t{idx + 1}. {item.type}")

        # Initialize the dat/qub file and csv file
        for item in data.structures:
            match item.type:
                case "Table_Delimited":
                    object.__setattr__(self, "csv_file", Path(item.parent_filename))
                    message = f"Identified a CSV File ({self.csv_file.name})"
                    logger.info(message)
                    if self.verbosity > 1:
                        self.console.print(f"{MSG.INFO}{message}")
                    object.__setattr__(self, "csv_data", item)
                    pass
                case "Array_2D_Image":
                    object.__setattr__(self, "image_file", Path(item.parent_filename))
                    message = f"Identified a 2D Image File ({self.image_file.name})"
                    logger.info(message)
                    if self.verbosity > 1:
                        self.console.print(f"{MSG.INFO}{message}")
                    object.__setattr__(self, "image_data", item)
                case "Array_3D_Image":
                    object.__setattr__(self, "cube_file", Path(item.parent_filename))
                    message = f"Identified a 3D Image File ({self.image_file.name}) - VIHI Cube"
                    logger.info(message)
                    if self.verbosity > 1:
                        self.console.print(f"{MSG.INFO}{message}")
                    object.__setattr__(self, "cube_data", item)
                    pass
                case _:
                    pass

        # Read the lblx file to initialize the variables
        tree = etree.parse(self.lblx_file)
        root = tree.getroot()

        # Namespace definition
        namespaces = {
            "pds": root.nsmap[None],
            "psa": root.nsmap["psa"],
        }

        def set_value(xpath, attribute):
            item = root.xpath(f"string({xpath})", namespaces=namespaces)
            object.__setattr__(self, attribute, item)

        # Identication of the channel
        channel_name = (
            root.xpath(
                "string(./pds:Observation_Area/pds:Mission_Area/"
                "psa:Sub-Instrument/psa:identifier)",
                namespaces=namespaces,
            )
            .upper()
            .strip()
        )
        logger.debug(f"Identied the sub-instument name: {channel_name}")
        try:
            channel = INSTRUMENT(channel_name)
        except ValueError as exc:
            message = (
                f"The sub-Instrument {channel_name} is not a valid "
                "SIMBIO-SYS sub-instrument"
            )
            self.console.print(f"{MSG.CRITICAL}{message}")
            logger.critical(message)
            raise ValueError(message) from exc
        object.__setattr__(self, "channel", channel)

        # get Data Title
        set_value("./pds:Identification_Area/pds:title", "title")
        # get the processing level
        IDENTIFICATION_AREA = "/pds:Product_Observational[1]/pds:Identification_Area[1]"
        OBSERVATION_AREA = "/pds:Product_Observational[1]/pds:Observation_Area[1]"
        set_value(
            "/pds:Product_Observational[1]/pds:Observation_Area[1]/pds:Primary_Result_Summary[1]/pds:processing_level[1]",
            "processing_level",
        )
        set_value(f"{IDENTIFICATION_AREA}/pds:logical_identifier[1]", "lid")
        set_value(f"{IDENTIFICATION_AREA}/pds:version_id[1]", "version_id")
        set_value(
            f"{IDENTIFICATION_AREA}/pds:information_model_version[1]",
            "information_model_version",
        )
        set_value(
            f"{OBSERVATION_AREA}/pds:Mission_Area[1]/psa:Mission_Information[1]/psa:Mission_Phase[1]/psa:name[1]",
            "mission_phase",
        )
        if self.debug:
            message = f"Initialized SimbioReader with channel: {self.title}, version: {self.processing_level}, Datamodel: {self.information_model_version}"
            self.console.print(f"{MSG.DEBUG}{message}")
        logger.debug(message)

        # Time coordinates
        dateformat = "%Y-%m-%dT%H:%M:%S.%fZ"
        xpath = f"{OBSERVATION_AREA}/pds:Time_Coordinates[1]/pds:start_date_time[1]"
        start = datetime.strptime(
            root.xpath(f"string({xpath})", namespaces=namespaces), dateformat
        )
        xpath = f"{OBSERVATION_AREA}/pds:Time_Coordinates[1]/pds:stop_date_time[1]"
        end = datetime.strptime(
            root.xpath(f"string({xpath})", namespaces=namespaces), dateformat
        )
        xpath = f"{OBSERVATION_AREA}/pds:Mission_Area[1]/psa:Mission_Information[1]/psa:spacecraft_clock_start_count[1]"
        start_scet = root.xpath(f"string({xpath})", namespaces=namespaces)
        xpath = f"{OBSERVATION_AREA}/pds:Mission_Area[1]/psa:Mission_Information[1]/psa:spacecraft_clock_stop_count[1]"
        end_scet = root.xpath(f"string({xpath})", namespaces=namespaces)
        object.__setattr__(
            self, "time_coordinates", TimeCoordinates(start, end, start_scet, end_scet)
        )
        if self.verbosity > 1:
            message = f"Setted the time coordinates to {self.time_coordinates}"
            self.console.print(f"{MSG.DEBUG}{message}")
        logger.debug(message)

        # Target Information
        object.__setattr__(
            self,
            "target",
            Target(
                root.xpath(
                    f"string({OBSERVATION_AREA}/pds:Target_Identification[1]/pds:name[1])",
                    namespaces=namespaces,
                ),
                root.xpath(
                    f"string({OBSERVATION_AREA}/pds:Target_Identification[1]/pds:type[1])",
                    namespaces=namespaces,
                ),
            ),
        )
        if self.verbosity > 1:
            message = f"Setted the target to {self.target}"
            self.console.print(f"{MSG.DEBUG}{message}")
        logger.debug(message)

        # Software Context

        object.__setattr__(
            self,
            "software_context",
            SoftwareContext(
                root.xpath(
                    f"string({OBSERVATION_AREA}/pds:Mission_Area[1]/psa:Processing_Context[1]/psa:processing_software_title[1])",
                    namespaces=namespaces,
                ),
                root.xpath(
                    f"string({OBSERVATION_AREA}/pds:Mission_Area[1]/psa:Processing_Context[1]/psa:processing_software_version[1])",
                    namespaces=namespaces,
                ),
            ),
        )
        if self.verbosity > 1:
            message = f"Setted the Software Context to {self.software_context}"
            self.console.print(f"{MSG.DEBUG}{message}")
        logger.debug(message)

        last_row = "qui"
        return

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

        return f"{self.lid}::{self.version_id}"


    def show(
        self,
        hk: bool = False,
        detector: bool = False,
        data_structure: bool = False,
        filters: bool = False,
        all_info: bool = False,
    ) -> Panel:
        columns = [self.info(), self.target.show()]
        if hk or all_info:
            columns.append(self.data.hk.show())
        if detector or all_info:
            for item in self.data.filters:
                disp = getattr(self.data, f"filter_{item.lower()}")
                columns.append(
                    disp.detector.show(title=f"Detector Info - Filter {item.upper()}")
                )
        if data_structure or all_info:
            for item in self.data.filters:
                disp = getattr(self.data, f"filter_{item.lower()}")
                columns.append(
                    disp.data_structure.show(
                        title=f"Data Structure Info - Filter {item.upper()}"
                    )
                )

        if filters and hasattr(self.data, "filters"):
            for item in self.data.filters:
                disp = getattr(self.data, f"filter_{item.lower()}")
                columns.append(disp.show())
        col = Columns(
            columns,  # [self.info(), self.target.show(), self.filters_summary()],#, self.data.hk.show(), *filters],
            expand=True,
        )

        return Panel(
            col,
            title=f"SimbioReader Summary: {self.pdsLabel.stem}",
            border_style="green",
            expand=False,
        )

    def info(self) -> Panel:
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

    def filters_summary(self) -> Panel:
        tb = Table()
        tb.add_column("", style="yellow", justify="right")
        tb.add_column("Filter Names", style="yellow", justify="center")
        for item in self.data.filters:
            tb.add_row(":green_circle:", item.upper())
            # disp = getattr(self.data, f"filter_{item.lower()}")

        return Panel(
            tb,
            title="Filters Summary",
            border_style="green",
            expand=False,
        )

    def summary(self) -> Panel:
        filters = []
        for item in self.data.filters:
            disp = getattr(self.data, f"filter_{item.lower()}")
            filters.append(disp.show())
        col = Columns(
            [
                self.info(),
                self.target.show(),
                self.filters_summary(),
            ],  # , self.data.hk.show(), *filters],
            expand=True,
        )

        return Panel(
            col,
            title=f"SimbioReader Summary: {self.pdsLabel.stem}",
            border_style="green",
            expand=False,
        )

    def __getattr__(self, name: str):
        if name.startswith("segment") and self.channel in ["stc", "hric"]:
            self.console.print(
                f"{MSG.ERROR}Attribute [blue]{name}[/blue] not available. The current Channel id is {self.channel.upper()}."
            )
        elif name.startswith("segment") and self.channel == "vihi":
            self.console.print(f"{MSG.ERROR}Segment {name} not available.")
        elif name.startswith("filter") and self.channel == "vihi":
            self.console.print(
                f"{MSG.ERROR}Attribute [blue]{name}[/blue] not available. The current Channel id is {self.channel.upper()}."
            )

        return None

    def get_filter_by_file(self, file_name: Path) -> SimbioObject | None:
        if isinstance(file_name, str):
            file_name = Path(file_name)
        for item in self.data.filters:
            disp = getattr(self.data, f"filter_{item.lower()}")
            if disp.file_name.name == file_name.name:
                return disp
        return None

    def get_filters(self) -> list:
        filters = []
        for item in self.data.filters:
            disp = getattr(self.data, f"filter_{item.lower()}")
            filters.append(disp)
        return filters

    def get_segment_by_file(self, file_name: Path) -> SimbioObject | None:
        if isinstance(file_name, str):
            file_name = Path(file_name)
        for item in self.data.segments:
            disp = getattr(self.data, f"{item}")
            if disp.file_name.name == file_name.name:
                return disp
        return None

    def savePreview(
        self,
        img_type: str = "png",
        quality: int = 100,
        outFolder: Path = None,
        template: Path = None,
        description: str = "This is the first version.",
    ) -> str | None:
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
            img_type = "png"
        if outFolder is None:
            dest = self.pdsLabel.parent
        else:
            if type(outFolder) is not Path:
                outFolder = Path(outFolder)
            dest = outFolder
            if dest.exists() is False:
                dest.mkdir(parents=True, exist_ok=True)
        # ret=self.data.savePreview(img_type=img_type,quality=quality,outFolder=dest)
        if "vihi" in self.channel:
            self.console.print("VIHI")
        if template:
            if not isinstance(template, Path):
                template = Path(template)
            if not template.exists():
                raise FileNotFoundError(f"The template {template.name} was not found")
            new_filename = gen_filename(self.pdsLabel)
            new_label = dest.joinpath(new_filename).with_suffix(".lblx")
            # template.rename(new_label)
            # from xml.dom.minidom import parse, parseString, Element
            tree = parse(template.as_posix())
            for item in tree.getElementsByTagName("File_Area_Browse"):
                item.parentNode.removeChild(item)

            if "cal" in Path(new_filename).stem:
                calib = True
            else:
                calib = False
            new_lid = lidUpdate(tree, new_label, calib=calib)
            creatTime = datetime.now()
            updateXML(tree, "modification_date", creatTime.strftime("%Y-%m-%d"), idx=0)
            file_version = str(new_filename).split("__")[1].split(".")[0]
            file_version = file_version.replace("_", ".")
            updateXML(tree, "version_id", file_version, idx=0)
            updateXML(tree, "version_id", file_version, idx=1)
            updateXML(tree, "description", description, idx=0)
            lvidUpdate(tree, new_label, file_version)
            ret = self.data.savePreview(
                img_type=img_type, quality=quality, outFolder=dest, tree=tree
            )
            br = getElement(tree, "Product_Browse")
            for item in ret:
                br.appendChild(item)

            dom2 = parseString(pretty_print(tree))
            with open(new_label, "w") as xmlFile:
                dom2.writexml(xmlFile, encoding="utf-8")
            return f"{new_lid}::{file_version}"
        else:
            ret = self.data.savePreview(
                img_type=img_type, quality=quality, outFolder=dest
            )

    def image(self) -> im:
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

    def __str__(self) -> str:
        return f"SimbioReader(channel={self.channel}, level={self.level}, lid={self.lid}, version={self.version})"

    def __repr__(self) -> str:
        return self.__str__()
