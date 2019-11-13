from custom_fixtures import testapp, context
from ghia.cli.strategy import GhiaContext 

def test_basic(testapp):
    context: GhiaContext = testapp.application.config["GHIA_CONTEXT"]
    # assert 'Hello' in testapp.get('/').get_data(as_text=True)
    assert testapp is not None
    assert context is not None

    assert context.username is not None
    assert context.reposlug is not None
    assert context.base is not None

    data: str = testapp.get('/').get_data(as_text=True)
    
    assert data is not None and data != ""
    assert context.username in data

    print