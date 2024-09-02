CLI
###

The pacchage has some Command line interface (CLI) tools to help the user to diplay the label file and other information about the mission.


simbioReader
************

.. code-block:: bash

    simbioReader sim_raw_sc_vihi_internal_cruise_ico6_2021-11-22_001.dat


will show the main information about the product.

Are avalaible some options:

* **\--all** will display all the avilable information
* **\--hk** wil display also the housekeeping
* **\--detector** will display all the detector information
* **\--data-structure** will display the data structure of the file
* **\--filter** will display the information about the used filter if the data come from HRIC or STC, otherwise the option will be ignored

For any details you can use the option **\--help**.

Using the option **\--version** will be shown the software version and the datamodel version implemented in it.

simbioInfo filters
******************

The subcommand **filter** has an argument, the channel and an option *\--name*.

If the user provides only the channel, all the filters specific to that channel will be shown. 
If the user adds the -name option, only the selected filter will be displayed, if found.

A description of argument and options coul be required using the option **\--help**

Examples
========

.. code-block:: bash

    simbioInfo filter hric


will show all the filters of the channel HRIC


.. code-block:: bash

    simbioInfo filter hric --name pan-l

will show the *HRIC* filter with the name *PAN-L*

A description of argument and options coul be required using the option **\--help**

simbioInfo phases
*****************

The subcommand **phases** will display a table of all or filtered past mission phases.

The options are:

- **\--all** Show all the past mission phases;
- **\--date** Show all the phases for the given date;
- **\--name** Show the phase with the given name.

Examples
========

.. code-block:: bash

    simbioInfo phases --all

will show all the past mission phases.


.. code-block:: bash

    simbioInfo phases --date 2024-04-081

will show the phase that include the day *2024-04-08*.

.. code-block:: bash

    simbioInfo phases --name necp

will show the phase with the name *necp*.

A description of argument and options coul be required using the option **\--help**

simbioInfo subphases
********************

The subcommand **subphases** will display a table of all or filtered past mission subphases.

The options are:

- **\--all** Show all the past mission subphases;
- **\--date** Show all the subphases for the given date;
- **\--name** Show the subphase with the given name.

Examples
========

.. code-block:: bash

    simbioInfo subphases --all

will show all the past mission subphases.


.. code-block:: bash

    simbioInfo phases --date 2024-04-081

will show the phase that include the day *2024-04-08*, the **ico11** subphase.

.. code-block:: bash

    simbioInfo subphases --name ico9

will show the phase with the name *ico9*.

A description of argument and options coul be required using the option **\--help**


simbioInfo tests
****************

The subcommand **tests** will display a table of all or filtered SIMBIO-SYS tests.

The options are:

- **\--all** Show all the past SIMBIO-SYS tests;
- **\--date** Show all the SIMBIO-SYS tests for the given date;
- **\--name** Show the SIMBIO-SYS tests with the given name;
- **\--phase** Show the SIMBIO-SYS tests for the specific phase;
- **\--subphase** Show the SIMBIO-SYS tests for the specific subphase.

.. note::
    The tests name are not unique. Please use the option **\--subphase** togeter the option **\--name**


Examples
========

.. code-block:: bash

    simbioInfo tests --all


will show all the SIMBIO-SYS tests.

.. code-block:: bash

    simbioInfo tests -d 2024-04-08\ 2:00:00  


will show the test that SIMBIO-SYS was performing at 2:00:00 on 2024-04-08, the *Interference Test* in the subphase *ico11*

.. code-block:: bash

    simbioInfo tests --name hric\ functional --subphase ico9

will show the test with the name that contain the string *hric functional* performed during the subphase *ico9*

A description of argument and options coul be required using the option **\--help**