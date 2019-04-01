from typing import Optional, Any

from .base import GoogleBaseReceiver, GoogleBaseReceiveAndReply


class GoogleEarlyAckReceiver(GoogleBaseReceiver):
    def _after_on_received(self, message: Optional[Any]):
        self.ack(message)
        super()._after_on_received(message)


class GoogleEarlyAckReceiveAndReply(GoogleBaseReceiveAndReply):
    def _after_on_received(self, message: Optional[Any]):
        self.ack(message)
        super()._after_on_received(message)
