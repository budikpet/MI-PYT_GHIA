from click.testing import CliRunner
from ghia import ghia
from ghia.ghia_cli_logic import ghia_run
from ghia.cli.strategy import GhiaContext
from custom_fixtures import context

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