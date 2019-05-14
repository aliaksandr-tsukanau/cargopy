Installation
============

Happyly is hosted on PyPI, so you can use:

.. code-block:: bash

  pip install happyly

There are extra dependencies for some components.

Happyly with Google Pub/Sub components are to be installed this way:

.. code-block:: bash

  pip install happyly[google-cloud-pubsub]

If you want to use Happyly's components for Flask, install it like this:

.. code-block:: bash

  pip install happyly[flask]

There is also an extra dependency which enables cached components via Redis.
If you need it, install Happyly like this:

.. code-block:: bash

  pip install happyly[redis]
