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
The Flask web application requires FLASK_APP and GHIA_CONFIG environment variables described in :ref:`config`.


.. _githubSpecific:

GitHub specific information
-----------------------------

MI-PYT_GHIA connects to a GitHub repository using GitHub API. 
It requires these variables to authenticate:

- GITHUB_TOKEN
    - user account wide
    - used to authenticate a user against GitHub API
    - required to modify GitHub repository
    - how to set and use GITHUB_TOKEN is described `here <https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line>`_
- GITHUB_SECRET
    - repository wide
    - used by webhooks to connect to GitHub repository and listen to required events
    - how to set and use GITHUB_SECRET is described `here <https://help.github.com/en/actions/automating-your-workflow-with-github-actions/creating-and-using-encrypted-secrets>`_

.. _webhooks:

GitHub webhooks
_________________

GitHub webhooks are used by MI-PYT_GHIA flask web app to subscribe to issue-specific events from github repository. 
These events are used to trigger MI-PYT_GHIA CLI application when any trigger action occures for a specific issue.

All trigger actions are listed in :ref:`rules_file`.

Further information about webhooks, how to set them up and use them is available `here <https://developer.github.com/webhooks/>`_.