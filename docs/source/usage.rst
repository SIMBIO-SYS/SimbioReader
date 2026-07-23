Usage
=====

Installation
------------

Install the published package with pip:

.. code-block:: bash

   python3 -m pip install SimbioReader

or with uv:

.. code-block:: bash

   uv add SimbioReader

Python API
----------

Create a reader from a PDS4 label, an associated ``.dat``, ``.qub``, or
``.csv`` file, or a directory containing exactly one label:

.. code-block:: python

   from pathlib import Path

   from SimbioReader import SimbioReader

   product = SimbioReader(Path("product.lblx"))

   print(product.channel)
   print(product.time_coordinates)
   print(product.target)

The observational structures loaded by ``pds4_tools`` are exposed through
``data_arrays`` and, when present, ``image_data``, ``cube_data``, and
``csv_data``.

Typed metadata
--------------

The ``simbio`` attribute exposes only the model associated with the product
channel:

.. code-block:: python

   if product.channel == "STC":
       print(product.simbio.stc.housekeeping)
   elif product.channel == "HRIC":
       print(product.simbio.hric.general_parameters)
   elif product.channel == "VIHI":
       print(product.simbio.vihi.frame_parameters)

Discipline-area metadata is available through ``display``, ``imaging``, and
``geometry``. Product links are available through ``reference``. Numeric XML
values preserve their units in companion ``*_unit`` fields.

Display helpers
---------------

``summary()`` returns a compact Rich panel. ``show()`` accepts selectors for
the additional sections:

.. code-block:: python

   console.print(
       product.show(
           hk=True,
           detector=True,
           data_structure=True,
           filters=True,
           all_info=False,
           no_symbols=False,
       )
   )

Housekeeping and detector values are rendered as ``parameter = value unit``.
Geometry uses leaf attribute names and a compact two-column arrangement.

VIHI segments
-------------

``get_segment_by_file()`` is available only for VIHI products containing more
than one data array. It returns the structure whose parent filename matches
the requested file; it returns ``None`` for single-array VIHI products and
other channels.

Obsolete preview API
--------------------

``savePreview()`` is retained temporarily for source compatibility. It prints
an obsolescence warning and raises
:class:`SimbioReader.exceptions.DeprecatedMethodError`. New code must not use
this method.
