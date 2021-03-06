from configparser import ConfigParser
import betamax
import pytest
import os
from ghia.ghia import inputStrategies
from ghia.cli.strategy import GhiaContext, Strategies
from ghia.github.config_data import ConfigData

fixtures_path = f"{os.path.dirname(os.path.abspath(__file__))}/fixtures"
tmp_credentials_path = f"{fixtures_path}/tmp_credentials.cfg"

def create_tmp_credentials(TOKEN: str = "XXX", SECRET: str = "XXX"):
    with open(tmp_credentials_path, "w+") as credentials_file:
        credentials_file.writelines(["[github]\n", f'token={TOKEN}\n', f'secret={SECRET}\n'])

with betamax.Betamax.configure() as config:
    cassettes_lib = f'{fixtures_path}/cassettes'

    if(not os.path.isdir(cassettes_lib)):
        os.mkdir(cassettes_lib)

    # tell Betamax where to find the cassettes
    config.cassette_library_dir = cassettes_lib
    env_configs = "CREDENTIALS_FILE"

    TOKEN = SECRET = "xxx"

    if env_configs in os.environ:
        # Credentials file exists
        with open(os.environ[env_configs]) as credentials_file:
            credentials = ConfigParser()
            credentials.read_file(credentials_file)
            data = ConfigData(credentials)
            TOKEN = data.token
            SECRET = data.secret
        
        # Always re-record the cassetes
        # https://betamax.readthedocs.io/en/latest/record_modes.html
        config.default_cassette_options['record_mode'] = 'once'
    else:
        # Do not attempt to record sessions with bad fake token
        config.default_cassette_options['record_mode'] = 'none'

    # Create a temporary credentials file
    create_tmp_credentials(TOKEN, SECRET)

    # Hide the token in the cassettes
    config.define_cassette_placeholder('<TOKEN>', TOKEN)
    config.define_cassette_placeholder('<SECRET>', SECRET)

def get_configs(credentials_path: str, rules_path: str):
    config_auth, config_rules = ConfigParser(), ConfigParser()
    with open(rules_path) as rules_file:
        config_rules.read_file(rules_file)

    with open(credentials_path) as credentials_file:
        config_auth.read_file(credentials_file)

    return config_auth, config_rules

def get_github_data():
    """  
        Reads test_config.cfg 

        Returns (base, reposlug).
        
    """
    parser = ConfigParser()
    with open(f"{fixtures_path}/test_config.cfg", "r") as github_config:
        parser.read_file(github_config)
    
    return parser["github"]["base"], parser["github"]["reposlug"]

@pytest.fixture(params=(inputStrategies))
def context_with_session(betamax_parametrized_session, request):
    """ 
        Creates a dry_run context with betamax session. 

        Used mainly for unit tests which have recorded HTTP communication with the real API.
    
    """
    base, reposlug = get_github_data()
    config_auth, config_rules = get_configs(tmp_credentials_path, f"{fixtures_path}/rules_http.cfg")
    
    return GhiaContext(base, strategy=request.param, dry_run=True, 
        config_auth=config_auth, config_rules=config_rules, reposlug=reposlug, session=betamax_parametrized_session)

@pytest.fixture(params=(inputStrategies))
def context(request):
    """ 
        Creates a dry_run context without any session. 

        Used mainly for unit tests which use dummies.
    """
    base, reposlug = get_github_data()
    config_auth, config_rules = get_configs(f'{fixtures_path}/dummy_credentials.cfg', f"{fixtures_path}/rules_unit.cfg")
    
    return GhiaContext(base, strategy=request.param, dry_run=True, 
        config_auth=config_auth, config_rules=config_rules, reposlug=reposlug, session=None)

@pytest.fixture
def testapp(context):
    from ghia import create_app

    context.username = "test_username"
    app = create_app(context=context)
    app.config['TESTING'] = True
    return app.test_client()

@pytest.fixture(scope='session', autouse=True)
def remove_credentials_file():
    # Will be executed at the start of the whole test session
    
    yield True
    # Will be executed at the end of the whole test session
    # os.remove(tmp_credentials_path)
    # print("Temporary credentials file removed.")