# `sphinx-babel`

`sphinx.ext.autodoc`-like extensions for auto-generating codebase documentation in languages other than Python. To date, `sphinx-babel` includes:

- `sphinx_babel.autodox` to ingest Doxygen documentation. This extension simply invokes `doxygen` (which is assumed to be present in the system)
and [`doxysphinx`](https://github.com/boschglobal/doxysphinx) to produce the desired output.

Useful for polyglot projects.

## Installation

Install the package from sources e.g.:

```sh
pip install git+https://github.com/Ekumen-OS/sphinx-babel.git
```

Then add the extensions of choice to your `conf.py` file e.g.:

``` python
extensions = ["sphinx_babel.autodox"]
```

## Usage

To use `sphinx_babel.autodox`, you must list each of your Doxygen projects in your `conf.py` file e.g.:

``` python
extensions = ["sphinx_babel.autodox"]

autodox_outdir = "path/to/output"
autodox_projects = {
    "my_project": "path/to/doxygen/docs",
}
```

All paths will be resolved relative to the Sphinx source directory. You may refer to the generated documentation like `path/to/output/my_project/html/index`. Note only the `html` format is supported.
