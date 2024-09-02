![Version 0.2.2](https://img.shields.io/badge/version-0.2.2-blue?style=plastic)
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

##### Examples

```console
simbioInfo filters hric
```

will show all the filters of the channel HRIC

```console
simbioInfo flters hric -n pan-l
```

will show the *HRIC* filter with the name *PAN-L*



#### phases

The subcommand **phases** will display a table of all or filtered past mission phases.

The options are:

- **--all** Show all the past mission phases;
- **--date** Show all the phases for the given date;
- **--name** Show the phase with the given name.

##### Examples

```console
simbioInfo phases --all
```
will show all the past mission phases.


```console
simbioInfo phases --date 2024-04-08
```

will show the phase that include the day *2024-04-08*

```console
simbioInfo phases --name necp
```
will show the phase with the name *necp*

#### subphases

The subcommand **subphases** will display a table of all or filtered past mission subphases.

The options are:

- **--all** Show all the past mission subphases;
- **--date** Show all the subphases for the given date;
- **--name** Show the subphase with the given name.

##### Examples

```console
simbioInfo subphases --all
```
will show all the past mission subphases.

```console
simbioInfo subphases --date 2024-04-08
```

will show the subphase that include the day *2024-04-08*, the **ico11**.

```console
simbioInfo subphases --name ico9
```
will show the phase with the name *ico9*

#### tests

The subcommand **tests** will display a table of all or filtered SIMBIO-SYS tests.

The options are:

- **--all** Show all the past SIMBIO-SYS tests;
- **--date** Show all the SIMBIO-SYS tests for the given date;
- **--name** Show the SIMBIO-SYS tests with the given name;
- **--phase** Show the SIMBIO-SYS tests for the specific phase;
- **--subphase** Show the SIMBIO-SYS tests for the specific subphase.

> [!NOTE] 
> The tests name are not unique. Please use the option **--subphase** togeter the option **--name**

##### Examples

```console
simbioInfo tests --all
```

will show all the SIMBIO-SYS tests.

```console
simbioInfo tests -d 2024-04-08\ 2:00:00  
````

will show the test that SIMBIO-SYS was performing at 2:00:00 on 2024-04-08, the *Interference Test* in the subphase *ico11*

```console
simbioInfo tests --name hric\ functional --subphase ico9
```
will show the test with the name that contain the string *hric functional* performed during the subphase *ico9*


## Class Description

### Methods

+ **Show()** display the main information related to the data file

```python
dat.Show()
```
