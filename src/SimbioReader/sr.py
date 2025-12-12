from pathlib import Path
from rich.console import Console
from xml.dom.minidom import Element, parse
from SimbioReader.tools import getElement, getValue, camel_case
from dateutil import parser
import pandas as pd
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from SimbioReader.constants import MSG


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
        self.items_number = len(file_obs)
        self.channel = channel
        self.level = level
        for i, fo in enumerate(file_obs):
            file_name = source_path.joinpath(getValue(fo, "file_name"))
            if verbose or debug:
                self.console.print(
                    f"{MSG.Info}Processing file {i+1}/{self.items_number}: {file_name.name}"
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
                    if debug:
                        self.console.print(
                            f"{MSG.Degug}Found filter: {filter}"
                        )
                    pass
                else:
                    # qube /segments
                    pass

    def __str__(self):
        return f"Data(channel={self.channel}, level={self.level}, items_number={self.items_number})"

    def __repr__(self):
        return self.__str__()


class SimbioReader:
    def __init__(
        self, file_path: Path, debug: bool = False, verbose: bool = False, console=None
    ):
        # Initialize the SimbioReader with a file path and optional console for output
        self.pdsLabel: Path = None
        if console is None:
            self.console = Console()
        else:
            self.console = console

        if debug:
            self.console.print(
                f"{MSG.DEBUG}Initializing SimbioReader with file path: {file_path}"
            )
        # Check the filename extension
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
        if debug:
            self.console.print(
                f"{MSG.DEBUG}Initialized SimbioReader with channel: {self.title}, version: {self.level}, Datamodel: {self.dataModelVersion}"
            )

        # Observation Time

        obsArea = getElement(label, "Observation_Area")
        timeCoords = getElement(obsArea, "Time_Coordinates")
        self.startTime = parser.parse(getValue(timeCoords, "start_date_time"))
        self.stopTime = parser.parse(getValue(timeCoords, "stop_date_time"))

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
                self.console.print(
                    f"{MSG.ERROR}The file {file_path} does not have a .lblx extension."
                )
                parts = file_path.stem.split("_")
                pdsLabel = f"{('_').join(parts[:-5])}__{'_'.join(parts[-2:])}.lblx"
                return file_path.parent.joinpath(pdsLabel)
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
        col = Columns(
            [self.show(), self.target.show(), self.data.hk.show()], expand=True
        )

        return Panel(
            col, title="SimbioReader Summary", border_style="green", expand=False
        )
