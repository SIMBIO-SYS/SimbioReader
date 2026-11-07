CLI
===

The package exposes a single ``simbioReader`` command organized into
subcommands. Running it without a subcommand displays the help.

version
*******

Display the installed code version and the compatible PSA and SIMBIO-SYS data
models. Both values include the semantic version and coded identifier.

.. code-block:: bash

    simbioReader version

about
*****

Display package metadata, author contact, description, and repository.

.. code-block:: bash

    simbioReader about

phases
******

Display mission phases, subphases, and test campaigns. Use ``--kind`` to
select ``phases``, ``subphases``, ``tests``, or ``all``. Results can be
selected with ``--date``, ``--name``, ``--phase``, and ``--subphase``.

.. code-block:: bash

    simbioReader phases --kind phases
    simbioReader phases --kind subphases --date 2024-04-08
    simbioReader phases --kind tests --subphase ico9

filters
*******

Display all HRIC or STC filters, or select one with ``--name``. When
``--name`` is provided, the channel is optional and both instruments are
searched. When neither channel nor name is provided, all filters from both
instruments are displayed. Filter names and channel identifiers are
case-insensitive; hyphens in kebab-case filter names are optional.

.. code-block:: bash

    simbioReader filters
    simbioReader filters HRIC
    simbioReader filters STC --name PAN-L
    simbioReader filters --name pan-l

info
****

Read a specific PDS4 product. The command supports ``--all``, ``--hk``,
``--detector``, ``--data-structure``, ``--filters``, ``--summarize``,
``--debug``, ``--verbose``, and ``--no-symbols``. Measurement units use
symbols by default; ``--no-symbols`` preserves the names found in the XML
label.

Use ``--imaging``, ``--display``, ``--geometry``, and ``--references`` to
select individual panels alongside general product and target information.
The flags can be combined. References are shown in separate internal and
external tables. Associated products are labeled as housekeeping or geometry
when their LID contains the corresponding ``hk`` or ``geometry`` token.

When ``--hk`` is selected, the output includes both the typed instrument
housekeeping values and the loaded CSV housekeeping table. Housekeeping and
detector rows use the ``parameter = value unit`` convention. Geometry groups
fields by section, with separate headings for footprint corners and vectors.
Imaging groups optional Downsampling fields and lists temperatures by sensor.
Use ``--verbose`` for file discovery and ``--debug`` for metadata diagnostics.

.. code-block:: bash

    simbioReader info product.lblx --all
    simbioReader info product.lblx --display --geometry
    simbioReader info product.lblx --references
    simbioReader info product.dat --summarize
