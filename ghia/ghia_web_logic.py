import requests
import os
from flask import Flask
from typing import Tuple
from ghia.cli import validator
from ghia.cli.strategy import Strategies, GhiaContext
from ghia.ghia_cli_logic import ghia_run
from ghia.root_index import bp_root
from ghia.github import util

def get_username(context: GhiaContext) -> str:
	"""
	Get username of the current user using GITHUB_TOKEN.
	
	Args:
		context (GhiaContext): Context to use.
	
	Returns:
		str: Username.
	"""	
	
	session = requests.Session()
	session.headers = {
		'User-Agent': 'Python',
		'Authorization': f'token {context.get_token()}',
		}

	r = session.get(f'{context.base}/user')

	return r.json()["login"]

def get_context(config_auth: str, config_rules: str) -> GhiaContext:
	"""
	Constructs GhiaContext from the provided configuration file paths.
	
	Args:
		config_auth (str): Path to the credentials file.
		config_rules (str): Path to the rules file.
	
	Returns:
		GhiaContext: The newly created GhiaContext.
	"""	

	context: GhiaContext = None
	with open(config_auth) as authFile:
		with open(config_rules) as rulesFile:
			dataAuth = validator.validateAuth(None, None, authFile=authFile)
			dataRules = validator.validateRules(None, None, rulesFile=rulesFile)
			context = GhiaContext("https://api.github.com", Strategies.APPEND.name, False, dataAuth, dataRules)

	context.username = get_username(context)

	return context

def create_app(context: GhiaContext = None) -> Flask:
	"""
	Create the Flask app.
	
	Args:
		context (GhiaContext, optional): If no context is provided a new default one is automatically created. That requires GHIA_CONFIG environment variable. Defaults to None.
	
	Returns:
		Flask: Newly created Flask application.
	"""	
	app = Flask(__name__, template_folder="templates")

	if context is None:
		config_auth, config_rules = util.get_configs()
		context: GhiaContext = get_context(config_auth, config_rules)
	# else:
	# 	context.username = get_username(context)

	app.config["GHIA_CONTEXT"] = context
	app.secret_key = context.get_secret()
	app.register_blueprint(bp_root, url_prefix="/")

	# app.config.from_pyfile(config or 'config.py')

	return app