import click
import requests
import re
import sys
import json
import validator
from strategy import Strategies, GhiaContext
from enum import Enum
from configData import ConfigData

class UserStatus(Enum):
	ADD = "+"
	REMOVE = "-"
	LEAVE = "="	

def hasFallbackLabel(issue, context):
	existingLabels = [label for label in issue["labels"] if label["name"] == context.getFallbackLabel()]
	return len(existingLabels) > 0

def writeOutput(context: GhiaContext, issue, users):
	symbol = lambda currSymbol, color: click.style(currSymbol, bold=True, fg=color)
	info = f'{context.reposlug}#{issue["number"]}'
	click.echo(f'-> {click.style(info, bold=True)} ({issue["html_url"]})')

	# Update issue
	statusCode = 200
	changes = False

	assignees = list()
	for user in users:
		assignees.append(user[1])
		if user[0] != UserStatus.LEAVE:
			changes = True

	if not context.dry_run:
		if changes:
			data = {
				"assignees": list({user[1] for user in users if user[0] != UserStatus.REMOVE})
			}
			data = json.dumps(data)
			r = context.session.patch(f'{context.base}/repos/{context.reposlug}/issues/{issue["number"]}', data=data)
			statusCode = r.status_code	
		elif context.getFallbackLabel() != "" and not hasFallbackLabel(issue, context):
			labels = [context.getFallbackLabel()]
			labels.extend([label["name"] for label in issue["labels"]])
			data = {
				"labels": labels
			}
			data = json.dumps(data)
			r = context.session.patch(f'{context.base}/repos/{context.reposlug}/issues/{issue["number"]}', data=data)
			statusCode = r.status_code
	
	# Create output
	if statusCode != 200 and not context.dry_run:
		# Error occured
		click.echo(f'   {click.style("ERROR", fg="red")}: Could not update issue {info}', err=True)
	else:
		if len(users) != 0:
			for (userStatus, user) in users:
				click.echo(f'   {symbol(userStatus.value, "green")} {user}')
		elif context.getFallbackLabel() != "":
			msg = ""
			if not hasFallbackLabel(issue, context):
				msg = "added label"
			else:
				msg = "already has label"
			click.echo(f'   {click.style("FALLBACK", fg="yellow")}: {msg} \"{context.getFallbackLabel()}\"')
	
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
def separateUsers(context: GhiaContext, issue):
	alreadyAssignedUsers = set(map(lambda assignee: assignee["login"], issue["assignees"]))
	usersToAssign = set()
	
	# Find users that should be assigned
	for (location, pairs) in context.getUserPatterns().items():
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

inputStrategies = [strategy.name.lower() for strategy in Strategies]

@click.command()
@click.option('-s', '--strategy', type=click.Choice(inputStrategies, case_sensitive=False), default=inputStrategies[0], help='How to handle assignment collisions.', show_default=True)
@click.option('-d', '--dry-run', is_flag=True, help='Run without making any changes.')
@click.option('-a', '--config-auth', callback=validator.validateAuth, type=click.File('r'), required=True, metavar='FILENAME', help='File with authorization configuration.')
@click.option('-r', '--config-rules', callback=validator.validateRules, type=click.File('r'), required=True, metavar='FILENAME', help='File with assignment rules configuration.')
@click.argument('REPOSLUG', callback=validator.validateReposlug, required=True)
def ghia(strategy, dry_run, config_auth, config_rules, reposlug):
	"""CLI tool for automatic issue assigning of GitHub issues"""

	context = GhiaContext("https://api.github.com", strategy, dry_run, config_auth, config_rules, reposlug)

	# Load issues
	context.session = requests.Session()
	context.session.headers = {
		'User-Agent': 'Python',
		'Authorization': f'token {context.getToken()}',
		# 'Content-Type': 'application/json', 
		# 'Accept': 'application/json'
		}
	context.session.params = {
		'per_page': 50,
		'page': 1
	}

	while True:
		r = context.session.get(f'{context.base}/repos/{reposlug}/issues')
		issues = r.json()

		if r.status_code != 200:
			click.echo(f'{click.style("ERROR", fg="red")}: Could not list issues for repository {reposlug}', err=True)
			context.session.close()
			sys.exit(10)
		elif len(issues) <= 0:
			# No more issues exist
			break
		
		# Check all received issues
		for issue in issues:
			# Check current issue against all patterns in all locations
			users = separateUsers(context, issue)
			writeOutput(context, issue, users)
					
		# Next page
		context.session.params['page'] += 1

	context.session.close()
	
# Toto bude použito při zavolání z CLI
if __name__ == '__main__':
	ghia()	# pylint: disable=no-value-for-parameter