MI-PYT_GHIA
=============
.. image:: https://travis-ci.com/budikpet/MI-PYT_GHIA.svg?token=NsX1uECKWY27k8Urnctq&branch=master
    :target: https://travis-ci.com/budikpet/MI-PYT_GHIA

MI-PYT_GHIA makes it possible to connect to an existing GitHub repository and 
automatically modify issues according to provided rules. 

It was created as a homework project of naucse.python_. Tested on TravisCI_.

.. _naucse.python: https://naucse.python.cz/2019/mipyt-zima/
.. _TravisCI: https://travis-ci.com/budikpet/MI-PYT_GHIA

To generate full documentation in HTML format use:

.. code-block:: bash

	$ make -C docs html

Tests in test/test_unit/test_http.py module use betamax to record HTTP communication into cassettes. 
There are prerecorded cassettes with HTTP communication in the repository. 
This communication was taken from the authors test repository. 

The environment is automatically reset and ready to record new cassetts using a new test repository when the tests_environment/setup.sh bash script is used. 
Original cassettes folder and test_config.cfg is not removed but it is renamed.