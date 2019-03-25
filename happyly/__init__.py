"""Python library for Pub/Sub message handling."""

# flake8: noqa F401

__version__ = '0.3.1'


from .listening import Executor, Listener, BaseListener
from .schemas import Schema
from .caching import Cacher
from .serialization import Serializer, Deserializer
from .handling import Handler, DUMMY_HANDLER


def _welcome():
    import sys

    sys.stdout.write(f'Using happyly v{__version__}.\n')


def _reset_warnings():
    import warnings

    warnings.resetwarnings()


_welcome()
_reset_warnings()
del _welcome
del _reset_warnings
