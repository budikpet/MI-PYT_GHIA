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

.. _config:

Configuration
---------------

These environment variables are required:

- FLASK_APP
    - location of the module which creates the flask app (here ghia/ghia.py)
- GHIA_CONFIG
    - locations of both credentials and rules config files
    - delimiter is ':'

MI-PYT_GHIA also requires a few configuration files to run.

.. _credentials_file:

Credentials configuration file
________________________________

Contains GITHUB_TOKEN and GITHUB_SECRET variables. 
These variables require an additional setup in GitHub account and repository. 
They need to remain secret so this file mustn't be pushed to a GitHub repository.
Additional information available at :ref:`githubSpecific`.

.. literalinclude:: _static/cfgs/credentials_sample.cfg
	:language: ini

.. _rules_file:

Rules configuration file
_____________________________

Contains rules which determine how the programme modifies the GitHub repository.
Patterns use regex of the 're' library that can be located in specific locations.

.. literalinclude:: _static/cfgs/rules_sample.cfg
	:language: ini

.. _usage:

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

The application needs :ref:`credentials_file` and :ref:`rules_file`.

If no fallback label is specified, it isn't used.

The application uses strategies to change the way modifications are done. These strategies are:

- Append
    - users are assigned to an issue if matched by rules
- Set
    - users are assigned to an issue if matched by rules
    - the issue mustn't have any users assigned already
- Change
    - users are assigned to an issue if matched by rules
    - users that shouldn't be assigned by rules are unassigned

Flask web application
________________________

Shows HTML web page with basic information about GHIA. It also handles :ref:`webhooks`. 
The Flask web application requires FLASK_APP and GHIA_CONFIG environment variables described in :ref:`config`.