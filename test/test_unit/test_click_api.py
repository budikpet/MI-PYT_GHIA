from click.testing import CliRunner
from ghia import ghia
from ghia.ghia_cli_logic import ghia_run
from ghia.cli.strategy import GhiaContext
from custom_fixtures import context_with_session, remove_credentials_file

def test_help():
    runner = CliRunner()
    result = runner.invoke(ghia, ['--help'])
    assert result.exit_code == 0
    assert 'Usage: ghia [OPTIONS] REPOSLUG' in result.output
    assert '-s' in result.output
    assert '-a' in result.output
    assert '-r' in result.output