Concepts
========


Handler
-------

*Handler* is the main concept of all Happyly library.
Basically a handler is a callable which implements business logic, and nothing else:


* No serialization/deserialiation here
* No sending stuff over the network
* No message queues' related stuff

Let the handler do its job!

To create a handler you can simply define a function which takes a :code:`dict` as an input
and returns a :code:`dict`:

.. code-block:: python

  def handle_my_stuff(message: dict):
      try
          db.update(message['user'], message['status'])
          return {
              'request_id': message['request_id'],
              'action': 'updated',
          }
      except Exception:
          return {
              'action': 'failed'
          }

Done! This handler can be plugged into your application:
whether it uses Flask or Celery or whatever.

Note that you are allowed to return nothing
if you don't actually need a result from your handler.
This handler is also valid:

.. code-block:: python

  def handle_another_stuff(message: dict):
      try
          neural_net.start_job(message['id'])
          _LOGGER.info('Job created')
      except Exception:
          _LOGGER.warning('Failed to create a job')

If you prefer class-based approach, Happyly can satisfy you too.
Subclass :meth:`happyly.Handler` and implement the following methods:

.. code-block:: python

  class MyHandler(happyly.Handler):

      def handle(message: dict)
          db.update(message['user'], message['status'])
          return {
              'request_id': message['request_id'],
              'action': 'updated',
          }

      def on_handling_failed(message: dict, error)
          return {
              'action': 'failed'
          }

Instance of :code:`MyHandler` is equivalent to :code:`handle_my_stuff`

Executor
--------

To plug a handler into your application you will need :meth:`happyly.Executor`
(or one of its subclasses).

Executor brings the handler into a context of more pipeline steps:

.. image:: images/run.png
   :width: 300

So a typical construction of an Executor looks like this:

.. code-block:: python

  my_executor = Executor(
    deserializer=...
    handler=...
    serializer=...
    publisher=...
  )

Executor implements two crucial methods: :code:`run()`
and :code:`run_for_result()`.
:code:`run(message)` starts an execution pipeline for the provided message.
:code:`run()` returns nothing but can optionally publish a serialized result of
handling.
If you'd like to deal with the result by yourself, use :code:`run_for_result()`
which returns a serialized result of handling.

Executor manages all the stages of the pipeline,
including situation when some stage fails.
But the implementation of any stage itself (deserialization, handling,
serialization, publishing) is provided to a constructor
during executor instantiation.

Let's take a deeper look at these stages.

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

