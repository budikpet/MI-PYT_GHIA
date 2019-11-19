from custom_fixtures import testapp, context
from ghia.cli.strategy import GhiaContext 

def get_context(app) -> GhiaContext:
    context: GhiaContext = app.application.config["GHIA_CONTEXT"]
    assert context is not None

    assert context.username is not None
    assert context.reposlug is not None
    assert context.base is not None

    return context

def test_basic(testapp):
    assert testapp is not None
    context: GhiaContext = get_context(testapp)

    data: str = testapp.get('/').get_data(as_text=True)
    
    assert data is not None and data != ""
    assert context.username in data
    assert f"http://{context.username}.pythonanywhere.com/" in data
    assert context.get_fallback_label() in data

    print