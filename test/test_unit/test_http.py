import pytest
from ghia.cli.strategy import GhiaContext, Strategies
from ghia.github.my_data_classes import Issue, GroupedUsers, UserStatus
from custom_fixtures import context_with_session, remove_credentials_file
from ghia.ghia_cli_logic import ghia_run

def test_ghia_run(context_with_session: GhiaContext, capfd):
    # betamax_session.get('https://httpbin.org/get')
    assert context_with_session.session is not None
    assert context_with_session.get_token() is not None and context_with_session.get_token() != ""
    assert context_with_session.get_secret() is not None and context_with_session.get_secret() != ""

    ghia_run(context_with_session)

    out, err = capfd.readouterr()
    assert err == '' or err is None
    assert out is not None

    opened_issues = 112
    assert out.count(f"-> {context_with_session.reposlug}") == opened_issues
    assert out.count(f"https://github.com/mi-pyt-ghia/budikpet/issues/") == opened_issues

    assert out.count(f"   FALLBACK: added label \"{context_with_session.get_fallback_label()}\"") == 8
    assert out.count(f"   FALLBACK: already has label \"{context_with_session.get_fallback_label()}\"") == 93

    if context_with_session.strategy_name == Strategies.APPEND:
        assert out.count("   +") == 6
        assert out.count("   =") == 8
        assert out.count("   -") == 0
    if context_with_session.strategy_name == Strategies.SET:
        assert out.count("   +") == 5
        assert out.count("   =") == 8
        assert out.count("   -") == 0
    if context_with_session.strategy_name == Strategies.CHANGE:
        assert out.count("   +") == 6
        assert out.count("   =") == 0
        assert out.count("   -") == 8

    print