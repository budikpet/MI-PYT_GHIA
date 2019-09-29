import click
import requests
import re
import sys
import json
from enum import Enum
from configData import ConfigData

class UserStatus(Enum):
	ADD = "+"
	REMOVE = "-"
	LEAVE = "="	

def writeOutput(session, issue, configData, dry_run, reposlug, users):
	symbol = lambda currSymbol, color: click.style(currSymbol, bold=True, fg=color)
	info = f'{reposlug}#{issue["number"]}'
	click.echo(f'-> {click.style(info, bold=True)} ({issue["html_url"]})')

	# Update issue
	statusCode = 403
	if not dry_run:
		assignees = list()
		changes = False
		for user in users:
			assignees.append(user[1])
			if user[0] != UserStatus.LEAVE:
				changes = True
		
		# if len(data["assignees"] != 0) or len(users) != 0:
			# Current issue has assignees that have to be added or deleted
		if changes:
			data = {
				"assignees": list({user[1] for user in users if user[0] != UserStatus.REMOVE})
			}
			data = json.dumps(data)
			r = session.patch(f'https://api.github.com/repos/{reposlug}/issues/{issue["number"]}', data=data)
			statusCode = r.status_code	
		else:
			statusCode = 200
	
	# Create output
	if statusCode != 200 and not dry_run:
		# Error occured
		click.echo(f'   {click.style("ERROR", fg="red")}: Could not update issue {info}', err=True)
	else:
		for (userStatus, user) in users:
			click.echo(f'   {symbol(userStatus.value, "green")} {user}')
	
	print

# Matches patterns to data in appropriate locations
def patternMatches(issue, location, pattern):
	result = False
	
	if location == "title" or location == "any":
		result = result or bool(re.search(pattern, issue["title"], re.IGNORECASE))
	
	if location == "text" or location == "any":
		result = result or bool(re.search(pattern, issue["body"], re.IGNORECASE))
	
	if location == "label" or location == "any":
		for label in issue["labels"]:
			if bool(re.search(pattern, label["name"], re.IGNORECASE)):
				result = True
				break
	
	return result


# Checks current issue against all patterns
# Returns: [(userStatus, user), ...]
def check(issue, strategy, configData):
	alreadyAssignedUsers = set(map(lambda assignee: assignee["login"], issue["assignees"]))
	usersToAssign = set()
	
	# Find users that should be assigned
	for (location, pairs) in configData.userPatterns.items():
		for (pattern, username) in pairs:
			if patternMatches(issue, location, pattern):
				# Current user should be added to the issue
				usersToAssign.add(username)

	# Prepare output
	output = list()
	fun = lambda userStatus, currSet: [(userStatus, username) for username in currSet]
	if strategy == "append":
		output = fun(UserStatus.ADD, usersToAssign.difference(alreadyAssignedUsers))
		output.extend(fun(UserStatus.LEAVE, alreadyAssignedUsers))
	elif strategy == "set":
		output = fun(UserStatus.ADD, usersToAssign)
		output.extend(fun(UserStatus.LEAVE, alreadyAssignedUsers))
	elif strategy == "change":
		output = fun(UserStatus.ADD, usersToAssign.difference(alreadyAssignedUsers))
		output.extend(fun(UserStatus.REMOVE, alreadyAssignedUsers.difference(usersToAssign)))
		output.extend(fun(UserStatus.LEAVE, alreadyAssignedUsers.intersection(usersToAssign)))
	
	output.sort(key=lambda pair: pair[1].lower())
	return output

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
		'Authorization': f'token {configData.token}',
		# 'Content-Type': 'application/json', 
		# 'Accept': 'application/json'
		}
	session.params = {
		'per_page': 50,
		'page': 1
	}

	while True:
		r = session.get(f'https://api.github.com/repos/{reposlug}/issues')
		issues = r.json()

		if r.status_code != 200:
			click.echo(f'{click.style("ERROR", fg="red")}: Could not list issues for repository {reposlug}', err=True)
			session.close()
			sys.exit(10)
		elif len(issues) <= 0:
			# No more issues exist
			break
		
		# Check all received issues
		for issue in issues:
			# Check current issue against all patterns in all locations
			users = check(issue, strategy, configData)
			writeOutput(session, issue, configData, dry_run, reposlug, users)
					
		# Next page
		session.params['page'] += 1

	session.close()
	
# Toto bude použito při zavolání z CLI
if __name__ == '__main__':
	ghia()	# pylint: disable=no-value-for-parameter