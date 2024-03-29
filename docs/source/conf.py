# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here.
import pathlib
import sys
sys.path.insert(0, pathlib.Path(__file__).parents[2].resolve().as_posix())


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'lukas-staab/ball-and-hoop'
copyright = '2022, Lukas Staab, MIT Licence'
author = 'Lukas Staab'
release = '2022'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx_rtd_theme',
    'sphinx.ext.mathjax',
    'sphinx.ext.graphviz',
]

graphviz_output_format = 'svg'

templates_path = ['_templates']
exclude_patterns = []
autodoc_mock_imports = ['picamera', 'picamera.array']


intersphinx_mapping = {
    'picamera': ('https://picamera.readthedocs.io/en/release-1.13/', None),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_theme_options = {
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    'vcs_pageview_mode': 'edit',
    # Toc options
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 3,
    'includehidden': True,
    'titles_only': False,
}

# small hack to make __iter__ and __next__() visible but not the other ones
def skip(app, what, name, obj, would_skip, options):
    if name == "__iter__" or name == '__next__':
        return False
    return would_skip

def setup(app):
    app.connect("autodoc-skip-member", skip)