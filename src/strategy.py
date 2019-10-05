from enum import Enum
from configData import ConfigData
import requests
import click
from typing import Set

class GhiaContext():
    def __init__(self, base, strategy, dry_run, config_auth, config_rules, reposlug):
        self.base = base
        self.strategy: GhiaStrategy = strategy
        self.dry_run = dry_run
        self.reposlug = reposlug
        self.session = None

        # Get configuration
        self.configData = ConfigData(config_auth, config_rules)

    def getUserPatterns(self):
        return self.configData.userPatterns

    def getToken(self):
        return self.configData.token

    def getFallbackLabel(self):
        return self.configData.fallbackLabel

class GhiaStrategy():
    def getSeparatedUsers(self, usersToAssign: Set[str], usersAlreadyAssigned: Set[str]):
        pass

class AppendStrategy():
    def getSeparatedUsers(self, usersToAssign: Set[str], usersAlreadyAssigned: Set[str]):
        pass

class SetStrategy():
    def getSeparatedUsers(self, usersToAssign: Set[str], usersAlreadyAssigned: Set[str]):
        pass

class ChangeStrategy():
    def getSeparatedUsers(self, usersToAssign: Set[str], usersAlreadyAssigned: Set[str]):
        pass


class Strategies(Enum):
	APPEND = AppendStrategy()
	SET = SetStrategy()
	CHANGE = ChangeStrategy()