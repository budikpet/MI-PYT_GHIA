import pytest
import json
from typing import List
from ghia.cli.strategy import GhiaContext, Strategies
from ghia.github.my_data_classes import Issue, GroupedUsers, UserStatus
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
    assert cli_logic.pattern_matches(issue, location, pattern) == should_be_found

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
    else:
        raise ValueError("Unknown strategy.")

def test_output_data_labels(context: GhiaContext):
    issue = dummies.has_fallback_label
    grouped_users: GroupedUsers = cli_logic.group_users(context, issue)
    data = cli_logic.get_output_data(context, issue, grouped_users)
    assert data is None

    issue = dummies.no_fallback_label
    grouped_users: GroupedUsers = cli_logic.group_users(context, issue)
    data = cli_logic.get_output_data(context, issue, grouped_users)
    assert data is not None
    
    data = json.loads(data)
    assignees: List[str] = data.get("assignees")
    labels: List[str] = data.get("labels")
    assert labels is not None
    assert dummies.fallback_label in labels
    assert len(labels) == len(issue.labels) + 1

    if context.strategy_name == Strategies.CHANGE:
        assert len(assignees) == issue.ppl_after_change
    elif context.strategy_name == Strategies.APPEND:
        assert assignees is None or len(assignees) == issue.ppl_after_append
    elif context.strategy_name == Strategies.SET:
        assert assignees is None or len(assignees) == issue.ppl_after_set

@pytest.mark.parametrize(
    'issue', (dummies.in_any, dummies.in_label_text, dummies.in_text, dummies.in_title)
)
def test_output_data_ppl(context: GhiaContext, issue):
    grouped_users: GroupedUsers = cli_logic.group_users(context, issue)
    data = cli_logic.get_output_data(context, issue, grouped_users)
    
    if grouped_users.update_needed():
        assert data is not None
    else:
        assert data is None
        return
    
    data = json.loads(data)
    assignees: List[str] = data.get("assignees")
    labels: List[str] = data.get("labels")
    assert labels is None
    assert assignees is not None
    assert all(user in assignees for user in issue.users_to_add)

    if context.strategy_name == Strategies.APPEND:
        assert len(assignees) == issue.ppl_after_append
    if context.strategy_name == Strategies.SET:
        assert len(assignees) == issue.ppl_after_set
    if context.strategy_name == Strategies.CHANGE:
        assert len(assignees) == issue.ppl_after_change
        assert dummies.random_person not in assignees

    print


@pytest.mark.parametrize(
    ['issue', 'has_label'], [(dummies.has_fallback_label, True), (dummies.no_fallback_label, False)]
)
def test_write_label(context: GhiaContext, capfd, issue, has_label: bool):
    cli_logic.write_label(issue, context)

    out, err = capfd.readouterr()
    assert err == '' or err is None
    assert out is not None

    if has_label:
        assert out == f'   FALLBACK: already has label \"{dummies.fallback_label}\"\n'
    else:
        assert out == f'   FALLBACK: added label \"{dummies.fallback_label}\"\n'

    print

@pytest.mark.parametrize(
    "user_status", (UserStatus.ADD, UserStatus.LEAVE, UserStatus.REMOVE)
)
def test_write_user(capfd, user_status: UserStatus):
    user = "person"
    cli_logic.write_user(user_status, user)
    
    out, err = capfd.readouterr()
    assert err == '' or err is None
    assert out is not None
    assert out == f"   {user_status.value} {user}\n"
    