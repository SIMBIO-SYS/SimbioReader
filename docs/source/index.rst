SimbioReader documentation
==========================

**SimbioReader** reads SIMBIO-SYS PDS4 products from ESA's BepiColombo
mission. It exposes observational arrays and housekeeping tables together with
typed metadata for STC, HRIC, VIHI, Display, Imaging, Geometry, and product
references.

SimbioReader 1.0 requires Python 3.14 and provides both a Python API and the
``simbioReader`` command-line interface.

.. note::

   Version 1.0 is under active development. ``savePreview`` remains only as an
   obsolete compatibility stub and raises an exception when called.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   usage
   class-map
   cli
   reference
