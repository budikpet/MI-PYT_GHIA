import click
import requests
import re
import sys
import json
from enum import Enum
from ghia.github.config_data import ConfigData
from ghia.github.my_data_classes import GroupedUsers, UserStatus, Issue
from ghia.cli.strategy import GhiaContext

def get_output_data(context: GhiaContext, issue: Issue, grouped_users: GroupedUsers) -> str:
	"""
	Checks all things that need to be updated and creates data for the outgoing PATCH request.
	
	Args:
		context (GhiaContext): Context to use.
		issue (Issue): Currently selected issue.
		grouped_users (GroupedUsers): Result of pattern matching.
	
	Returns:
		str: JSON data string that is going to be used in a request to GitHub API.
	"""	

	data = dict()

	if grouped_users.update_needed():
		data["assignees"] = grouped_users.get_users_to_assign()
	
	if not grouped_users.users_found_by_rules and context.get_fallback_label() is not None and context.get_fallback_label() not in issue.labels:
		labels = [context.get_fallback_label()]
		labels.extend(issue.labels)
		data["labels"] = labels

	if data:
		# Data is not empty
		data = json.dumps(data)
	else:
		data = None

	return data

def update_issue(context: GhiaContext, issue: Issue, grouped_users: GroupedUsers) -> int:
	"""
	Update the selected issue online.
	
	Args:
		context (GhiaContext): Context to use.
		issue (Issue): Currently selected issue.
		grouped_users (GroupedUsers): Result of pattern matching.
	
	Returns:
		int: Returns status code of the operation.
	"""	

	status_code = 200

	if not context.dry_run:
		data = get_output_data(context, issue, grouped_users)

		if data is not None:
			r = context.session.patch(f'{context.base}/repos/{context.get_reposlug()}/issues/{issue.number}', data=data)
			status_code = r.status_code

	return status_code

def write_user(user_status: UserStatus, user: str):
	"""
	Write log message about state of the currently selected user.
	
	Args:
		user_status (UserStatus): Status of the found user.
		user (str): Username of the user.
	"""	

	symbol = lambda curr_symbol, color: click.style(curr_symbol, bold=True, fg=color)
	color = ""

	if user_status == UserStatus.ADD:
		color = "green"
	elif user_status == UserStatus.LEAVE:
		color = "blue"
	else:
		color = "red"

	click.echo(f'   {symbol(user_status.value, color)} {user}')

def write_label(issue: Issue, context: GhiaContext):
	"""
	Write log message about state of the Fallback label.
	
	Args:
		issue (Issue): Currently selected issue.
		context (GhiaContext): Context to use.
	"""	

	msg = ""
	if context.get_fallback_label() not in issue.labels:
		msg = "added label"
	else:
		msg = "already has label"
	click.echo(f'   {click.style("FALLBACK", fg="yellow")}: {msg} \"{context.get_fallback_label()}\"')

def write_output(context: GhiaContext, issue: Issue, grouped_users: GroupedUsers, status_code: int):
	"""
	Writes out all changes that the ghia algorithm did (or should have done) in the Github repository.
	
	Args:
		context (GhiaContext): Context to use.
		issue (Issue): Currently selected issue.
		grouped_users (GroupedUsers): Result of pattern matching.
		status_code (int): If 200 then changes were successful. Otherwise error is shown.
	"""	

	info = f'{context.reposlug}#{issue.number}'
	click.echo(f'-> {click.style(info, bold=True)} ({issue.html_url})')

	# Create output
	if status_code != 200 and not context.dry_run:
		# Error occured
		click.echo(f'   {click.style("ERROR", fg="red")}: Could not update issue {info}', err=True)
	else:
		if grouped_users.has_users() != 0:
			for (user_status, user) in grouped_users.get_output_list():
				write_user(user_status, user)
		elif context.get_fallback_label() is not None:
			write_label(issue, context)

	print

def pattern_matches(issue: Issue, location: str, pattern: str) -> bool:
	"""
	Matches patterns from the rules file to issue data in appropriate issue locations (issue body, issue labels etc).
	
	Args:
		issue (Issue): Currently selected issue.
		location (str): Where in the Issue object should we look for the match.
		pattern (str): Pattern to match against
	
	Returns:
		bool: True if match found.
	"""	

	result = False

	if location == "title" or location == "any":
		result = result or bool(re.search(pattern, issue.title, re.IGNORECASE))

	if location == "text" or location == "any":
		result = result or bool(re.search(pattern, issue.body, re.IGNORECASE))

	if location == "label" or location == "any":
		for label in issue.labels:
			if bool(re.search(pattern, label, re.IGNORECASE)):
				result = True
				break

	return result

def group_users(context: GhiaContext, issue: Issue) -> GroupedUsers:
	"""
	Checks current issue against all patterns.
	
	Args:
		context (GhiaContext): Used context
		issue (Issue): Currently selected issue.
	
	Returns:
		GroupedUsers: Result of rules matching for the currently selected issue.
	"""	

	already_assigned_users = set(issue.assignees)
	users_automatched = set()

	# Find users that should be assigned
	for (location, pairs) in context.get_user_patterns().items():
		for (pattern, username) in pairs:
			if pattern_matches(issue, location, pattern):
				# Current user should be added to the issue
				users_automatched.add(username)

	# Prepare output
	return context.strategy.get_grouped_users(users_automatched, already_assigned_users)

def ghia_run(context: GhiaContext, issue_number: int = None):
	"""
	Run GHIA algorighm to automatically assign GitHub issues.
	
	Args:
		context (GhiaContext): Context to be used.
		issue_number (int, optional): Modifies an issue with this number only if provided. If not provided then modifies all issues. Defaults to None.
	"""	

	# Load issues
	context.session.headers = {
		'User-Agent': 'Python',
		'Authorization': f'token {context.get_token()}',
		# 'Content-Type': 'application/json', 
		# 'Accept': 'application/json'
		}
	context.session.params = {
		'per_page': 50
	}

	xstr = lambda s: '' if s is None else f'/{str(s)}'
	r = context.session.get(f'{context.base}/repos/{context.get_reposlug()}/issues{xstr(issue_number)}')

	while True:
		issues = list()
		if issue_number is None:
			issues = r.json()
		else:
			issues.append(r.json())

		if r.status_code != 200:
			click.echo(f'{click.style("ERROR", fg="red")}: Could not list issues for repository {context.get_reposlug()}', err=True)
			context.session.close()
			sys.exit(10)
		elif len(issues) <= 0:
			# No more issues exist
			break

		# Check all received issues
		for issue in issues:
			# Check current issue against all patterns in all locations
			issue = Issue(issue)
			grouped_users = group_users(context, issue)
			status_code = update_issue(context, issue, grouped_users)
			write_output(context, issue, grouped_users, status_code)

		# Next page
		next_path = r.links.get("next")
		if next_path is not None:
			r = context.session.get(next_path["url"])
			print
		else:
			# No more pages exist
			break

	context.session.close()