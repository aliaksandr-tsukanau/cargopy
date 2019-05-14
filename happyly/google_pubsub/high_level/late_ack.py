from typing import Optional, Any

from happyly._deprecations.utils import will_be_removed

from ..high_level.base import GoogleBaseReceiver, GoogleBaseReceiveAndReply


class GoogleLateAckReceiver(GoogleBaseReceiver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        will_be_removed(
            'GoogleLateAckReceiver',
            'ExecutorWithAck or GooglePubSubExecutorWithRequestId',
            '0.11.0',
        )

    def on_finished(self, original_message: Any, error: Optional[Exception]):
        self.ack(original_message)
        super().on_finished(original_message, error)


class GoogleLateAckReceiveAndReply(GoogleBaseReceiveAndReply):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        will_be_removed(
            'GoogleLateAckReceiveAndReply',
            'ExecutorWithAck or GooglePubSubExecutorWithRequestId',
            '0.11.0',
        )

    def on_finished(self, original_message: Any, error: Optional[Exception]):
        self.ack(original_message)
        super().on_finished(original_message, error)
