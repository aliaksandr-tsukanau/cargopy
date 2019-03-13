from unittest.mock import patch

from happyly.listening import Executor
from tests.unit.test_handler import TestHandler


@patch('test_executor.Executor.on_received')
@patch('test_executor.Executor.on_deserialized')
@patch('test_executor.Executor.on_deserialization_failed')
@patch('test_executor.Executor.on_handled')
@patch('test_executor.Executor.on_published')
@patch('test_executor.Executor.on_publishing_failed')
@patch('test_executor.TestHandler.__call__', return_value=42)
def test_executor_no_input(
    handler,
    on_publishing_failed,
    on_published,
    on_handled,
    on_deserialization_failed,
    on_deserialized,
    on_received,
):
    executor = Executor(handler=TestHandler(), deserializer=None, publisher=None)
    assert executor.deserializer is None
    assert executor.publisher is None
    executor.run()
    handler.assert_called_with({})
    on_handled.assert_called_with(original_message=None, parsed_message={}, result=42)
    on_received.assert_not_called()
    on_published.assert_not_called()
    on_publishing_failed.assert_not_called()
    on_deserialized.assert_not_called()
    on_deserialization_failed.assert_not_called()
