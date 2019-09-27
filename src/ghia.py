import click
import requests

@click.command()
@click.argument('source', nargs=-1, required=True)
@click.argument('target', required=True)
def cp(source, target):
	for s in source:
		click.echo(f'Copying {s} to {target}')


@click.command()
@click.option('--count', required=True, type=int, help='Number of greetings.')
@click.option('--name', '-n', prompt='Enter name: ', help='Name to greet', metavar='NAME')
@click.option('-c/-C', '--color/--no-color')
@click.option('-v', '--verbose', is_flag=True)
def hello(count, name, color, verbose):
	greeting = (f'Hello, {name}')
	if color:
		greeting = click.style(greeting, fg='green', bg='black')
	for x in range(count):
		click.echo(greeting)

@click.command()
@click.option('-s', '--strategy', type=click.Choice(['append', 'set', 'change'], case_sensitive=False), default='append', help='How to handle assignment collisions.', show_default=True)
@click.option('-d', '--dry-run', is_flag=True, help='Run without making any changes.')
@click.option('-a', '--config-auth', type=click.File('r'), required=True, metavar='FILENAME', help='File with authorization configuration.')
@click.option('-r', '--config-rules', type=click.File('r'), required=True, metavar='FILENAME', help='File with assignment rules configuration.')
@click.argument('REPOSLUG', required=True)
def ghia(strategy, dry_run, config_auth, config_rules, reposlug):
	"""CLI tool for automatic issue assigning of GitHub issues"""
	print(f'{strategy}, {dry_run}, {reposlug}')
	
# Toto bude použito při zavolání z CLI
if __name__ == '__main__':
	ghia()
