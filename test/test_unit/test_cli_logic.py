import pytest
from typing import List
from ghia.cli.strategy import GhiaContext, Strategies
from ghia.github.my_data_classes import Issue, GroupedUsers
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

@pytest.mark.parametrize(
    'issue', (dummies.in_any, dummies.in_label_text, dummies.in_text, dummies.in_title)
)
def test_group_users(context: GhiaContext, issue):
    issue = dummies.in_title
    result: GroupedUsers = cli_logic.group_users(context, dummies.in_title)
    users_to_assign: List[str] = result.get_users_to_assign()

    if context.strategy_name == Strategies.APPEND:
        assert len(users_to_assign) == issue.ppl_after_append
        if dummies.random_person in issue.assignees:
            assert dummies.random_person in result.users_to_leave
        assert all(user in users_to_assign for user in issue.users_to_add)
        print
    elif context.strategy_name == Strategies.CHANGE:
        assert len(users_to_assign) == issue.ppl_after_change
        if dummies.random_person in issue.assignees:
            assert dummies.random_person in result.users_to_remove
        print
    elif context.strategy_name == Strategies.SET:
        assert len(users_to_assign) == issue.ppl_after_set
        if dummies.random_person in issue.assignees:
            assert dummies.random_person in result.users_to_leave

        if len(issue.assignees) > 0:
            # No ppl were added
            assert len(users_to_assign) == len(issue.assignees)
            assert all(user in users_to_assign for user in issue.assignees)
        else:
            assert len(users_to_assign) == len(issue.users_to_add)
            assert all(user in users_to_assign for user in issue.users_to_add)

        print
    else:
        raise ValueError("Unknown strategy.")

    print