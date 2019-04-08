from typing import Any, Mapping
from unittest.mock import patch

import pytest

from happyly.exceptions import FetchedNoResult
from happyly import Deserializer, Serializer, StopPipeline
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
    executor = Executor(
        handler=TestHandler(), deserializer=des, publisher=None, serializer=ser
    )
    assert executor.deserializer == des
    assert executor.serializer == ser
    assert executor.publisher is None
    executor.run("original message")

    def assert_callbacks():
        on_received.assert_called_with("original message")
        on_deserialized.assert_called_with(
            original_message="original message", parsed_message={'spam': 'eggs'}
        )
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
def test_serialization_failure(
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
    error = KeyError('123')

    class TestDeser(Deserializer):
        def deserialize(self, message: Any) -> Mapping[str, Any]:
            raise error

        def build_error_result(
            self, message: Any, error: Exception
        ) -> Mapping[str, Any]:
            return {"SPAM": "EGGS"}

    des = TestDeser()
    executor = Executor(handler=TestHandler(), deserializer=des, publisher=None)
    executor.run("orig")

    def assert_callbacks():
        on_received.assert_called_with("orig")
        on_deserialized.assert_not_called()
        on_deserialization_failed.assert_called_with(message="orig", error=error)
        handler.assert_not_called()
        on_handled.assert_not_called()
        on_handling_failed.assert_not_called()
        on_serialized.assert_called_with(
            original="orig",
            deserialized=None,
            result=HandlingResult.err({'SPAM': 'EGGS'}),
            serialized={'SPAM': 'EGGS'},
        )
        on_serialization_failed.assert_not_called()
        on_published.assert_not_called()
        on_publishing_failed.assert_not_called()
        on_finished.assert_called_with(original_message="orig", error=None)
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
    result = executor.run_for_result("orig")
    assert_callbacks()
    assert result == {'SPAM': 'EGGS'}


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
def test_serialization_fallback_failure(
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
    error = KeyError('123')

    class TestDeser(Deserializer):
        def deserialize(self, message: Any) -> Mapping[str, Any]:
            raise error

    des = TestDeser()
    executor = Executor(handler=TestHandler(), deserializer=des, publisher=None)
    executor.run("orig")

    def assert_callbacks():
        on_received.assert_called_with("orig")
        on_deserialized.assert_not_called()
        on_deserialization_failed.assert_called_with(message="orig", error=error)
        handler.assert_not_called()
        on_handled.assert_not_called()
        on_handling_failed.assert_not_called()
        on_serialized.assert_not_called()
        on_serialization_failed.assert_not_called()
        on_published.assert_not_called()
        on_publishing_failed.assert_not_called()
        on_finished.assert_called_with(original_message="orig", error=error)
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
    with pytest.raises(FetchedNoResult):
        executor.run_for_result("orig")
    assert_callbacks()


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
    return_value=HandlingResult.err({'error': 42}),  # type: ignore
)
def test_handling_status_err(
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
    executor.run({"orig": 'msg'})

    def assert_callbacks():
        on_received.assert_called_with({"orig": 'msg'})
        on_deserialized.assert_called_with(
            original_message={"orig": 'msg'}, parsed_message={"orig": 'msg'}
        )
        on_deserialization_failed.assert_not_called()
        handler.assert_called_with({'orig': 'msg'})
        on_handled.assert_called_with(
            original_message={'orig': 'msg'},
            parsed_message={'orig': 'msg'},
            result=HandlingResult.err({'error': 42}),
        )
        on_handling_failed.assert_not_called()
        on_serialized.assert_called_with(
            original={'orig': 'msg'},
            deserialized={'orig': 'msg'},
            result=HandlingResult.err({'error': 42}),
            serialized={'error': 42},
        )
        on_serialization_failed.assert_not_called()
        on_published.assert_not_called()
        on_publishing_failed.assert_not_called()
        on_finished.assert_called_with(original_message={"orig": 'msg'}, error=None)
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
    result = executor.run_for_result({"orig": 'msg'})
    assert_callbacks()
    assert result == {'error': 42}


_ERR = KeyError('123')


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
@patch('test_executor.TestHandler.__call__', side_effect=_ERR)  # type: ignore
def test_handling_fallback_fails(
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
    executor.run({"orig": 'msg'})

    def assert_callbacks():
        on_received.assert_called_with({"orig": 'msg'})
        on_deserialized.assert_called_with(
            original_message={"orig": 'msg'}, parsed_message={"orig": 'msg'}
        )
        on_deserialization_failed.assert_not_called()
        handler.assert_called_with({'orig': 'msg'})
        on_handled.assert_not_called()
        on_handling_failed.assert_called_with(
            original_message={'orig': 'msg'}, parsed_message={'orig': 'msg'}, error=_ERR
        )
        on_serialized.assert_not_called()
        on_serialization_failed.assert_not_called()
        on_published.assert_not_called()
        on_publishing_failed.assert_not_called()
        on_finished.assert_called_with(original_message={"orig": 'msg'}, error=_ERR)
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
    with pytest.raises(FetchedNoResult):
        executor.run_for_result({"orig": 'msg'})
    assert_callbacks()


_STOP = StopPipeline('reason')


@patch('test_executor.Executor.on_received', side_effect=_STOP)
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
def test_stop_on_received(
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
    executor = Executor(
        handler=TestHandler(), deserializer=des, publisher=None, serializer=ser
    )
    assert executor.deserializer == des
    assert executor.serializer == ser
    assert executor.publisher is None
    executor.run("original message")

    def assert_callbacks():
        on_received.assert_called_with("original message")
        on_deserialized.assert_not_called()
        on_deserialization_failed.assert_not_called()
        handler.assert_not_called()
        on_handled.assert_not_called()
        on_handling_failed.assert_not_called()
        on_serialized.assert_not_called()
        on_serialization_failed.assert_not_called()
        on_published.assert_not_called()
        on_publishing_failed.assert_not_called()
        on_finished.assert_not_called()
        on_stopped.assert_called_with(
            original_message="original message", reason='reason'
        )

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
    with pytest.raises(FetchedNoResult):
        executor.run_for_result("original message")
    assert_callbacks()


@patch('test_executor.Executor.on_received')
@patch('test_executor.Executor.on_deserialized', side_effect=_STOP)
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
def test_stop_on_deserialized(
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
    executor = Executor(
        handler=TestHandler(), deserializer=des, publisher=None, serializer=ser
    )
    assert executor.deserializer == des
    assert executor.serializer == ser
    assert executor.publisher is None
    executor.run("original message")

    def assert_callbacks():
        on_received.assert_called_with("original message")
        on_deserialized.assert_called_with(
            original_message='original message', parsed_message={'spam': 'eggs'}
        )
        on_deserialization_failed.assert_not_called()
        handler.assert_not_called()
        on_handled.assert_not_called()
        on_handling_failed.assert_not_called()
        on_serialized.assert_not_called()
        on_serialization_failed.assert_not_called()
        on_published.assert_not_called()
        on_publishing_failed.assert_not_called()
        on_finished.assert_not_called()
        on_stopped.assert_called_with(
            original_message="original message", reason='reason'
        )

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
    with pytest.raises(FetchedNoResult):
        executor.run_for_result("original message")
    assert_callbacks()
