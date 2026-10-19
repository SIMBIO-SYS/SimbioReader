# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import sys
import tomllib
from pathlib import Path

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'SimbioReader'
copyright = '2024, Romolo Politi'
author = 'Romolo Politi'
ROOT = Path(__file__).resolve().parents[2]
release = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']['version']
sys.path.insert(0, str(ROOT / 'src'))

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    # 'sphinx_rtd_theme',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
]

templates_path = []
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme" #'furo'
html_static_path = []


autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'private-members': False,
    'show-inheritance': True,
    
}
autodoc_typehints_format= 'short'


