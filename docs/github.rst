.. _githubSpecific:

GitHub specific information
=============================

MI-PYT_GHIA connects to a GitHub repository using GitHub API. 
It requires these variables to authenticate:

- GITHUB_TOKEN
    - user account wide
    - used to authenticate a user against GitHub API
    - required to modify GitHub repository
    - how to set and use GITHUB_TOKEN is described `here <https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line>`__
- GITHUB_SECRET
    - repository wide
    - used by webhooks to connect to GitHub repository and listen to required events
    - how to set and use GITHUB_SECRET is described `here <https://help.github.com/en/actions/automating-your-workflow-with-github-actions/creating-and-using-encrypted-secrets>`__

.. _webhooks:

GitHub webhooks
-------------------

GitHub webhooks are used by MI-PYT_GHIA flask web app to subscribe to issue-specific events from github repository. 
These events are used to trigger MI-PYT_GHIA CLI application when any trigger action occures for a specific issue.

All trigger actions are listed in :ref:`rules_file`.

Further information about webhooks, how to set them up and use them is available `here <https://developer.github.com/webhooks/>`_.