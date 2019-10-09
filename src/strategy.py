from enum import Enum
from config_data import ConfigData
from my_data_classes import GroupedUsers, UserStatus
import requests
import click
from typing import Set, List

class GhiaContext():
    def __init__(self, base: str, strategy: str, dry_run: bool, config_auth, config_rules, reposlug: str = None):
        self.base: str = base
        self.strategy: GhiaStrategy = Strategies[strategy.upper()].value
        self.dry_run: bool = dry_run
        self.reposlug: str = reposlug
        self.session: requests.session = None
        self.username: str = None

        # Get configuration
        self.config_data: ConfigData = ConfigData(config_auth, config_rules)

    def get_user_patterns(self):
        return self.config_data.user_patterns

    def get_token(self):
        return self.config_data.token

    def get_secret(self):
        return self.config_data.secret

    def get_fallback_label(self):
        return self.config_data.fallback_label

    def get_reposlug(self):
        if self.reposlug is not None:
            return self.reposlug
        else:
            msg = "Reposlug not set."
            print(msg)
            raise ValueError(msg)

class GhiaStrategy():
    def get_grouped_users(self, users_automatched: Set[str], users_already_assigned: Set[str]) -> GroupedUsers:
        pass

class AppendStrategy(GhiaStrategy):
    def get_grouped_users(self, users_automatched: Set[str], users_already_assigned: Set[str]) -> GroupedUsers:
        return GroupedUsers(users_automatched=users_automatched.difference(users_already_assigned), 
            users_to_leave=users_already_assigned,
            users_to_remove=set())

class SetStrategy(GhiaStrategy):
    def get_grouped_users(self, users_automatched: Set[str], users_already_assigned: Set[str]) -> GroupedUsers:
        return GroupedUsers(users_automatched=users_automatched, 
            users_to_leave=users_already_assigned,
            users_to_remove=set())

class ChangeStrategy(GhiaStrategy):
    def get_grouped_users(self, users_automatched: Set[str], users_already_assigned: Set[str]) -> GroupedUsers:
        return GroupedUsers(users_automatched=users_automatched.difference(users_already_assigned), 
            users_to_leave=users_already_assigned.intersection(users_automatched),
            users_to_remove=users_already_assigned.difference(users_automatched))

class Strategies(Enum):
	APPEND = AppendStrategy()
	SET = SetStrategy()
	CHANGE = ChangeStrategy()