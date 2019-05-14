from typing import Any

from happyly.pubsub import BasePublisher


class GooglePubSubPublisher(BasePublisher):
    """
    Publisher for Google Pub/Sub.
    Synchronously publishes the provided message to given topic.
    """

    def __init__(self, project: str, to_topic: str):
        try:
            from google.cloud import pubsub_v1
        except ImportError:
            raise ImportError(
                'Please install google-cloud-pubsub to use this component'
            )

        super().__init__()
        self.project = project
        self.to_topic = to_topic
        self._publisher_client = pubsub_v1.PublisherClient()

    def publish(self, serialized_message: Any):
        future = self._publisher_client.publish(
            f'projects/{self.project}/topics/{self.to_topic}', serialized_message
        )
        try:
            future.result()
            return
        except Exception as e:
            raise e
