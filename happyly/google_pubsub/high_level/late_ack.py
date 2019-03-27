from typing import Optional, Any

from ..high_level.base import GoogleBaseReceiver, GoogleBaseReceiveAndReply


class GoogleLateAckReceiver(GoogleBaseReceiver):
    def run(self, message: Optional[Any] = None):
        super().run(message)
        self.ack(message)


class GoogleLateAckReceiveAndReply(GoogleBaseReceiveAndReply):
    def on_finished(self, original_message: Any, error: Optional[Exception]):
        self.ack(original_message)
        super().on_finished(original_message, error)
