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