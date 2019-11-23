Doctests
======================

.. testsetup::

    from ghia.github.config_data import ConfigData
    from configparser import ConfigParser
    import json

    with open("_static/json/example_issue.json", "r") as example_issue:
        issue_json_dict = json.load(example_issue)

    cred_cfg_parser, rules_cfg_parser = ConfigParser(), ConfigParser()
    with open("_static/cfgs/credentials_sample.cfg", "r") as cred_file, open("_static/cfgs/rules_sample.cfg", "r") as rules_file:
        cred_cfg_parser.read_file(cred_file)
        rules_cfg_parser.read_file(rules_file)

ConfigData
------------

Takes care of parsing all information from configuration files. Lets give it configuration files shown in :ref:`config`.

.. doctest::

    >>> config_data: ConfigData = ConfigData(cred_cfg_parser, rules_cfg_parser)
    
    >>> config_data.token
    'someTokenValue'

    >>> config_data.secret
    'someSecretValue'

    >>> config_data.user_patterns["title"]
    [('network', 'mareksuchanek')]

    >>> config_data.user_patterns_by_user["hroncok"]
    [('any', 'Python')]

    >>> config_data.fallback_label
    'Need assignment'

Matching rules for users of an issue
--------------------------------------

The first step after receiving issues from GitHub API is to use the provided rules to determine which users should
be assigned, removed and left alone. That is done by :meth:`ghia.ghia_cli_logic.group_users` 
which returns a :class:`ghia.github.my_data_classes.GroupedUsers` object.

Lets use a following GitHub issue:

.. literalinclude:: _static/json/example_issue.json
    :language: json

The resulting :class:`ghia.github.my_data_classes.GroupedUsers` object is influenced by rules configuration
and the strategy used. Information about all strategies is available in :ref:`usage`.

Let's setup :class:`ghia.github.my_data_classes.Issue` object and :class:`ghia.cli.strategy.GhiaContext` objects with
different strategies:

.. testcode::

    from ghia.github.my_data_classes import Issue, GroupedUsers
    from ghia.cli.strategy import GhiaContext, Strategies
    from ghia.ghia_cli_logic import group_users

    issue: Issue = Issue(issue_json_dict)
    
    set_context = GhiaContext(base="https://api.github.com", 
        strategy="set", dry_run=True, 
        config_auth=cred_cfg_parser, 
        config_rules=rules_cfg_parser, 
        reposlug="user/repo", session=None)

    append_context = GhiaContext(base="https://api.github.com", 
        strategy="append", dry_run=True, 
        config_auth=cred_cfg_parser, 
        config_rules=rules_cfg_parser, 
        reposlug="user/repo", session=None)

    change_context = GhiaContext(base="https://api.github.com", 
        strategy="change", dry_run=True, 
        config_auth=cred_cfg_parser, 
        config_rules=rules_cfg_parser, 
        reposlug="user/repo", session=None)

    set_res: GroupedUsers = group_users(set_context, issue)
    append_res: GroupedUsers = group_users(append_context, issue)
    change_res: GroupedUsers = group_users(change_context, issue)

Then by using the same issue and rules with different strategies:

.. testcode::
    
    print("Add both users, leave already assigned user:")
    print(append_res.get_output_list())
    print()

    print("Leave already assigned user:")
    print(set_res.get_output_list())
    print()

    print("Add both users, remove already assigned user:")
    print(change_res.get_output_list())

Will generate this output:

.. testoutput::

    Add both users, leave already assigned user:
    [(<UserStatus.ADD: '+'>, 'hroncok'), (<UserStatus.ADD: '+'>, 'mareksuchanek'), (<UserStatus.LEAVE: '='>, 'Person1')]

    Leave already assigned user:
    [(<UserStatus.LEAVE: '='>, 'Person1')]

    Add both users, remove already assigned user:
    [(<UserStatus.ADD: '+'>, 'hroncok'), (<UserStatus.ADD: '+'>, 'mareksuchanek'), (<UserStatus.REMOVE: '-'>, 'Person1')]