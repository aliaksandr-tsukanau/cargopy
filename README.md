[![Happyly on PyPI](https://img.shields.io/pypi/v/happyly.svg)](https://pypi.python.org/pypi/happyly)
[![Python version](https://img.shields.io/pypi/pyversions/happyly.svg)](https://pypi.python.org/pypi/happyly)
[![Build Status](https://travis-ci.com/equeumco/happyly.svg?branch=master)](https://travis-ci.com/equeumco/happyly)

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
1. Create and activate a virtual environment (e.g. `python -m venv env; source env/bin/activate`).
2. Install [`flit`](https://flit.readthedocs.io/en/latest/): `pip install flit`.
3. Use `flit` to install the package with all development dependencies: `flit install`.
   Repeat this whenever you want to account for new code changes
   or dependencies.
4. Note that the repository uses [pre-commit](https://pre-commit.com/)
   to auto-check code for style and types.
   Enable it for your cloned repo with `pre-commit install`.
5. In order to run tests, use either `pytest` (tests against your current python version)
   or `tox` (will try to test against all supported python versions).
6. When you are ready to deploy the project,
   use [`bumpversion`](https://github.com/c4urself/bump2version):
   `bumpversion patch` (or `minor`, or `major`) and then `git push && git push --tags`.
   [Travis](https://travis-ci.org/equeumco/happyly) will detect it
   and automatically deploy the package to PyPI.
   It is also advised to create a new release on GitHub
   describing significant changes since the previous version.

# Note about versioning scheme
We use semantic versioning with added `rc` stage:
each version (major, minor or patch) will start with `rc1` variant,
which is then advanced either to `rc2` etc using `bumpversion rc`
or "released" using `bumpversion rel` (which removed `rcN` suffix completely).

From the `bumpversin`'s point of view, there are two additional version parts:
`rel` (which can be either `alpha`, `rc` or missing = `release`)
and `rc` which denotes number of release candidate.
`alpha` is not used by `bumpversion` directly
but can be used when specifying version manually: `bumpversion --new-version 1.1.0alpha1`.
If you use `bumpversion rel` on such version, it will first transition from `alphaN` to `rc1`,
and only then will it switch to `release`, rejecting `rc` suffix.

If you want to release new version skipping `rc` stage (probably a `patch` version)
then you can use either of these methods:

1. `bumpversion --new-version 1.0.1` (substitute the desired new version) - not recommended;
2. Recommended approach: `bumpversion --no-tag patch && bumpversion rel`.
This will create an intermediary commit for `rc` but won't create a tag for it
and hence won't trigger deployment for intermediary `rc1` version.

# License

The code inside this repository is licensed under [MIT License](LICENSE),
while images and documentation material are licensed under
[Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
