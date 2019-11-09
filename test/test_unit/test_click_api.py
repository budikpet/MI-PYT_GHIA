from click.testing import CliRunner
from configparser import ConfigParser
import betamax
import pytest
import os
from ghia import ghia
from ghia.cli.strategy import GhiaContext, Strategies
from ghia.github.config_data import ConfigData

fixtures_path = f"{os.path.dirname(os.path.abspath(__file__))}/fixtures"
tmp_credentials_path = f"{fixtures_path}/tmp_credentials.cfg"

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
        config.default_cassette_options['record_mode'] = 'all'
    else:
        # Do not attempt to record sessions with bad fake token
        config.default_cassette_options['record_mode'] = 'none'

    # Create a temporary credentials file
    with open(tmp_credentials_path, "w+") as credentials_file:
        credentials_file.writelines(["[github]\n", f'token={TOKEN}\n', f'secret={SECRET}\n'])

    # Hide the token in the cassettes
    config.define_cassette_placeholder('<TOKEN>', TOKEN)
    config.define_cassette_placeholder('<SECRET>', SECRET)

@pytest.fixture
def context(betamax_session):
    config_auth, config_rules = ConfigParser(), ConfigParser()
    with open(f"{fixtures_path}/rules.cfg") as rules_file:
        config_rules.read_file(rules_file)

    with open(tmp_credentials_path) as credentials_file:
        config_auth.read_file(credentials_file)

    yield GhiaContext("https://api.github.com", strategy=Strategies.APPEND.name, dry_run=True, 
        config_auth=config_auth, config_rules=config_rules, reposlug="mi-pyt-ghia/budikpet", session=betamax_session)

    os.remove(tmp_credentials_path)
    print("Temporary credentials file removed.")

def test_context(context: GhiaContext):
    # betamax_session.get('https://httpbin.org/get')
    assert context.base == "https://api.github.com"
    assert context.session is not None
    assert context.get_token() is not None and context.get_token() != ""
    assert context.get_secret() is not None and context.get_secret() != ""

def test_help():
    runner = CliRunner()
    result = runner.invoke(ghia, ['--help'])
    assert result.exit_code == 0
    assert 'Usage: ghia [OPTIONS] REPOSLUG' in result.output
    assert '-s' in result.output
    assert '-a' in result.output
    assert '-r' in result.output