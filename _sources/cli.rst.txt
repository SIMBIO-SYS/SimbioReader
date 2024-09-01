CLI
===

The pacchage has some Command line interface (CLI) tools to help the user to diplay the label file and other information about the mission.


simbioReader
------------

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
------------------

The subcommand **filter** has an argument, the channel and an option **\--name**.

If the user provides only the channel, all the filters specific to that channel will be shown. 

.. code-block:: bash

    simbioInfo filter HRIC


If the user adds the -name option, only the selected filter will be displayed, if found.

.. code-block:: bash

    simbioInfo filter HRIC --name PAN-L

A description of argument and options coul be required using the option **\--help**