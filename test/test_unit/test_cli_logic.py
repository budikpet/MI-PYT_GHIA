from ghia.cli.strategy import GhiaContext
from custom_fixtures import context
import ghia.ghia_cli_logic

def test_pattern_matches(context: GhiaContext, issue, should_be_found: bool):
    print