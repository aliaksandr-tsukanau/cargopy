"""Conveniently separate your business logic from messaging stuff."""

# flake8: noqa F401
import logging

__version__ = '0.9.0rc1'


from .listening import Executor, BaseListener
from .schemas import Schema
from .caching import Cacher
from .serialization import Serializer, Deserializer
from .handling import Handler, DUMMY_HANDLER
from .exceptions import StopPipeline


def _welcome():
    import sys

    sys.stdout.write(f'Using happyly v{__version__}.\n')


def _setup_warnings():
    import warnings

    for warning_type in PendingDeprecationWarning, DeprecationWarning:
        warnings.filterwarnings(
            'always', category=warning_type, module=r'^{0}\.'.format(__name__)
        )


def _setup_logging():
    logging.getLogger(__name__).setLevel(logging.INFO)


_welcome()
_setup_warnings()
_setup_logging()
del _welcome
del _setup_warnings
del _setup_logging
