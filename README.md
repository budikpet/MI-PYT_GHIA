# MI-PYT_GHIA
Work repository of [naucse.python](https://naucse.python.cz/2019/mipyt-zima/) homework [GHIA](https://github.com/cvut/ghia/tree/basic).

Tests in test/test_unit/test_http.py module use betamax to record HTTP communication into cassettes. There are prerecorded cassettes with HTTP communication in the repository. This communication was taken from the authors test repository. 

The environment is automatically reset and ready to record new cassetts using a new test repository when the tests_environment/setup.sh bash script is used. Original cassettes folder and test_config.cfg is not removed but it is renamed.
