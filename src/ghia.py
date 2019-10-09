import click
import validator
import requests
import os
from flask import Flask
from strategy import Strategies, GhiaContext
from ghia_cli_logic import ghia_run
from strategy import GhiaContext
import validator

# Pro testování webhook buď nasadit na pythonanywhere, nebo použít https://requestbin.com/
# GHIA_CONFIG = /Users/petr/Documents/Projects/Python/MI-PYT_GHIA/src/credentials.cfg:/Users/petr/Documents/Projects/Python/MI-PYT_GHIA/src/rules.cfg

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
	context.reposlug = f"mi-pyt-ghia/{context.username}-web"

	return context

def create_app(config=None):
	app = Flask(__name__)

	# TODO: Get files from GHIA_CONFIG env var
	config_auth = "/Users/petr/Documents/Projects/Python/MI-PYT_GHIA/src/credentials.cfg"
	config_rules = "/Users/petr/Documents/Projects/Python/MI-PYT_GHIA/src/rules.cfg"
	
	context = get_context(config_auth, config_rules)

	# app.config.from_pyfile(config or 'config.py')
	# app.config['the_answer'] = 42
	app.secret_key = os.environ.get('MY_SECRET', None)
	
	# TODO: Use blueprint to separate routes
	@app.route('/')
	def index():
		return 'MI-PYT je nejlepší předmět na FITu!'

	return app

############################  CLI ###################################
inputStrategies = [strategy.name.lower() for strategy in Strategies]
@click.command()
@click.option('-s', '--strategy', type=click.Choice(inputStrategies, case_sensitive=False), default=inputStrategies[0], help='How to handle assignment collisions.', show_default=True)
@click.option('-d', '--dry-run', is_flag=True, help='Run without making any changes.')
@click.option('-a', '--config-auth', callback=validator.validateAuth, type=click.File('r'), required=True, metavar='FILENAME', help='File with authorization configuration.')
@click.option('-r', '--config-rules', callback=validator.validateRules, type=click.File('r'), required=True, metavar='FILENAME', help='File with assignment rules configuration.')
@click.argument('REPOSLUG', callback=validator.validateReposlug, required=True)
def ghia(strategy, dry_run, config_auth, config_rules, reposlug):
	"""CLI tool for automatic issue assigning of GitHub issues"""
	ghia_run(strategy, dry_run, config_auth, config_rules, reposlug)
	
# Toto bude použito při zavolání z CLI
if __name__ == '__main__':
	ghia()	# pylint: disable=no-value-for-parameter