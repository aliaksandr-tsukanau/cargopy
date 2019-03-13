from typing import Any

from google.cloud import pubsub_v1

from happyly.pubsub import Publisher


class GooglePubSubPublisher(Publisher):
    def __init__(self, project, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project
        self._publisher_client = pubsub_v1.PublisherClient()

    def __attrs_post_init__(self):
        self._publisher_client = pubsub_v1.PublisherClient()

    def publish_message(self, serialized_message: Any, to: str):
        future = self._publisher_client.publish(
            f'projects/{self.project}/topics/{to}', serialized_message
        )
        try:
            future.result()
            return
        except Exception as e:
            raise e
