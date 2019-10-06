import click
import requests
import re
import sys
import json
import validator
from myDataClasses import GroupedUsers, UserStatus
from strategy import Strategies, GhiaContext, GhiaStrategy
from enum import Enum
from configData import ConfigData

def hasFallbackLabel(issue, context):
	existingLabels = [label for label in issue["labels"] if label["name"] == context.getFallbackLabel()]
	return len(existingLabels) > 0

def getOutputData(context: GhiaContext, issue, groupedUsers: GroupedUsers):
	data = None
	
	if groupedUsers.updateNeeded():
		data = {
			"assignees": groupedUsers.getUsersToAssign()
		}
	elif context.getFallbackLabel() != "" and not hasFallbackLabel(issue, context):
		labels = [context.getFallbackLabel()]
		labels.extend([label["name"] for label in issue["labels"]])
		data = {
			"labels": labels
		}

	if data is not None:
		data = json.dumps(data)

	return data

def updateIssue(context: GhiaContext, issue, groupedUsers: GroupedUsers):
	# Update issue
	statusCode = 200

	if not context.dry_run:
		data = getOutputData(context, issue, groupedUsers)
		
		if data is not None:
			r = context.session.patch(f'{context.base}/repos/{context.reposlug}/issues/{issue["number"]}', data=data)
			statusCode = r.status_code

	return statusCode

def writeUser(userStatus: UserStatus, user: str):
	symbol = lambda currSymbol, color: click.style(currSymbol, bold=True, fg=color)
	color = ""

	if userStatus == UserStatus.ADD:
		color = "green"
	elif userStatus == UserStatus.LEAVE:
		color = "blue"
	else:
		color = "red"

	click.echo(f'   {symbol(userStatus.value, color)} {user}')

def writeLabel(issue, context: GhiaContext):
	msg = ""
	if not hasFallbackLabel(issue, context):
		msg = "added label"
	else:
		msg = "already has label"
	click.echo(f'   {click.style("FALLBACK", fg="yellow")}: {msg} \"{context.getFallbackLabel()}\"')

def writeOutput(context: GhiaContext, issue, groupedUsers: GroupedUsers, statusCode):
	info = f'{context.reposlug}#{issue["number"]}'
	click.echo(f'-> {click.style(info, bold=True)} ({issue["html_url"]})')
	
	# Create output
	if statusCode != 200 and not context.dry_run:
		# Error occured
		click.echo(f'   {click.style("ERROR", fg="red")}: Could not update issue {info}', err=True)
	else:
		if groupedUsers.hasUsers() != 0:
			for (userStatus, user) in groupedUsers.getOutputList():
				writeUser(userStatus, user)
		elif context.getFallbackLabel() != "":
			writeLabel(issue, context)
	
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
def groupUsers(context: GhiaContext, issue):
	alreadyAssignedUsers = set(map(lambda assignee: assignee["login"], issue["assignees"]))
	usersAutoMatched = set()
	
	# Find users that should be assigned
	for (location, pairs) in context.getUserPatterns().items():
		for (pattern, username) in pairs:
			if patternMatches(issue, location, pattern):
				# Current user should be added to the issue
				usersAutoMatched.add(username)

	# Prepare output
	return context.strategy.getGroupedUsers(usersAutoMatched, alreadyAssignedUsers)
	
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
			groupedUsers = groupUsers(context, issue)
			statusCode = updateIssue(context, issue, groupedUsers)
			writeOutput(context, issue, groupedUsers, statusCode)
					
		# Next page
		context.session.params['page'] += 1

	context.session.close()
	
# Toto bude použito při zavolání z CLI
if __name__ == '__main__':
	ghia()	# pylint: disable=no-value-for-parameter