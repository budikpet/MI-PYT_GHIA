import requests
import os
from flask import Flask
from typing import Tuple
from ghia.cli import validator
from ghia.cli.strategy import Strategies, GhiaContext
from ghia.cli.ghia_cli_logic import ghia_run
from .root.root_index import bp_root

def get_username(context: GhiaContext):
	session = requests.Session()
	session.headers = {
		'User-Agent': 'Python',
		'Authorization': f'token {context.get_token()}',
		}

	r = session.get(f'{context.base}/user')

	return r.json()["login"]

def get_context(config_auth, config_rules) -> GhiaContext:
	context: GhiaContext = None
	with open(config_auth) as authFile:
		with open(config_rules) as rulesFile:
			dataAuth = validator.validateAuth(None, None, authFile=authFile)
			dataRules = validator.validateRules(None, None, rulesFile=rulesFile)
			context = GhiaContext("https://api.github.com", Strategies.APPEND.name, False, dataAuth, dataRules)

	context.username = get_username(context)

	return context

def get_configs() -> Tuple[str, str]:
	env = os.getenv("GHIA_CONFIG").split(":")

	if "rules" in env[0]:
		return env[1], env[0]
	else:
		return env[0], env[1]

def create_app(config=None):
	app = Flask(__name__)

	config_auth, config_rules = get_configs()
	context = get_context(config_auth, config_rules)

	app.config["GHIA_CONTEXT"] = context
	app.secret_key = context.get_secret()
	app.register_blueprint(bp_root, url_prefix="/")

	# app.config.from_pyfile(config or 'config.py')

	return app