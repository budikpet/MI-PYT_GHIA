from configparser import ConfigParser
import click

def validateAuth(ctx, param, authFile):
	dataAuth = ConfigParser()
	dataAuth.read_file(authFile)
	
	if "github" in dataAuth.keys():
		if "token" in dataAuth["github"].keys():
			return dataAuth
		
	raise click.BadParameter('incorrect configuration format')

def validateRules(ctx, param, rulesFile):
	dataRules = ConfigParser()
	dataRules.optionxform = str
	dataRules.read_file(rulesFile)
	
	if "patterns" in dataRules.keys():
		return dataRules
		
	raise click.BadParameter('incorrect configuration format')

def validateReposlug(ctx, param, reposlug):
	split = reposlug.split("/")

	if len(split) == 2:
		return reposlug
	else:
		raise click.BadParameter('Error: Invalid value for "REPOSLUG": not in owner/repository format')