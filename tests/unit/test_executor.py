from typing import Any, Mapping
from unittest.mock import patch

from happyly import Deserializer
from happyly.handling import HandlingResult, HandlingResultStatus
from happyly.listening import Executor
from happyly.serialization import DUMMY_SERDE
from tests.unit.test_handler import TestHandler


@patch('test_executor.Executor.on_received')
@patch('test_executor.Executor.on_deserialized')
@patch('test_executor.Executor.on_deserialization_failed')
@patch('test_executor.Executor.on_handled')
@patch('test_executor.Executor.on_published')
@patch('test_executor.Executor.on_publishing_failed')
@patch('test_executor.Executor.on_finished')
@patch(
    'test_executor.TestHandler.__call__',
    return_value=HandlingResult.ok(42),  # type: ignore
)
def test_executor_no_input(
    handler,
    on_finished,
    on_publishing_failed,
    on_published,
    on_handled,
    on_deserialization_failed,
    on_deserialized,
    on_received,
):
    executor = Executor(handler=TestHandler())
    assert executor.deserializer is DUMMY_SERDE
    assert executor.publisher is None
    executor.run()
    on_received.assert_called_with(None)
    on_deserialized.assert_called_with(None, {})
    handler.assert_called_with({})
    on_handled.assert_called_with(
        original_message=None,
        parsed_message={},
        result=HandlingResult(HandlingResultStatus.OK, data=42),  # type: ignore
    )
    on_published.assert_not_called()
    on_publishing_failed.assert_not_called()
    on_deserialization_failed.assert_not_called()
    on_finished.assert_called_with(original_message=None, error=None)


@patch('test_executor.Executor.on_received')
@patch('test_executor.Executor.on_deserialized')
@patch('test_executor.Executor.on_deserialization_failed')
@patch('test_executor.Executor.on_handled')
@patch('test_executor.Executor.on_published')
@patch('test_executor.Executor.on_publishing_failed')
@patch('test_executor.Executor.on_finished')
@patch(
    'test_executor.TestHandler.__call__',
    return_value=HandlingResult.ok(42),  # type: ignore
)
def test_executor_with_input(
    handler,
    on_finished,
    on_publishing_failed,
    on_published,
    on_handled,
    on_deserialization_failed,
    on_deserialized,
    on_received,
):
    class TestDeser(Deserializer):
        def deserialize(self, message: Any) -> Mapping[str, Any]:
            return {'spam': 'eggs'}

        def build_error_result(
            self, message: Any, error: Exception
        ) -> Mapping[str, Any]:
            raise error

    des = TestDeser()
    executor = Executor(handler=TestHandler(), deserializer=des, publisher=None)
    assert executor.deserializer == des
    assert executor.publisher is None
    executor.run("original message")
    on_received.assert_called_with("original message")
    on_deserialized.assert_called_with("original message", {'spam': 'eggs'})
    handler.assert_called_with({'spam': 'eggs'})
    on_handled.assert_called_with(
        original_message="original message",
        parsed_message={'spam': 'eggs'},
        result=HandlingResult(HandlingResultStatus.OK, data=42),
    )
    on_published.assert_not_called()
    on_publishing_failed.assert_not_called()
    on_deserialization_failed.assert_not_called()
    on_finished.assert_called_with(original_message="original message", error=None)
