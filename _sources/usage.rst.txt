Usage
=====

.. _installation:

Installation
------------
To install the reader you can use the command:

.. code-block:: bash

    pip install SimbioReader

Usage
-----

The package contain a class that read and decode the SIMBIO-SYS image

.. code-block:: python

    from SimbioReader import SimbioReader as SR

    dat = SimbioReader("sim_raw_sc_vihi_internal_cruise_ico4_2020-12-14_001.dat")