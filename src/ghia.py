import click
import requests
import re
from configData import ConfigData

@click.command()
@click.option('-s', '--strategy', type=click.Choice(['append', 'set', 'change'], case_sensitive=False), default='append', help='How to handle assignment collisions.', show_default=True)
@click.option('-d', '--dry-run', is_flag=True, help='Run without making any changes.')
@click.option('-a', '--config-auth', type=click.File('r'), required=True, metavar='FILENAME', help='File with authorization configuration.')
@click.option('-r', '--config-rules', type=click.File('r'), required=True, metavar='FILENAME', help='File with assignment rules configuration.')
@click.argument('REPOSLUG', required=True)
def ghia(strategy, dry_run, config_auth, config_rules, reposlug):
	"""CLI tool for automatic issue assigning of GitHub issues"""
	
	# Get configuration
	configData = ConfigData(config_auth, config_rules)

	# Load issues
	session = requests.Session()
	session.headers = {
		'User-Agent': 'Python',
		'Authorization': f'token {configData.token}'
		}
	session.params = {
		'per_page': 50,
		'page': 1
	}

	while True:
		r = session.get(f'https://api.github.com/repos/{reposlug}/issues')
		issues = r.json()

		if len(issues) <= 0:
			# No more issues exist
			break
		
		# Check all received issues
		for issue in issues:
			print(issue)

		# Next page
		session.params['page'] += 1

	session.close()
	# testConfig = f'{len(issues)}'
	# testConfig = click.style(testConfig, fg='red', bg='black')
	# click.echo(testConfig)
	
# Toto bude použito při zavolání z CLI
if __name__ == '__main__':
	ghia()	# pylint: disable=no-value-for-parameter