from typing import Any, Mapping
from unittest.mock import patch

from happyly import Deserializer, Serializer
from happyly.handling import HandlingResult, HandlingResultStatus
from happyly.listening import Executor
from happyly.serialization import DUMMY_SERDE
from tests.unit.test_handler import TestHandler


@patch('test_executor.Executor.on_received')
@patch('test_executor.Executor.on_deserialized')
@patch('test_executor.Executor.on_deserialization_failed')
@patch('test_executor.Executor.on_handled')
@patch('test_executor.Executor.on_handling_failed')
@patch('test_executor.Executor.on_serialized')
@patch('test_executor.Executor.on_serialization_failed')
@patch('test_executor.Executor.on_published')
@patch('test_executor.Executor.on_publishing_failed')
@patch('test_executor.Executor.on_finished')
@patch('test_executor.Executor.on_stopped')
@patch(
    'test_executor.TestHandler.__call__',
    return_value=HandlingResult.ok({'result': 42}),  # type: ignore
)
def test_executor_no_input(
    handler,
    on_stopped,
    on_finished,
    on_publishing_failed,
    on_published,
    on_serialization_failed,
    on_serialized,
    on_handling_failed,
    on_handled,
    on_deserialization_failed,
    on_deserialized,
    on_received,
):
    executor = Executor(handler=TestHandler())
    assert executor.deserializer is DUMMY_SERDE
    assert executor.serializer is DUMMY_SERDE
    assert executor.publisher is None
    executor.run()

    def assert_callbacks():
        on_received.assert_called_with(None)
        on_deserialized.assert_called_with(original_message=None, parsed_message={})
        on_deserialization_failed.assert_not_called()
        handler.assert_called_with({})
        on_handled.assert_called_with(
            original_message=None,
            parsed_message={},
            result=HandlingResult(
                HandlingResultStatus.OK, data={'result': 42}
            ),  # type: ignore
        )
        on_handling_failed.assert_not_called()
        on_serialized.assert_called_with(
            original=None,
            deserialized={},
            result=HandlingResult.ok({'result': 42}),
            serialized={'result': 42},
        )
        on_serialization_failed.assert_not_called()
        on_published.assert_not_called()
        on_publishing_failed.assert_not_called()
        on_finished.assert_called_with(original_message=None, error=None)
        on_stopped.assert_not_called()

        for callback in [
            handler,
            on_stopped,
            on_finished,
            on_publishing_failed,
            on_published,
            on_serialization_failed,
            on_serialized,
            on_handling_failed,
            on_handled,
            on_deserialization_failed,
            on_deserialized,
            on_received,
        ]:
            callback.reset_mock()

    assert_callbacks()
    result = executor.run_for_result()
    assert_callbacks()
    assert result == {'result': 42}


@patch('test_executor.Executor.on_received')
@patch('test_executor.Executor.on_deserialized')
@patch('test_executor.Executor.on_deserialization_failed')
@patch('test_executor.Executor.on_handled')
@patch('test_executor.Executor.on_handling_failed')
@patch('test_executor.Executor.on_serialized')
@patch('test_executor.Executor.on_serialization_failed')
@patch('test_executor.Executor.on_published')
@patch('test_executor.Executor.on_publishing_failed')
@patch('test_executor.Executor.on_finished')
@patch('test_executor.Executor.on_stopped')
@patch(
    'test_executor.TestHandler.__call__',
    return_value=HandlingResult.ok({'result': 42}),  # type: ignore
)
def test_executor_with_input(
    handler,
    on_stopped,
    on_finished,
    on_publishing_failed,
    on_published,
    on_serialization_failed,
    on_serialized,
    on_handling_failed,
    on_handled,
    on_deserialization_failed,
    on_deserialized,
    on_received,
):
    class TestDeser(Deserializer):
        def deserialize(self, message: Any) -> Mapping[str, Any]:
            return {'spam': 'eggs'}

    class TestSer(Serializer):
        def serialize(self, message_attributes: Mapping[str, Any]) -> Any:
            return {'i am': 'serialized'}

    des = TestDeser()
    ser = TestSer()
    executor = Executor(handler=TestHandler(), deserializer=des, publisher=None, serializer=ser)
    assert executor.deserializer == des
    assert executor.serializer == ser
    assert executor.publisher is None
    executor.run("original message")

    def assert_callbacks():
        on_received.assert_called_with("original message")
        on_deserialized.assert_called_with(original_message="original message", parsed_message={'spam': 'eggs'})
        on_deserialization_failed.assert_not_called()
        handler.assert_called_with({'spam': 'eggs'})
        on_handled.assert_called_with(
            original_message="original message",
            parsed_message={'spam': 'eggs'},
            result=HandlingResult(
                HandlingResultStatus.OK, data={'result': 42}
            ),  # type: ignore
        )
        on_handling_failed.assert_not_called()
        on_serialized.assert_called_with(
            original="original message",
            deserialized={'spam': 'eggs'},
            result=HandlingResult.ok({'result': 42}),
            serialized={'i am': 'serialized'},
        )
        on_serialization_failed.assert_not_called()
        on_published.assert_not_called()
        on_publishing_failed.assert_not_called()
        on_finished.assert_called_with(original_message='original message', error=None)
        on_stopped.assert_not_called()

        for callback in [
            handler,
            on_stopped,
            on_finished,
            on_publishing_failed,
            on_published,
            on_serialization_failed,
            on_serialized,
            on_handling_failed,
            on_handled,
            on_deserialization_failed,
            on_deserialized,
            on_received,
        ]:
            callback.reset_mock()

    assert_callbacks()

    result = executor.run_for_result("original message")
    assert_callbacks()
    assert result == {'i am': 'serialized'}
