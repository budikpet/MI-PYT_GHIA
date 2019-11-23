import os
from typing import Tuple

def get_configs() -> Tuple[str, str]:
	"""
	Parses file paths to credentials and rules configuration files from GHIA_CONFIG environment variable.
	
	Returns:
		Tuple[str, str]: A tuple (path to credentials, path to rules)
	"""	
	env = os.getenv("GHIA_CONFIG").split(":")

	if "rules" in env[0]:
		return env[1], env[0]
	else:
		return env[0], env[1]