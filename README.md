[![Happyly on PyPI](https://img.shields.io/pypi/v/happyly.svg)](https://pypi.python.org/pypi/happyly)
[![Python version](https://img.shields.io/pypi/pyversions/happyly.svg)](https://pypi.python.org/pypi/happyly)

# Description
Happyly helps to build an extensible codebase when you are using Google Pub/Sub - and potentially any similar technology.
Actual actions your code perform are abstracted into universal _Handlers_ which can be used with any serialization technology or messaging protocol without any change.

# Why this name?
Happyly stands for <b>HA</b>ndlers for <b>P</b>ub/sub as a <b>PY</b>thon <b>L</b>ibrar<b>Y</b>

# Installation
```pip install happyly```

# Where can I learn how to use it?
Check out [tutorial](https://github.com/equeumco/happyly/blob/master/Tutorial.ipynb)

# Development
1. Create and activate a virtual environment (e.g. `python -m venv env; source env/bin/activate`)
2. Install [`flit`](https://flit.readthedocs.io/en/latest/): `pip install flit`
3. Use `flit` to install the package with all development dependencies: `flit install`
4. Note that the repository uses [pre-commit](https://pre-commit.com/) to auto-check code for style and types. Enable it for your cloned repo with `pre-commit install`.
