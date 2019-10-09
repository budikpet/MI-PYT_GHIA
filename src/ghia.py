import click
import validator
import os
from flask import Flask
from strategy import Strategies
from ghia_cli_logic import ghia_run
from strategy import GhiaContext

# Pro testování webhook buď nasadit na pythonanywhere, nebo použít https://requestbin.com/
# Získání username: https://developer.github.com/v3/users/#get-the-authenticated-user

def create_app(config=None):
	app = Flask(__name__)

	app.config.from_pyfile(config or 'config.py')
	app.config['the_answer'] = 42
	app.secret_key = os.environ.get('MY_SECRET', None)

	return app
	
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