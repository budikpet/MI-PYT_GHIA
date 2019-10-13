from flask import Blueprint, render_template, current_app
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