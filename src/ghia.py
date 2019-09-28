import click
import requests
import configparser

@click.command()
@click.option('-s', '--strategy', type=click.Choice(['append', 'set', 'change'], case_sensitive=False), default='append', help='How to handle assignment collisions.', show_default=True)
@click.option('-d', '--dry-run', is_flag=True, help='Run without making any changes.')
@click.option('-a', '--config-auth', type=click.File('r'), required=True, metavar='FILENAME', help='File with authorization configuration.')
@click.option('-r', '--config-rules', type=click.File('r'), required=True, metavar='FILENAME', help='File with assignment rules configuration.')
@click.argument('REPOSLUG', required=True)
def ghia(strategy, dry_run, config_auth, config_rules, reposlug):
	"""CLI tool for automatic issue assigning of GitHub issues"""
	
	"Get configuration"
	authConfig = configparser.ConfigParser()
	authConfig.read_file(config_auth)
	
	ruleConfig = configparser.ConfigParser()
	ruleConfig.read_file(config_rules)

	testConfig = f'{authConfig["github"]["token"]}, {ruleConfig}'
	testConfig = click.style(testConfig, fg='green', bg='black')
	click.echo(testConfig)
	print(f'{strategy}, {dry_run}, {reposlug}')
	
# Toto bude použito při zavolání z CLI
if __name__ == '__main__':
	ghia()	# pylint: disable=no-value-for-parameter