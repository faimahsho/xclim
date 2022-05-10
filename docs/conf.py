#!/usr/bin/env python
#
# xclim documentation build configuration file, created by
# sphinx-quickstart on Fri Jun  9 13:47:02 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.
from __future__ import annotations

import datetime
import os
import sys
import warnings
from collections import OrderedDict

import xarray

xarray.DataArray.__module__ = "xarray"
xarray.Dataset.__module__ = "xarray"

import xclim  # noqa

# If extensions (or modules to document with autodoc) are in another
# directory, add these directories to sys.path here. If the directory is
# relative to the documentation root, use os.path.abspath to make it
# absolute, like shown here.
#
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("."))


def _get_indicators(module):
    """For all modules or classes listed, return the children that are instances of registered Indicator classes.

    module : A xclim module.
    """
    from xclim.core.indicator import registry

    out = {}
    for key, val in module.__dict__.items():
        if hasattr(val, "_registry_id") and val._registry_id in registry:
            out[key] = val

    return OrderedDict(sorted(out.items()))


def _indicator_table(module):
    """Return a sequence of dicts storing metadata about all available indices in xclim."""
    inds = _get_indicators(getattr(xclim.indicators, module))
    table = {}
    for indname, ind in inds.items():
        # Apply default values
        # args = {
        #     name: p.default if p.default != inspect._empty else f"<{name}>"
        #     for (name, p) in ind._sig.parameters.items()
        # }
        try:
            table[indname] = ind.json()  # args?
        except KeyError as err:
            warnings.warn(
                f"{ind.identifier} could not be documented.({err})", UserWarning
            )
        else:
            table[indname]["doc"] = ind.__doc__
            if ind.compute.__module__.endswith("generic"):
                table[indname][
                    "function"
                ] = f"xclim.indices.generic.{ind.compute.__name__}"
            else:
                table[indname]["function"] = f"xclim.indices.{ind.compute.__name__}"
    return table


modules = ("atmos", "land", "seaIce", "cf", "icclim", "anuclim")
indicators = {module: _indicator_table(module) for module in modules}

# -- General configuration ---------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.coverage",
    "sphinx.ext.todo",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.intersphinx",
    "sphinx.ext.extlinks",
    "rstjinja",
    "nbsphinx",
    "IPython.sphinxext.ipython_console_highlighting",
    "autodoc_indicator",
]

napoleon_numpy_docstring = True
napoleon_use_rtype = False
napoleon_use_param = False
napoleon_use_ivar = True

intersphinx_mapping = {
    "clisops": ("https://clisops.readthedocs.io/en/latest/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference/", None),
    "sklearn": ("https://scikit-learn.org/stable/", None),
    "statsmodels": ("https://www.statsmodels.org/stable/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}
extlinks = {
    "issue": ("https://github.com/Ouranosinc/xclim/issues/%s", "GH/"),
    "pull": ("https://github.com/Ouranosinc/xclim/pull/%s", "PR/"),
    "user": ("https://github.com/", "@"),
}

nbsphinx_execute = "auto"
nbsphinx_prolog = r"""
{% set docname = env.doc2path(env.docname, base=None) %}

.. only:: html

    `Download this notebook from github. <https://github.com/Ouranosinc/xclim/raw/master/docs/{{ docname }}>`_
"""
nbsphinx_timeout = 300
nbsphinx_allow_errors = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# If a list of string, all suffixes will be understood as restructured text variants.
source_suffix = [".rst"]

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "xclim"
copyright = (
    f"2018-{datetime.datetime.now().year}, Ouranos Inc., Travis Logan, and contributors"
)
author = "Travis Logan"

# The version info for the project you're documenting, acts as replacement
# for |version| and |release|, also used in various other places throughout
# the built documents.
#
# The short X.Y version.
version = xclim.__version__
# The full version, including alpha/beta/rc tags.
release = xclim.__version__

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "notebooks/xclim_training",
    "**.ipynb_checkpoints",
]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Options for HTML output -------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_title = "XClim Official Documentation"
html_short_title = "XClim"

html_theme = "sphinx_rtd_theme"

html_context = {"indicators": indicators}

# Theme options are theme-specific and customize the look and feel of a
# theme further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {"logo_only": True, "style_external_links": True}

html_sidebars = {
    "**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"]
}

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = "_static/_images/xclim-logo.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# -- Options for HTMLHelp output ---------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "xclimdoc"

# -- Options for LaTeX output ------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': r"""
    # \renewcommand{\v}[1]{\mathbf{#1}}
    # """,
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass
# [howto, manual, or own class]).
latex_documents = [
    (master_doc, "xclim.tex", "xclim Documentation", "Travis Logan", "manual")
]

# -- Options for manual page output ------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "xclim", "xclim Documentation", [author], 1)]

# -- Options for Texinfo output ----------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "xclim",
        "xclim Documentation",
        author,
        "xclim",
        "One line description of project.",
        "Miscellaneous",
    )
]
