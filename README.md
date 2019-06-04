This is a fork of [Equeum's Happyly](https://github.com/equeumco/happyly) library,
aimed to be an independent continuation of the original library headed by the original author.
Version numbers will follow the ones used for Happyly so that no one is confused.

Cargopy is not yet ready, transition to the new package is in progress

# Description (old)
Happyly helps to abstract your business logic from messaging stuff,
so that your code is maintainable and ensures separation of concerns.
Actual actions your code perform are abstracted into universal *Handlers*
which can be used with any serialization technology or messaging protocol without any change.

Happyly can be used with Flask, Celery, Django, Kafka or whatever
technology which is utilized for messaging.
Happyly also provides first-class support of Google Pub/Sub.

![Happyly's pipeline](https://github.com/equeumco/happyly/blob/master/docs/images/callbacks_with_failures.png
 "Here's how Happyly manages execution of pipeline stages")

# Documentation (old)
[Read the docs](https://happyly.readthedocs.io/en/latest/)

# Development (old, for Happyly, to be rewritten)
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
   *Important:* at the time of writing, the package `bumpversion` in PyPI is unmaintained
   and has several issues. Please use `bump2version` instead.
   It will automatically be installed with `flit install` as a developmment dependency,
   so no need to install it manually.

# Note about versioning scheme
We use semantic versioning with added `rc` stage:
each version (major, minor or patch) will start with `rc1` variant,
which is then advanced either to `rc2` etc using `bumpversion rc`
or "released" using `bumpversion rel` (which removed `rcN` suffix completely).

From the `bumpversin`'s point of view, there are two additional version parts:
`rel` (which can be either `alpha`, `rc` or missing = `release`)
and `rc` which denotes number of release candidate.
`alpha` is not used by `bumpversion` directly
but can be used when specifying version manually: `bumpversion [major|minor|patch] --new-version 1.1.0alpha1`.
If you use `bumpversion rel` on such version, it will first transition from `alphaN` to `rc1`,
and only then will it switch to `release`, rejecting `rc` suffix.

If you want to release new version skipping `rc` stage (probably a `patch` version)
then you can use either of these methods:

1. `bumpversion --new-version 1.0.1` (substitute the desired new version) - not recommended;
2. Recommended approach: `bumpversion --no-tag patch && bumpversion rel`.
This will create an intermediary commit for `rc` but won't create a tag for it
and hence won't trigger deployment for intermediary `rc1` version.

# License

The code inside this repository is licensed under
[MIT License](https://github.com/equeumco/happyly/blob/master/LICENSE),
while images and documentation material are licensed under
[Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
