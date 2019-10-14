from flask import Blueprint, render_template, current_app, request, abort, Response
from jinja2 import Markup
from strategy import Strategies, GhiaContext
from my_data_classes import Rules, RuleLocation
import hmac
import hashlib
import json

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

def check_secret():
    headers = request.headers.environ
    payload = request.data

    secret = current_app.config["GHIA_CONTEXT"].get_secret()
    secret_hash = headers.get("HTTP_X_HUB_SIGNATURE").split("=")[1]

    key = bytes(secret, 'utf-8')
    digester = hmac.new(key=key, msg=payload, digestmod=hashlib.sha1)
    signature = digester.hexdigest()

    if not hmac.compare_digest(str(signature), str(secret_hash)):
        current_app.logger.warning(f"HASH_NO_MATCH: {signature} != {secret_hash}")
        return False

    return True

@bp_root.route('/', methods=["POST"])
def labels_hook():
    current_app.logger.warning('labels_webhook triggered')
    headers = request.headers

    if not check_secret():
        abort(Response(response="Secrets do not match.", status=403))

    if headers.environ["HTTP_X_GITHUB_EVENT"] == "issues":
        # Handle issues endpoint
        current_app.logger.warning('Issues endpoint handler started.')
        # trigger_ghia_cli()
        return "GHIA_CLI started."
    elif headers.environ["HTTP_X_GITHUB_EVENT"] == "ping":
        # Handle ping endpoint
        current_app.logger.warning('Ping endpoint handler started.')
        return "I was pinged. I am triggered now."
    
    return "Supports only issues and ping Github endpoints."