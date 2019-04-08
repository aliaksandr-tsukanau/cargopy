from unittest.mock import patch

import pytest

from happyly.handling import Handler


def test_handler_abstract():
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        Handler()


class TestHandler(Handler):
    def handle(self, message):
        pass

    def on_handling_failed(self, message, error):
        pass


@patch('test_handler.TestHandler.handle', return_value={'spam': 'eggs'})
@patch('test_handler.TestHandler.on_handling_failed')
def test_handling_empty_message(on_handling_failed, handle):
    handler = TestHandler()
    result = handler.__call__({})

    handle.assert_called_with({})
    on_handling_failed.assert_not_called()

    assert result == {'spam': 'eggs'}


@patch('test_handler.TestHandler.handle', return_value={'a': 'b'})
@patch('test_handler.TestHandler.on_handling_failed')
def test_handling_not_empty_message(on_handling_failed, handle):
    handler = TestHandler()
    result = handler.__call__({'hello': 'world'})

    handle.assert_called_with({'hello': 'world'})
    on_handling_failed.assert_not_called()

    assert result == {'a': 'b'}


@patch('test_handler.TestHandler.handle', side_effect=KeyError)
@patch('test_handler.TestHandler.on_handling_failed', return_value={'err': 'error'})
def test_handling_fails(on_handling_failed, handle):
    handler = TestHandler()
    result = handler.__call__({})

    handle.assert_called_once()
    on_handling_failed.assert_called_once()
    assert result == {'err': 'error'}
