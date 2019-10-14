from flask import Blueprint, render_template, current_app, request
from jinja2 import Markup
from strategy import Strategies, GhiaContext
from my_data_classes import Rules, RuleLocation

bp_root = Blueprint('bp_root', __name__, template_folder='templates')

def get_ghia_context() -> GhiaContext:
    return current_app.config["GHIA_CONTEXT"]

def get_color(string):
    try:
        return Rules[string.upper()].value.color
    except KeyError:
        return "grey"

@bp_root.app_template_filter('in_block')
def in_block(string: str):
    color = get_color(string)
    result = f'<span class="badge badge-secondary" style="background-color: {color};">{string}</span>'
    return Markup(result)

@bp_root.app_template_filter('github_url')
def convert_time(username: str):
    result = f'<a href="https://github.com/{username}">{username}</a>'

    return Markup(result)

@bp_root.route('/')
def index():
    context = get_ghia_context()

    return render_template("index.html", context=get_ghia_context())

def trigger_ghia_cli():
    test = request
    current_app.logger.warning(test)
    with open("data.json", "w") as data:
        with open("headers", "w") as headersfile:
            data.write(request.data.decode("utf-8"))
            headersfile.writelines([f'{name, currData}\n' for name, currData in request.headers.environ.items()])
    print

@bp_root.route('/', methods=["POST"])
def labels_hook():
    current_app.logger.warning('labels_webhook triggered')
    headers = request.headers

    if headers.environ["HTTP_X_GITHUB_EVENT"] == "issues":
        # Handle issues endpoint
        current_app.logger.warning('Issues endpoint handler started.')
        trigger_ghia_cli()
        return "GHIA_CLI started."
    elif headers.environ["HTTP_X_GITHUB_EVENT"] == "ping":
        # Handle ping endpoint
        current_app.logger.warning('Ping endpoint handler started.')
        return "I was pinged. I am triggered now."
    
    return "Supports only issues and ping Github endpoints."