from enum import Enum
from ghia.github.config_data import ConfigData
from ghia.github.my_data_classes import GroupedUsers, UserStatus
import requests
import click
from typing import Set, List

class GhiaContext():
    """ Holds all data that are important during the entire execution of the GHIA programme. """

    def __init__(self, base: str, strategy: str, dry_run: bool, config_auth, config_rules, reposlug: str = None, session = None):
        self.base: str = base
        self.strategy: GhiaStrategy = Strategies[strategy.upper()].value
        self.dry_run: bool = dry_run
        self.reposlug: str = reposlug
        self.session: requests.session = session
        self.username: str = None

        # Get configuration
        self.config_data: ConfigData = ConfigData(config_auth, config_rules)

    def get_user_patterns(self, by_user=False):
        """
            Returns a dictionary of patterns loaded from the rules config file. Keys of the dictionary are:
            - locations of the pattern inside the issue
            - usernames (if by_user is True)
        """

        if by_user:
            return self.config_data.user_patterns_by_user

        return self.config_data.user_patterns

    def get_token(self):
        """ Returns the Github token. """
        return self.config_data.token

    def get_secret(self):
        """ Returns the Github repository secret. """
        return self.config_data.secret

    def get_fallback_label(self):
        """ Returns the name of the fallback label (or None if not specified). """
        return self.config_data.fallback_label

    def get_reposlug(self):
        """ Returns the specified reposlug. """

        if self.reposlug is not None:
            return self.reposlug
        else:
            msg = "Reposlug not set."
            print(msg)
            raise ValueError(msg)

    def get_trigger_actions(self):
        """ Returns actions that can trigger the Github webhook. """
        return self.config_data.trigger_actions

    

class GhiaStrategy():
    """ The base strategy used for polymorphism Strategy pattern. """

    def get_grouped_users(self, users_automatched: Set[str], users_already_assigned: Set[str]) -> GroupedUsers:
        """ Returns the GroupedUsers object that is filled according to the specific strategy. """
        pass

class AppendStrategy(GhiaStrategy):
    """ 
        Append Ghia strategy.

        New users are added to the currently specified users of the issue. Currently specified users are left alone.
        
    """

    def get_grouped_users(self, users_automatched: Set[str], users_already_assigned: Set[str]) -> GroupedUsers:
        """ Returns the GroupedUsers object that is filled according to the specific strategy. """

        users_found = len(users_automatched) != 0
        return GroupedUsers(users_found_by_rules=users_found, 
            users_automatched=users_automatched.difference(users_already_assigned), 
            users_to_leave=users_already_assigned,
            users_to_remove=set())

class SetStrategy(GhiaStrategy):
    """ 
        Set Ghia strategy.

        New users are added to the issue only if there are no users specified.
        
    """

    def get_grouped_users(self, users_automatched: Set[str], users_already_assigned: Set[str]) -> GroupedUsers:
        """ Returns the GroupedUsers object that is filled according to the specific strategy. """

        users_found = len(users_automatched) != 0
        return GroupedUsers(users_found_by_rules=users_found,
            users_automatched=users_automatched, 
            users_to_leave=users_already_assigned,
            users_to_remove=set())

class ChangeStrategy(GhiaStrategy):
    """ 
        Change Ghia strategy.

        New users are added to the issue. Users that shouldn't be specified in the issue according to rules are removed.
        
    """
    
    
    def get_grouped_users(self, users_automatched: Set[str], users_already_assigned: Set[str]) -> GroupedUsers:
        """ Returns the GroupedUsers object that is filled according to the specific strategy. """

        users_found = len(users_automatched) != 0
        return GroupedUsers(users_found_by_rules=users_found,
            users_automatched=users_automatched.difference(users_already_assigned), 
            users_to_leave=users_already_assigned.intersection(users_automatched),
            users_to_remove=users_already_assigned.difference(users_automatched))

class Strategies(Enum):
    """ List of all strategies that are available. """
    APPEND = AppendStrategy()
    SET = SetStrategy()
    CHANGE = ChangeStrategy()