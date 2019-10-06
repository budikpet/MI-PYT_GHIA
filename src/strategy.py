from enum import Enum
from configData import ConfigData
from myDataClasses import GroupedUsers, UserStatus
import requests
import click
from typing import Set, List

class GhiaContext():
    def __init__(self, base, strategy: str, dry_run, config_auth, config_rules, reposlug):
        self.base: str = base
        self.strategy: GhiaStrategy = Strategies[strategy.upper()].value
        self.dry_run: bool = dry_run
        self.reposlug: str = reposlug
        self.session: requests.session = None

        # Get configuration
        self.configData: ConfigData = ConfigData(config_auth, config_rules)

    def getUserPatterns(self):
        return self.configData.userPatterns

    def getToken(self):
        return self.configData.token

    def getFallbackLabel(self):
        return self.configData.fallbackLabel

class GhiaStrategy():
    def getGroupedUsers(self, usersAutoMatched: Set[str], usersAlreadyAssigned: Set[str]) -> GroupedUsers:
        pass

class AppendStrategy(GhiaStrategy):
    def getGroupedUsers(self, usersAutoMatched: Set[str], usersAlreadyAssigned: Set[str]) -> GroupedUsers:
        return GroupedUsers(usersAutoMatched=usersAutoMatched.difference(usersAlreadyAssigned), 
            usersToLeave=usersAlreadyAssigned,
            usersToRemove=set())

class SetStrategy(GhiaStrategy):
    def getGroupedUsers(self, usersAutoMatched: Set[str], usersAlreadyAssigned: Set[str]) -> GroupedUsers:
        return GroupedUsers(usersAutoMatched=usersAutoMatched, 
            usersToLeave=usersAlreadyAssigned,
            usersToRemove=set())

class ChangeStrategy(GhiaStrategy):
    def getGroupedUsers(self, usersAutoMatched: Set[str], usersAlreadyAssigned: Set[str]) -> GroupedUsers:
        return GroupedUsers(usersAutoMatched=usersAutoMatched.difference(usersAlreadyAssigned), 
            usersToLeave=usersAlreadyAssigned.intersection(usersAutoMatched),
            usersToRemove=usersAlreadyAssigned.difference(usersAutoMatched))

class Strategies(Enum):
	APPEND = AppendStrategy()
	SET = SetStrategy()
	CHANGE = ChangeStrategy()