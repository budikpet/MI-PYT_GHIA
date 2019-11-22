from configparser import ConfigParser
import click

def validateAuth(ctx, param, authFile) -> ConfigParser:
	"""
	Click validator for credentials file.
	
	Args:
		ctx ([type]): [description]
		param ([type]): [description]
		authFile ([type]): Opened credentials file.
	
	Raises:
		click.BadParameter: Credential file did not have appropriate data.
	
	Returns:
		ConfigParser: Parsed credentials file.
	"""	

	dataAuth = ConfigParser()
	dataAuth.read_file(authFile)
	
	if "github" in dataAuth.keys():
		if "token" in dataAuth["github"].keys():
			return dataAuth
		
	raise click.BadParameter('incorrect configuration format')

def validateRules(ctx, param, rulesFile) -> ConfigParser:
	"""
	Click validator for rules file.
	
	Args:
		ctx ([type]): [description]
		param ([type]): [description]
		authFile ([type]): Opened rules file.
	
	Raises:
		click.BadParameter: Rules file did not have appropriate data.
	
	Returns:
		ConfigParser: Parsed rules file.
	"""	

	dataRules = ConfigParser()
	dataRules.optionxform = str
	dataRules.read_file(rulesFile)
	
	if "patterns" in dataRules.keys():
		return dataRules
		
	raise click.BadParameter('incorrect configuration format')

def validateReposlug(ctx, param, reposlug: str) -> str:
	"""
	Click validator for the reposlug.
	
	Args:
		ctx ([type]): [description]
		param ([type]): [description]
		reposlug (str): Reposlug in owner/repository format
	
	Raises:
		click.BadParameter: Reposlug has wrong format.
	
	Returns:
		str: Reposlug
	"""	

	split = reposlug.split("/")

	if len(split) == 2:
		return reposlug
	else:
		raise click.BadParameter('Error: Invalid value for "REPOSLUG": not in owner/repository format')