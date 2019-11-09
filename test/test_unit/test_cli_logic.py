import pytest
from ghia.cli.strategy import GhiaContext
from ghia.github.my_data_classes import Issue
from custom_fixtures import context, remove_credentials_file
import ghia.ghia_cli_logic as cli_logic
import dummies

@pytest.mark.parametrize(
    ['issue', 'location', 'pattern', 'should_be_found'],
    [(dummies.in_any, 'any', 'any_2', True),
     (dummies.in_text, 'text', 'text_1', True),
     (dummies.in_label_text, 'label', 'label_1', True),
     (dummies.in_title, 'title', 'title_1', True),
     (dummies.in_any, 'any', 'randomSomething', False),
     (dummies.in_text, 'title', 'text_1', False),
     ],
)
def test_pattern_matches(context: GhiaContext, issue: Issue, location: str, pattern: str, should_be_found: bool):
    assert cli_logic.patternMatches(issue, location, pattern) == should_be_found