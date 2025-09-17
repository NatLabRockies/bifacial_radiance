# -*- coding: utf-8 -*-
#
# bifacial_radiance documentation build configuration file, created by
# sphinx-quickstart on Tuesday Sep 24 18:48:33 2019.
#
# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

import sys
import os
import shutil
import pathlib

"""
# Mock modules so RTD works
try:
    from mock import Mock as MagicMock
except ImportError:
    from unittest.mock import MagicMock

class Mock(MagicMock):
    @classmethod
    def __getattr__(cls, name):
        return Mock()

MOCK_MODULES = []
sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)
"""
# import distutils before calling pd.show_versions(). not needed for pd >= 1.4.x
# https://github.com/pypa/setuptools/issues/3044
#import distutils  # noqa: F401

import pandas as pd
pd.show_versions()

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath('../sphinxext'))
sys.path.insert(0, os.path.abspath('../../../'))


# copy tutorials directory from repo root into the sphinx source directory;
# see notes in docs/sphinx/source/examples.rst
docs_root = pathlib.Path('./../..')
for directory_name in ["tutorials", "images_wiki"]:
    destination = docs_root / "sphinx" / "source" / directory_name
    shutil.rmtree(destination, ignore_errors=True)
    shutil.copytree(docs_root / directory_name, destination, 
                    ignore = shutil.ignore_patterns(".ipynb_checkpoints"))


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autodoc',
    'sphinx.ext.extlinks',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',
    'IPython.sphinxext.ipython_directive',
    'IPython.sphinxext.ipython_console_highlighting',
    'sphinx.ext.doctest',
    #'autoapi.extension',
    'sphinx.ext.todo',
    'nbsphinx',
    'sphinx_gallery.load_style',
]
   


# Document Python Code
#autodoc_mock_imports = ['bs4', 'requests']
#autoapi_type = 'python'
#autoapi_dirs = '../../../bifacial_radiance'

napoleon_use_rtype = False  # group rtype on same line together with return

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'bifacial_radiance'
copyright = u'2024, NREL'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.

import bifacial_radiance

# The short X.Y version.
version = '%s' % (bifacial_radiance.__version__)
# The full version, including alpha/beta/rc tags.
release = version

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['whatsnew/*', '**.ipynb_checkpoints']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

autosummary_generate = True


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_theme = "pydata_sphinx_theme"

# https://pydata-sphinx-theme.rtfd.io/en/latest/user_guide/configuring.html
html_theme_options = {
    "github_url": "https://github.com/NREL/bifacial_radiance",

    "icon_links": [
        {
            "name": "StackOverflow",
            "url": "https://stackoverflow.com/questions/tagged/bifacial-radiance",
            "icon": "fab fa-stack-overflow",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/bifacial_radiance",
            "icon": "fab fa-python",
        },
    ],
    #"use_edit_page_button": True,
    "show_toc_level": 1,
    #"footer_start": ["copyright"],
    #"footer_center": ["sphinx-version"],
}
# Add favicons from extension sphinx_favicon
favicons = [
    {"rel": "icon", "sizes": "16x16", "href": "favicon-16x16.png"},
    {"rel": "icon", "sizes": "32x32", "href": "favicon-32x32.png"},
]


# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = '../../images_wiki/bifacial_radiance.png'

# do not execute notebooks for gallery
nbsphinx_execute = 'never'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
html_show_copyright = True

# Output file base name for HTML help builder.
htmlhelp_basename = 'bifacial_radiancedoc'

# Manually assign static jpg or png as thumbnails (nbgallery only allows
# tagged code cells to contribute thumbnails, not markdown)
nbsphinx_thumbnails = {
    'tutorials/1 - Fixed Tilt Yearly Results': '_images/openhdr_FalseColorExample.PNG',
    'tutorials/2 - Single Axis Tracking Yearly Simulation':'_images/cumulativesky.png',
    'tutorials/3 - Single Axis Tracking Hourly': '_images/bifacial_radiance.png',
    'tutorials/4 - Debugging with Custom Objects':'_images/Journal_example_torquetube.PNG',
    'tutorials/5 - Bifacial Carports and Canopies':'_images/Carport_with_car.PNG',
    'tutorials/6 - Exploring Trackerdict Structure': '_images/bifacial_radiance.png',
    'tutorials/7 - Multiple Scene Objects':'_images/MultipleSceneObject_AnalysingSceneObj2_Row1_Module4.PNG',
    'tutorials/8 - Electrical Mismatch Method':'_images/Mismatch_Definition_Example.PNG',
    'tutorials/9 - Torquetube Shading':'_images/tutorials_9_-_Torquetube_Shading_24_1.png',
    'tutorials/11 - AgriPV Systems': '_images/AgriPV_2.PNG',
    'tutorials/13 - Modeling Modules with Glass': '_images/Glass_tilted_reflection.PNG',
    'tutorials/14 - Cement Racking Albedo Improvements': '_images/Pavers.PNG',
    'tutorials/15 - New Functionalities Examples':'_images/makeModule_ComplexGeometry.PNG',
    'tutorials/16 - AgriPV - 3-up and 4-up collector optimization': '_images/AgriPV_CWandXgap_Optimization.PNG',
    'tutorials/17 - AgriPV - Jack Solar Site Modeling': '_images/AgriPV_JackSolar.PNG',
    'tutorials/18 - AgriPV - Coffee Plantation with Tree Modeling': '_images/AgriPV_CoffeeTrees.PNG',
    'tutorials/19 - East & West Facing Sheds': '_images/EW_sheds_Offset.PNG',
    'tutorials/20 - Racking I Beams': '_images/NIST_Maryland_I_BeamsExample.PNG',
    'tutorials/21 - Weather to Module Performance': '_images/bifacial_radiance.png',
    'tutorials/22 - Mirrors and Modules': '_images/22_mirror_moduleCombo_rvu.PNG',
    }

# A workaround for the responsive tables always having annoying scrollbars.
def setup(app):
    app.add_css_file("no_scrollbars.css")
    

"""    
# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
#'papersize': 'letterpaper',

# The font size ('10pt', '11pt' or '12pt').
#'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
#'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
  ('index', 'bifacial_radiance.tex', u'bifacial_radiance\\_Python Documentation',
   u'NREL, github contributors', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True
"""
# extlinks alias
extlinks = {'issue': ('https://github.com/NREL/bifacial_radiance/issues/%s', 'GH %s'),
            'pull': ('https://github.com/NREL/bifacial_radiance/pull/%s', 'GH %s'),
            'wiki': ('https://github.com/NREL/bifacial_radiance/wiki/%s', 'wiki %s'),
            'doi': ('http://dx.doi.org/%s', 'DOI: %s'),
            'ghuser': ('https://github.com/%s', '@%s')}
"""
# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'bifacial_radiance', u'bifacial_radiance Documentation',
     [u'NREL, github contributors'], 1)
]

# If true, show URL addresses after external links.
#man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
  ('index', 'bifacial_radiance', u'bifacial_radiance Documentation',
   u'NREL, github contributors', 'bifacial_radiance', 'One line description of project.',
   'Miscellaneous'),
]

# Documents to append as an appendix to all manuals.
#texinfo_appendices = []

# If false, no module index is generated.
#texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
#texinfo_no_detailmenu = False

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3.7/', None),
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable/', None),
    'numpy': ('https://docs.scipy.org/doc/numpy/', None),
}

nbsphinx_allow_errors = True

ipython_warning_is_error = False
"""