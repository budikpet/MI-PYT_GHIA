from flask import Blueprint, render_template, current_app
from jinja2 import Markup
from strategy import Strategies, GhiaContext

bp_root = Blueprint('bp_root', __name__, template_folder='templates')

def get_ghia_context() -> GhiaContext:
    return current_app.config["GHIA_CONTEXT"]

@bp_root.app_template_filter('github_url')
def show_rules(rules):
    print

@bp_root.app_template_filter('github_url')
def convert_time(username: str):
    result = f'<a href="https://github.com/{username}">{username}</a>'

    return Markup(result)

@bp_root.route('/')
def index():
    context = get_ghia_context()

    return render_template("index.html", context=get_ghia_context())