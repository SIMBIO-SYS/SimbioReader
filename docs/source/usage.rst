Usage
=====

Installation
------------

Python 3.14 or later is required.

.. code-block:: console

    python3 -m pip install SimbioReader

Alternatively, add the package to a uv project:

.. code-block:: console

    uv add SimbioReader

Read a product
--------------

Pass an existing PDS4 ``.lblx`` label, a supported data file with its label,
or a directory containing exactly one ``.lblx`` label. Keep the data files
referenced by the label alongside the product.

.. code-block:: python

    from pathlib import Path
    from rich import print
    from SimbioReader import SimbioReader as SR

    dat = SR(Path("product.lblx"), updateCheck=False)
    print(dat.show())
    print(dat.lvid)

``updateCheck=False`` disables the constructor's package update check.
``show()`` returns a Rich panel; print it to display it.
For products with filter metadata, ``get_filters()`` returns the decoded
filter objects and ``summary()`` returns a product, target and filter summary.

Development and documentation
-----------------------------

From the repository root:

.. code-block:: console

    uv sync --locked --group test --group devel
    uv run pytest
    uv run ruff check src test
    uv build
    uv run --no-project --with-requirements docs/requirements.txt --with . python -m sphinx -b html docs/source docs/build/html

The repository also contains ``FLUSSO_DATI.md``, a detailed Italian guide to
parsing and data flow.
