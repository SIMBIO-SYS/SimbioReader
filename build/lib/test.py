#! /usr/bin/env python3
from SimbioReader import SimbioReader
from rich.console import Console
console=Console()

dat = SimbioReader(
    "/Users/romolo.politi/Documents/Progetti/SIMBIO-SYS/Software/SimGen/output/raw/vihi/sim_raw_sc_vihi_cruise_ico4_2020-12-14_001/sim_raw_sc_vihi_internal_cruise_ico4_2020-12-14_001.dat", debug=True, verbose=True,console=console)
dat.Show()
console.print(dat)