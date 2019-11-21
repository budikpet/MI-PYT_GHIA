Getting started
==================

Installation
--------------

.. code-block:: bash

    $ pip install --extra-index-url https://test.pypi.org/pypi ghia_budikpet

All required dependencies are also installed. MI-PYT_GHIA requires these packages to run:

- Click
- Requests
- Flask

Configuration
---------------

MI-PYT_GHIA requires these configuration files to run:

Rules configuration file
_____________________________

.. literalinclude:: _static/cfgs/rules_sample.cfg
	:language: ini

Credentials configuration file
________________________________

.. literalinclude:: _static/cfgs/credentials_sample.cfg
	:language: ini

How to use
------------

CLI application
_________________

Handles connecting to a GitHub repository and all automated modification of issues.

Check how to use the CLI application using:

.. code-block:: bash

    $ python -m ghia --help

    ############ OR ################

    $ ghia --help

Flask web application
________________________

Shows HTML web page with basic information about GHIA. It also handles :ref:`webhooks`.

The Flask web application requires these environment variables:

- FLASK_APP
    - location of the module which creates the flask app (here ghia/ghia.py)
- GHIA_CONFIG
    - locations of both credentials and rules config files
    - delimiter is ':'


GitHub specific information
-----------------------------


.. _webhooks:

GitHub webhooks
_________________