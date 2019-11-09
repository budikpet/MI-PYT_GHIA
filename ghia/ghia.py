import click
from flask import Flask
import requests
from typing import Tuple
from ghia.cli import validator
from ghia.cli.strategy import Strategies, GhiaContext
from ghia.ghia_cli_logic import ghia_run
from ghia import ghia_web_logic

def create_app(config=None):
	return ghia_web_logic.create_app(config=config)

inputStrategies = [strategy.name.lower() for strategy in Strategies]

@click.command()
@click.option('-s', '--strategy', type=click.Choice(inputStrategies, case_sensitive=False), default=inputStrategies[0], help='How to handle assignment collisions.', show_default=True)
@click.option('-d', '--dry-run', is_flag=True, help='Run without making any changes.')
@click.option('-a', '--config-auth', callback=validator.validateAuth, type=click.File('r'), required=True, metavar='FILENAME', help='File with authorization configuration.')
@click.option('-r', '--config-rules', callback=validator.validateRules, type=click.File('r'), required=True, metavar='FILENAME', help='File with assignment rules configuration.')
@click.argument('REPOSLUG', callback=validator.validateReposlug, required=True)
def ghia(strategy, dry_run, config_auth, config_rules, reposlug):
	"""CLI tool for automatic issue assigning of GitHub issues"""
	context = GhiaContext("https://api.github.com", strategy, dry_run, config_auth, config_rules, reposlug, session=requests.Session())
	
	ghia_run(context)
	
# This function will be used as a default call
def main():
	# This way the programme is always called "ghia" in help
	ghia(prog_name="ghia")	# pylint: disable=no-value-for-parameter,unexpected-keyword-arg