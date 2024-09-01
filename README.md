![Version 0.2.0](https://img.shields.io/badge/version-0.2.0-blue?style=plastic)
![Language Python 3.12](https://img.shields.io/badge/python-3.12-orange?style=plastic&logo=python)
![BepiColombo SIMBIO-SYS](https://img.shields.io/badge/BepiColombo-SIMBIO--SYS-blue?style=plastic)
[![Upload Python Package](https://github.com/SIMBIO-SYS/SimbioReader/actions/workflows/python-publish.yml/badge.svg)](https://github.com/SIMBIO-SYS/SimbioReader/actions/workflows/python-publish.yml)
[![SimbioReader Test](https://github.com/SIMBIO-SYS/SimbioReader/actions/workflows/test.yml/badge.svg)](https://github.com/SIMBIO-SYS/SimbioReader/actions/workflows/test.yml)

# SimbioReader


SimbioReader is the official Python reader for the data of the Spectrometer And Imagers For Mpo Bepicolombo Integrated Observatory System on board the ESA mission BepiColombo.

For more information about SIMBIO-SYS you can visit the official [ESA SIMBIO-SYS webpage](https://www.cosmos.esa.int/web/bepicolombo/simbio-sys)

## Installation

To install the reader you can use the command:

```console
$ python3 -m pip install SimbioReader
```

## Usage

The package contain a class that read and decode the SIMBIO-SYS image

```python
from SimbioReader import SimbioReader as SR

dat = SimbioReader("sim_raw_sc_vihi_internal_cruise_ico4_2020-12-14_001.dat")
```

## Command line tools

In the package are included two command line tools:

+ **simbioReader** show the info of a specific SIMBIO-SYS data product;
+ **simbioInfo** show the information about phases, subphases and test of SIMBIO-SYS;

### simbioReader

```console
simbioReader sim_raw_sc_vihi_internal_cruise_ico6_2021-11-22_001.dat
```

will show the main information about the product.

Are avalaible some options:

- **--all** will display all the avilable information
- **--hk** wil display also the housekeeping
- **--detector** will display all the detector information
- **--data-structure** will display the data structure of the file
- **--filter** will display the information about the used filter if the data come from HRIC or STC, otherwise the option will be ignored

For any details you can use the option **--help**.

Using the option **--version** will be shown the software version and the datamodel version implemented in it.

### simbioInfo

***simbioInfo*** tool is a command line interface (cli) wiith three subcommands:

- **filters** Show the definition of filter(s) of a specific channel
- **phases** Show the past mission phase(s);
- **subphases** Show the past mission subphase(s);
- **tests** Show the past SIMBIO-SYS performed test(s)

#### filters

The subcommand **filter** has an argument, the channel and an option ***--name***.

If the user provides only the channel, all the filters specific to that channel will be shown. 
If the user adds the -name option, only the selected filter will be displayed, if found.

A description of argument and options coul be required using the option ***--help***




## Class Description

### Methods

+ **Show()** display the main information related to the data file

```python
dat.Show()
```
