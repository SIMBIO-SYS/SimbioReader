# SimbioReader

SimbioReader is the official Python reader for the data of the Spectrometer And Imagers For Mpo Bepicolombo Integrated Observatory System on board the ESA mission BepiColombo.

For more information about SIMBIO-SYS you can visit the official [ESA SIMBIO-SYS webpage](https://www.cosmos.esa.int/web/bepicolombo/simbio-sys)

## Installation

To install the reader you can use the command:

```shell
$ python3 -m pip install SimbioReader
```

## Usage

The package contain a class that read and decode the SIMBIO-SYS image

```python
from SimbioReader import SimbioReader as SR

dat = SimbioReader("sim_raw_sc_vihi_internal_cruise_ico4_2020-12-14_001.dat")
```

## Command line tools
in the package are included some command line toos:

+ **simbioPhases** show all the phases of the mission BepiColombo, with all the sub-phases of SIMBIO-SYS;
+ **hricFilters** show all the filters avaible for the SIMBIO-SYS channel HRIC;
+ **stcFilters** show all the filters avaible for the SIMBIO-SYS channel STC;

## Class Description

### Methods

+ **Show()** display the main information related to the data file

```python
dat.Show()
```
