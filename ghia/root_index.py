from flask import Blueprint, render_template, current_app, request, abort, Response
from jinja2 import Markup
import hmac
import hashlib
import json
from ghia.cli.strategy import Strategies, GhiaContext
from ghia.github.my_data_classes import Rules, RuleLocation
from ghia.ghia_cli_logic import ghia_run

bp_root = Blueprint('bp_root', __name__, template_folder='templates')

def get_ghia_context() -> GhiaContext:
    """
    
    Returns:
        GhiaContext: The context from the apps' config.
    """    
    return current_app.config["GHIA_CONTEXT"]

def get_color(string: str) -> str:
    """
    
    Args:
        string (str): Name of a Rule.
    
    Returns:
        str: A string representing a color.
    """  

    try:
        return Rules[string.upper()].value.color
    except KeyError:
        return "grey"

@bp_root.app_template_filter('in_block')
def in_block(string: str):
    """
    A filter that creates a badge with an appropriate title and color.
    
    Args:
        string (str): Rule name.
    
    Returns:
        Markup: The Markup for HTML.
    """    
    color = get_color(string)
    result = f'<span class="badge badge-secondary" style="background-color: {color};">{string}</span>'
    return Markup(result)

@bp_root.app_template_filter('github_url')
def convert_time(username: str):
    """
    Properly sets up the GitHub repository URL.
    
    Args:
        username (str): username string
    
    Returns:
        Markup: The Markup for HTML.
    """    
    result = f'<a href="https://github.com/{username}">{username}</a>'

    return Markup(result)

@bp_root.route('/')
def index():
    """ Renders the HTML template. """
    return render_template("index.html", context=get_ghia_context())

def check_secret(context: GhiaContext) -> bool:
    """
    Checks whether the request is properly authenticated.
    
    Args:
        context (GhiaContext): [description]
    
    Returns:
        bool: True if the request came from GitHub API and is properly authenticated.
    """    
    headers = request.headers.environ
    payload = request.data

    secret = context.get_secret()
    secret_hash = headers.get("HTTP_X_HUB_SIGNATURE").split("=")[1]

    key = bytes(secret, 'utf-8')
    digester = hmac.new(key=key, msg=payload, digestmod=hashlib.sha1)
    signature = digester.hexdigest()

    if not hmac.compare_digest(str(signature), str(secret_hash)):
        current_app.logger.warning(f"HASH_NO_MATCH: {signature} != {secret_hash}")
        return False

    return True

@bp_root.route('/', methods=["POST"])
def labels_hook() -> str:
    """
    Handles the labels and ping GitHub webhooks.

    - Gets all event from the GitHub webhook
    - Checks authentication
    - Checks event type
        - if PING event then only returns a positive answer
        - if ISSUE event that fits trigger_actions then runs GHIA CLI app for the received issue only 
    
    Returns:
        str: String that should be returned as a response.
    """

    current_app.logger.warning('labels_webhook triggered')
    headers = request.headers
    context: GhiaContext = get_ghia_context()

    if context.get_secret() is not None and not check_secret(context):
    # if False == True:    #TODO: Remove
        abort(Response(response="Secrets do not match.", status=403))
    elif request.content_type != "application/json":
        abort(Response(response="Accepts only JSON.", status=400))

    new_reposlug = request.json["repository"]["full_name"]
    if context.reposlug is None or context.reposlug != new_reposlug:
        context.reposlug = new_reposlug

    if headers.environ["HTTP_X_GITHUB_EVENT"] == "issues":
        # Handle issues endpoint
        current_app.logger.warning('Issues endpoint handler started.')

        if request.json["action"] not in context.get_trigger_actions() or request.json["issue"]["state"] != "open":
            return "This issue doesn't need to be checked."

        number = request.json["issue"]["number"]
        ghia_run(context, number)
        return "GHIA_CLI changed issues according to rules."
    elif headers.environ["HTTP_X_GITHUB_EVENT"] == "ping":
        # Handle ping endpoint
        return "I was pinged. I am triggered now."
    
    return "Supports only Github endpoints these github endpoints: [issues, ping]"