from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime

# from SimbioReader.version import version
from importlib.metadata import version as get_version
from pathlib import Path
from xml.dom.minidom import Document, Element

import pandas as pd
import pds4_tools
from loguru import logger
from lxml import etree
from mystrtools import convert_case
from pds4_tools.reader.array_objects import ArrayStructure
from pds4_tools.reader.table_objects import TableStructure
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from semantic_version_tools import Vers

from SimbioReader.constants import MSG
from SimbioReader.exceptions import DeprecatedMethodError, LoadingError
from SimbioReader.simbio_classes import (
    INSTRUMENT,
    Compression,
    Display,
    Geometry,
    Hric,
    Imaging,
    Reference,
    Simbio,
    Stc,
    Vihi,
    instruments,  # noqa: F401 - compatibility re-export
)
from SimbioReader.tools import (
    getElement,
    getValue,
)
from SimbioReader.version_check import check_pypi_version

installed_version = get_version("SimbioReader")
version = Vers(installed_version)

__version__ = version.full()




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

                    if debug:
                        self.console.print(f"{MSG.DEBUG}Found filter: {filter}")
                else:
                    self.seg_number += 1
                    self.segments.append(f"segment_{self.seg_number:03}")

    def savePreview(
        self,
        img_type: str = "png",
        quality: int = 100,
        outFolder: Path = None,
        tree: Document = None,
    ) -> str | None:
        """Report that legacy preview generation is no longer supported.

        .. deprecated::
            This method is obsolete and retained temporarily for API
            compatibility. It must be removed in a future version.
        """
        message = (
            "Data.savePreview() is obsolete and will be removed "
            "in a future version of SimbioReader."
        )
        self.console.print(f"{MSG.WARNING}{message}")
        raise DeprecatedMethodError(message)

    def __str__(self):
        return f"Data(channel={self.channel}, level={self.level}, items_number={self.items_number})"

    def __repr__(self):
        return self.__str__()



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
    data_arrays: tuple[ArrayStructure, ...]
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
    display: Display
    imaging: Imaging
    geometry: Geometry
    reference: Reference

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
        data_arrays = []
        for item in data.structures:
            if item.type.startswith("Array_"):
                data_arrays.append(item)
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
        object.__setattr__(self, "data_arrays", tuple(data_arrays))

        # Read the lblx file to initialize the variables
        tree = etree.parse(self.lblx_file)
        root = tree.getroot()

        # Namespace definition
        namespaces = {
            "pds": root.nsmap[None],
            "psa": root.nsmap["psa"],
            "disp": root.nsmap["disp"],
            "img": root.nsmap["img"],
            "geom": root.nsmap["geom"],
            "bc_mpo_simbio-sys": root.nsmap["bc_mpo_simbio-sys"],
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

        # Setup SIMBIO_SYS General Parameters

        SIMBIO = (
            f"{OBSERVATION_AREA}/pds:Mission_Area[1]/"
            "bc_mpo_simbio-sys:SIMBIO[1]"
        )
        instrument_data = {}
        if self.channel == INSTRUMENT.STC:
            stc_elements = root.xpath(
                f"{SIMBIO}/bc_mpo_simbio-sys:STC[1]",
                namespaces=namespaces,
            )
            if not stc_elements:
                raise LoadingError(
                    self.pdsLabel,
                    "Missing STC metadata in the SIMBIO mission area",
            )
            instrument_data["_stc"] = Stc.from_xml(stc_elements[0], namespaces)
        elif self.channel == INSTRUMENT.HRIC:
            hric_elements = root.xpath(
                f"{SIMBIO}/bc_mpo_simbio-sys:HRIC[1]",
                namespaces=namespaces,
            )
            if not hric_elements:
                raise LoadingError(
                    self.pdsLabel,
                    "Missing HRIC metadata in the SIMBIO mission area",
                )
            instrument_data["_hric"] = Hric.from_xml(
                hric_elements[0],
                namespaces,
            )
        elif self.channel == INSTRUMENT.VIHI:
            vihi_elements = root.xpath(
                f"{SIMBIO}/bc_mpo_simbio-sys:VIHI[1]",
                namespaces=namespaces,
            )
            if not vihi_elements:
                raise LoadingError(
                    self.pdsLabel,
                    "Missing VIHI metadata in the SIMBIO mission area",
                )
            instrument_data["_vihi"] = Vihi.from_xml(
                vihi_elements[0],
                namespaces,
            )

        simbio = Simbio(channel=self.channel, **instrument_data)
        object.__setattr__(
            simbio,
            'compression',
            Compression(
                float(root.xpath(
                    f"string({SIMBIO}/bc_mpo_simbio-sys:SIMBIO_General_Parameters[1]/bc_mpo_simbio-sys:Compression[1]/bc_mpo_simbio-sys:compression_box[1])",
                    namespaces=namespaces,
                )),
                float(root.xpath(
                    f"string({SIMBIO}/bc_mpo_simbio-sys:SIMBIO_General_Parameters[1]/bc_mpo_simbio-sys:Compression[1]/bc_mpo_simbio-sys:compression_rate[1])",
                    namespaces=namespaces,
                )),
                int(root.xpath(
                    f"string({SIMBIO}/bc_mpo_simbio-sys:SIMBIO_General_Parameters[1]/bc_mpo_simbio-sys:Compression[1]/bc_mpo_simbio-sys:ibr[1])",
                    namespaces=namespaces,
                )))
        )

        if self.verbosity > 1:
            message = f"Setted the Compression information to {simbio.compression}"
            self.console.print(f"{MSG.DEBUG}{message}")
        logger.debug(message)
        object.__setattr__(simbio,
                           'repetition_time',
                           float(root.xpath(
                               f"string({SIMBIO}/bc_mpo_simbio-sys:SIMBIO_General_Parameters[1]/bc_mpo_simbio-sys:repetition_time[1])",
                               namespaces=namespaces,
                           )
                                      )
                                      )
        object.__setattr__(self,'simbio',simbio)

        discipline_area = f"{OBSERVATION_AREA}/pds:Discipline_Area[1]"
        discipline_models = (
            ("display", "disp:Display_Settings", Display),
            ("imaging", "img:Imaging", Imaging),
            ("geometry", "geom:Geometry", Geometry),
        )
        for attribute, element_name, model in discipline_models:
            elements = root.xpath(
                f"{discipline_area}/{element_name}[1]",
                namespaces=namespaces,
            )
            if not elements:
                raise LoadingError(
                    self.pdsLabel,
                    f"Missing {element_name} metadata in the discipline area",
                )
            object.__setattr__(
                self,
                attribute,
                model.from_xml(elements[0], namespaces),
            )

        reference_lists = root.xpath(
            "/pds:Product_Observational[1]/pds:Reference_List[1]",
            namespaces=namespaces,
        )
        if not reference_lists:
            raise LoadingError(
                self.pdsLabel,
                "Missing Reference_List metadata",
            )
        object.__setattr__(
            self,
            "reference",
            Reference.from_xml(reference_lists[0], namespaces),
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
        no_symbols: bool = False,
    ) -> Panel:
        """Return a Rich summary built from the current metadata models."""
        columns = [self.info(), self.target.show()]
        instrument = self._instrument_metadata()

        if hk:
            columns.extend(
                [
                    self._housekeeping_panel(
                        f"{self.channel.value} Housekeeping",
                        instrument.housekeeping,
                        use_symbols=not no_symbols,
                    ),
                    self._csv_data_panel(),
                ]
            )

        if detector:
            detector_models = [("Imaging Detector", self.imaging.detector)]
            general_parameters = getattr(
                instrument,
                "general_parameters",
                None,
            )
            instrument_detector = getattr(
                general_parameters,
                "detector",
                None,
            )
            if instrument_detector is not None:
                detector_models.insert(
                    0,
                    (
                        f"{self.channel.value} Detector",
                        instrument_detector,
                    ),
                )
            columns.extend(
                self._measurement_panel(
                    title,
                    model,
                    use_symbols=not no_symbols,
                )
                for title, model in detector_models
            )

        if all_info:
            columns.extend(
                [
                    self._model_panel(
                        "SIMBIO",
                        self.simbio,
                        use_symbols=not no_symbols,
                    ),
                    self._model_panel(
                        "Display",
                        self.display,
                        use_symbols=not no_symbols,
                    ),
                    self._model_panel(
                        "Imaging",
                        self.imaging,
                        use_symbols=not no_symbols,
                    ),
                    self._model_panel(
                        "Geometry",
                        self.geometry,
                        use_symbols=not no_symbols,
                        leaf_names=True,
                        two_columns=True,
                    ),
                    self._model_panel(
                        "References",
                        self.reference,
                        use_symbols=not no_symbols,
                    ),
                ]
            )
        else:
            if data_structure:
                columns.extend(
                    [
                        self._model_panel(
                            "Display",
                            self.display,
                            use_symbols=not no_symbols,
                        ),
                        self._model_panel(
                            "Imaging Subframe",
                            self.imaging.subframe,
                            use_symbols=not no_symbols,
                        ),
                        self._model_panel(
                            "Geometry",
                            self.geometry,
                            use_symbols=not no_symbols,
                            leaf_names=True,
                            two_columns=True,
                        ),
                    ]
                )
            if filters:
                columns.append(
                    self._model_panel(
                        "Optical Filter",
                        self.imaging.optical_filter,
                        use_symbols=not no_symbols,
                    )
                )
        col = Columns(
            columns,
            expand=True,
        )

        return Panel(
            col,
            title=f"SimbioReader Summary: {self.lblx_file.stem}",
            border_style="green",
            expand=False,
        )

    def _instrument_metadata(self) -> Stc | Hric | Vihi:
        match self.channel:
            case INSTRUMENT.STC:
                return self.simbio.stc
            case INSTRUMENT.HRIC:
                return self.simbio.hric
            case INSTRUMENT.VIHI:
                return self.simbio.vihi

    @staticmethod
    def _flatten_model(
        value,
        prefix: str = "",
        use_symbols: bool = True,
    ) -> list[tuple[str, str]]:
        if value is None:
            return [(prefix or "Value", "Not available")]
        if is_dataclass(value):
            rows = []
            model_fields = {field.name for field in fields(value)}
            unit_fields = SimbioReader._model_unit_fields(model_fields)
            unit_field_names = set(unit_fields.values())
            for field in fields(value):
                if field.name in unit_field_names:
                    continue
                label = f"{prefix}.{field.name}" if prefix else field.name
                field_value = getattr(value, field.name)
                unit_field = unit_fields.get(field.name)
                if unit_field:
                    unit = getattr(value, unit_field)
                    if unit and use_symbols:
                        unit = SimbioReader._unit_symbol(unit)
                    rows.append(
                        (
                            label,
                            f"{field_value} {unit}" if unit else str(field_value),
                        )
                    )
                    continue
                rows.extend(
                    SimbioReader._flatten_model(
                        field_value,
                        label,
                        use_symbols=use_symbols,
                    )
                )
            return rows
        if isinstance(value, (tuple, list)):
            if not value:
                return [(prefix or "Items", "None")]
            rows = []
            for index, item in enumerate(value, start=1):
                rows.extend(
                    SimbioReader._flatten_model(
                        item,
                        f"{prefix}[{index}]",
                        use_symbols=use_symbols,
                    )
                )
            return rows
        return [(prefix or "Value", str(value))]

    @classmethod
    def _model_panel(
        cls,
        title: str,
        model,
        use_symbols: bool = True,
        leaf_names: bool = False,
        two_columns: bool = False,
    ) -> Panel:
        table = Table.grid()
        column_groups = 2 if two_columns else 1
        for _ in range(column_groups):
            table.add_column(style="yellow", justify="right")
            table.add_column()
            table.add_column(style="cyan", justify="left")

        rows = cls._flatten_model(model, use_symbols=use_symbols)
        formatted_rows = [
            (
                (name.rsplit(".", 1)[-1] if leaf_names else name)
                .replace("_", " ")
                .title(),
                " = ",
                value,
            )
            for name, value in rows
        ]
        if two_columns:
            midpoint = (len(formatted_rows) + 1) // 2
            left_rows = formatted_rows[:midpoint]
            right_rows = formatted_rows[midpoint:]
            empty = ("", "", "")
            for index, left_row in enumerate(left_rows):
                right_row = right_rows[index] if index < len(right_rows) else empty
                table.add_row(*left_row, *right_row)
        else:
            for row in formatted_rows:
                table.add_row(*row)
        return Panel(table, title=title, border_style="green", expand=False)

    @classmethod
    def _housekeeping_panel(
        cls,
        title: str,
        model,
        use_symbols: bool = True,
    ) -> Panel:
        """Render housekeeping values together with their measurement units."""
        return cls._measurement_panel(
            title,
            model,
            use_symbols=use_symbols,
        )

    @classmethod
    def _measurement_panel(
        cls,
        title: str,
        model,
        use_symbols: bool = True,
    ) -> Panel:
        """Render model values together with their measurement units."""
        model_fields = {field.name for field in fields(model)}
        unit_fields = cls._model_unit_fields(model_fields)
        table = Table.grid()
        table.add_column(style="yellow", justify="right")
        table.add_column()
        table.add_column(style="cyan", justify="left")
        unit_field_names = set(unit_fields.values())
        for field in fields(model):
            if field.name in unit_field_names:
                continue
            value = getattr(model, field.name)
            unit_field = unit_fields.get(field.name)
            unit = getattr(model, unit_field) if unit_field else None
            if unit and use_symbols:
                unit = cls._unit_symbol(unit)
            formatted_value = f"{value} {unit}" if unit else str(value)
            table.add_row(
                field.name.replace("_", " ").title(),
                " = ",
                formatted_value,
            )
        return Panel(table, title=title, border_style="green", expand=False)

    @staticmethod
    def _model_unit_fields(model_fields: set[str]) -> dict[str, str]:
        unit_fields = {}
        for field_name in model_fields:
            if field_name.endswith("_measurement_unit"):
                value_name = field_name.removesuffix("_measurement_unit")
                if value_name in model_fields:
                    unit_fields[value_name] = field_name
            elif field_name.endswith("_unit"):
                value_name = field_name.removesuffix("_unit")
                if value_name in model_fields:
                    unit_fields[value_name] = field_name
        return unit_fields

    @staticmethod
    def _unit_symbol(unit: str) -> str:
        symbols = {
            "arcmin": "′",
            "arcsec": "″",
            "byte": "B",
            "deg": "°",
            "micrometer": "µm",
            "pixel": "px",
            "second": "s",
        }
        return symbols.get(unit, unit)

    def _csv_data_panel(self) -> Panel:
        """Render the product CSV table loaded by pds4_tools."""
        table = Table(show_header=True, header_style="bold yellow")
        csv_structure = getattr(self, "csv_data", None)
        if csv_structure is None:
            table.add_column("Status")
            table.add_row("CSV housekeeping data not available")
            return Panel(
                table,
                title="CSV Housekeeping Data",
                border_style="green",
                expand=False,
            )

        csv_data = csv_structure.data
        column_names = csv_data.dtype.names or ()
        if not column_names:
            table.add_column("Row", justify="right")
            table.add_column("Value")
            for row_number, row in enumerate(csv_data, start=1):
                table.add_row(str(row_number), str(row))
        else:
            table.add_column("Row", justify="right")
            table.add_column("Parameter", style="yellow")
            table.add_column("Value", style="cyan")
            for row_number, row in enumerate(csv_data, start=1):
                for column_name in column_names:
                    table.add_row(
                        str(row_number),
                        column_name.replace("_", " ").title(),
                        self._format_csv_value(row[column_name]),
                    )
        return Panel(
            table,
            title="CSV Housekeeping Data",
            border_style="green",
            expand=False,
        )

    @staticmethod
    def _format_csv_value(value) -> str:
        if isinstance(value, bytes):
            return value.decode(errors="replace")
        return str(value)

    def info(self) -> Panel:
        dt = Table.grid()
        dt.add_column(style="yellow", justify="right")
        dt.add_column()
        dt.add_column(style="cyan", justify="left")

        sep = " = "
        dt.add_row("Channel", sep, self.channel.value)
        dt.add_row("Processing Level", sep, self.processing_level)
        dt.add_row("Mission Phase", sep, self.mission_phase)
        dt.add_row("Logical Identifier", sep, self.lid)
        dt.add_row("Version", sep, self.version_id)
        dt.add_row("Title", sep, self.title)
        dt.add_row(
            "Data Model Version",
            sep,
            self.information_model_version,
        )
        dt.add_row(
            "Observation Start Time",
            sep,
            self.time_coordinates.start_utc.isoformat(),
        )
        dt.add_row(
            "Observation Stop Time",
            sep,
            self.time_coordinates.end_utc.isoformat(),
        )
        dt.add_row(
            "Spacecraft Clock Start Count",
            sep,
            self.time_coordinates.start_scet,
        )
        dt.add_row(
            "Spacecraft Clock Stop Count",
            sep,
            self.time_coordinates.end_scet,
        )

        return Panel(dt, title="SimbioReader Info", border_style="green", expand=False)

    def summary(self) -> Panel:
        return self.show()

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

    def get_segment_by_file(
        self, file_name: str | Path
    ) -> ArrayStructure | None:
        """Return a VIHI array by data-file name for multi-array products."""
        if self.channel != INSTRUMENT.VIHI or len(self.data_arrays) <= 1:
            return None

        requested_name = Path(file_name).name
        for data_array in self.data_arrays:
            if Path(data_array.parent_filename).name == requested_name:
                return data_array
        return None

    def savePreview(
        self,
        img_type: str = "png",
        quality: int = 100,
        outFolder: Path = None,
        template: Path = None,
        description: str = "This is the first version.",
    ) -> str | None:
        """Report that preview generation is no longer supported.

        .. deprecated::
            This method is obsolete and retained temporarily for API
            compatibility. It must be removed in a future version.

        Args:
            img_type: The desired image format. Supported formats are 'png', 'tif', and 'jpg'. Defaults to 'png'.
            quality: The quality of the saved image (applicable for 'png' and 'jpg' formats only). Ranges from 0 (worst) to 100 (best). Defaults to 100.
            out_folder: The output folder path where the preview image will be saved. Defaults to the same directory as the original Simbio file.
            template: name of the PDS4 template that will be generated. If None no template will be written. If the template is not none the img_type
                    is forced to png

        Raises:
            DeprecatedMethodError: Always raised because the method is obsolete.
        """
        # TODO: Remove savePreview in a future major release.
        message = (
            "savePreview() is obsolete and will be removed in a future "
            "version of SimbioReader."
        )
        self.console.print(f"{MSG.WARNING}{message}")
        raise DeprecatedMethodError(message)

    def __str__(self) -> str:
        return f"SimbioReader(channel={self.channel}, level={self.level}, lid={self.lid}, version={self.version})"

    def __repr__(self) -> str:
        return self.__str__()
