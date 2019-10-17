import click
import requests
import re
import sys
import json
from my_data_classes import GroupedUsers, UserStatus
from strategy import Strategies, GhiaContext, GhiaStrategy
from enum import Enum
from config_data import ConfigData

def has_fallback_label(issue, context):
	existing_labels = [label for label in issue["labels"] if label["name"] == context.get_fallback_label()]
	return len(existing_labels) > 0

def get_output_data(context: GhiaContext, issue, grouped_users: GroupedUsers):
	data = None

	if grouped_users.update_needed():
		data = {
			"assignees": grouped_users.get_users_to_assign()
		}
	elif not grouped_users.users_found_by_rules and context.get_fallback_label() is not None and not has_fallback_label(issue, context):
		labels = [context.get_fallback_label()]
		labels.extend([label["name"] for label in issue["labels"]])
		data = {
			"labels": labels
		}

	if data is not None:
		data = json.dumps(data)

	return data

def update_issue(context: GhiaContext, issue, grouped_users: GroupedUsers):
	# Update issue
	status_code = 200

	if not context.dry_run:
		data = get_output_data(context, issue, grouped_users)

		if data is not None:
			r = context.session.patch(f'{context.base}/repos/{context.get_reposlug()}/issues/{issue["number"]}', data=data)
			status_code = r.status_code

	return status_code

def write_user(user_status: UserStatus, user: str):
	symbol = lambda curr_symbol, color: click.style(curr_symbol, bold=True, fg=color)
	color = ""

	if user_status == UserStatus.ADD:
		color = "green"
	elif user_status == UserStatus.LEAVE:
		color = "blue"
	else:
		color = "red"

	click.echo(f'   {symbol(user_status.value, color)} {user}')

def write_label(issue, context: GhiaContext):
	msg = ""
	if not has_fallback_label(issue, context):
		msg = "added label"
	else:
		msg = "already has label"
	click.echo(f'   {click.style("FALLBACK", fg="yellow")}: {msg} \"{context.get_fallback_label()}\"')

def write_output(context: GhiaContext, issue, grouped_users: GroupedUsers, status_code: int):
	info = f'{context.reposlug}#{issue["number"]}'
	click.echo(f'-> {click.style(info, bold=True)} ({issue["html_url"]})')

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
# Returns: [(user_status, user), ...]
def group_users(context: GhiaContext, issue):
	already_assigned_users = set(map(lambda assignee: assignee["login"], issue["assignees"]))
	users_automatched = set()

	# Find users that should be assigned
	for (location, pairs) in context.get_user_patterns().items():
		for (pattern, username) in pairs:
			if patternMatches(issue, location, pattern):
				# Current user should be added to the issue
				users_automatched.add(username)

	# Prepare output
	return context.strategy.get_grouped_users(users_automatched, already_assigned_users)

def ghia_run(context: GhiaContext, issue_number: int = None):
	"""Run GHIA algorighm to automatically assign GitHub issues"""

	# Load issues
	context.session = requests.Session()
	context.session.headers = {
		'User-Agent': 'Python',
		'Authorization': f'token {context.get_token()}',
		# 'Content-Type': 'application/json', 
		# 'Accept': 'application/json'
		}
	context.session.params = {
		'per_page': 50
	}

	xstr = lambda s: '' if s is None else str(s)
	r = context.session.get(f'{context.base}/repos/{context.get_reposlug()}/issues/{xstr(issue_number)}')

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