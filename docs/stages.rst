.. _stages_section:

Stages
======

Deserializer
------------

The simplest deserializer is a function which
takes a received message and returns a dict of attributes.

Here is an imaginary example:

.. code-block:: python

    def get_attributes_from_my_message(message):
        data = message.get_bytes().decode('utf-8')
        return json.loads(data)

You'll need a different deserializer for different
message transport technologies or serialization formats.

The same deserializer can be written as a class:

.. code-block:: python

    class MyDeserializer(happyly.Deserializer):
        def deserialize(self, message):
            data = message.get_bytes().decode('utf-8')
            return json.loads(data)

A class-based deserializer can implement a fallback method
that constructs an error result:

.. code-block:: python

    class MyDeserializer(happyly.Deserializer):
        def deserialize(self, message):
            data = message.get_bytes().decode('utf-8')
            return json.loads(data)

        def build_error_result(self, message, error):
            return {'status': 'failed', 'error': repr(error)}

Note that if deserialization fails, then handling is skipped
and the return value of :code:`build_error_result` is used
as a result of handling.

Class-based deserializer are also useful for parametrization,
e.g. with message schemas.

Serializer
----------

Serialization happens to the result provided by handler.
This step is optional.
It is useful when publishing occurs, or when the value is retrieved
with :code:`Executor.run_for_result()`.

The simplest serializer is a function that takes
:code:`dict` as an input and returns... well, whatever you need.

.. code-block:: python

    def prepare_response(message_attributes):
        resp = flask.jsonify(message_attributes)
        if 'error' in attributes:
            resp.status = 400
        return resp


As usual, there is a class-based approach:

.. code-block:: python

    class MySerializer(happyly.Serializer):

        def serialize(message_attributes):
            resp = flask.jsonify(message_attributes)
            if 'error' in attributes:
                resp.status = 400
            return resp

Publisher
---------

After result is serialized it can be either returned
(if :code:`Executor.run_for_result()` is used) or published
(if :code:`Executor.run()` is used).
Note that publishing is an optional step - executor that just does the things
without sending a message is a valid one too.

Publisher can be defined as a function which takes the only argument -
a serialized message.

.. code-block:: python

    def publish_my_result(serialized_message):
        my_client.publish_a_message(serialized_message)

If you'd like a class-based approach,
please subclass :meth:`happyly.BasePublisher`.
Here's how one of the Happyly's components is implemented:

.. code-block:: python

    class GooglePubSubPublisher(happyly.BasePublisher):
        def publish(self, serialized_message: Any):
            future = self._publisher_client.publish(
                f'projects/{self.project}/topics/{self.to_topic}', serialized_message
            )
            try:
                future.result()
                return
            except Exception as e:
                raise e

        def __init__(self, project: str, to_topic: str):
            super().__init__()
            self.project = project
            self.to_topic = to_topic
            self._publisher_client = pubsub_v1.PublisherClient()
