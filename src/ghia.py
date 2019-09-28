import click
import requests
import re
from configData import ConfigData

def writeOutput(issue, configData, addedUsers, removedUsers, leftUsers):
	print(f"#{issue['number']}: {addedUsers}, {removedUsers}, {leftUsers}")

# Matches patterns to data in appropriate locations
def patternMatches(issue, location, pattern):
	if location == "title" or location == "any":
		return bool(re.search(pattern, issue["title"], re.IGNORECASE))
	
	if location == "text" or location == "any":
		return bool(re.search(pattern, issue["body"], re.IGNORECASE))
	
	if location == "label" or location == "any":
		for label in issue["labels"]:
			if bool(re.search(pattern, label["name"], re.IGNORECASE)):
				return True
		
		return False


# Checks current issue against all patterns
# Returns triplet of sets: ({addedUsers}, {removedUsers}, {leftUsers})
def check(issue, strategy, configData):
	alreadyAssignedUsers = set(map(lambda assignee: assignee["login"], issue["assignees"]))
	usersToAssign = set()
	
	# Find users that should be assigned
	for (location, pairs) in configData.userPatterns.items():
		for (pattern, username) in pairs:
			if patternMatches(issue, location, pattern):
				# Current user should be added to the issue
				usersToAssign.add(username)

	if strategy == "append":
		return (usersToAssign, set(), alreadyAssignedUsers)
	elif strategy == "set":
		return (usersToAssign, set(), alreadyAssignedUsers)
	elif strategy == "change":
		return (
			usersToAssign.difference(alreadyAssignedUsers), 
			alreadyAssignedUsers.difference(usersToAssign), 
			alreadyAssignedUsers.intersection(usersToAssign)
			)
				

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

	if strategy == 'set':
		session.params['assignee'] = 'none'

	while True:
		r = session.get(f'https://api.github.com/repos/{reposlug}/issues')
		issues = r.json()

		if len(issues) <= 0:
			# No more issues exist
			break
		
		# Check all received issues
		for issue in issues:
			# Check current issue against all patterns in all locations
			addedUsers, removedUsers, leftUsers = check(issue, strategy, configData)
			# Append 13, 17, 46
			writeOutput(issue, configData, addedUsers, removedUsers, leftUsers)
					
		# Next page
		session.params['page'] += 1

	session.close()
	# testConfig = f'{len(issues)}'
	# testConfig = click.style(testConfig, fg='red', bg='black')
	# click.echo(testConfig)
	
# Toto bude použito při zavolání z CLI
if __name__ == '__main__':
	ghia()	# pylint: disable=no-value-for-parameter