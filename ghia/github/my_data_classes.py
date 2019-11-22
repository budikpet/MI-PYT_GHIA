from enum import Enum
from typing import Set, List
from dataclasses import dataclass, field

class Issue():
    """ 
    Parsed data from a dictionary received from requests.

    Args:
        title (str): Title of the issue.
        body (str): Description of the issue.
        html_url (str): URL of the issue.
        number (str): Number of the issue.
        assignees (List[str]): Already assigned users.
        labels (List[str]): Already assigned labels.
    
    """
    
    def __init__(self, issue):
        self.title = issue["title"]
        self.body = issue["body"]
        self.html_url = issue["html_url"]
        self.number = issue["number"]

        self.assignees = [assignee["login"] for assignee in issue["assignees"]]
        self.labels = [label["name"] for label in issue["labels"]]

@dataclass
class RuleLocation():
    name: str
    color: str

class Rules(Enum):
    TITLE = RuleLocation(name="title", color="blue")
    TEXT = RuleLocation(name="text", color="green")
    LABEL = RuleLocation(name="label", color="rgb(151, 151, 48)")
    ANY = RuleLocation(name="any", color="red")

class UserStatus(Enum):
    ADD = "+"
    LEAVE = "="
    REMOVE = "-"

@dataclass
class GroupedUsers():
    """
    Result of pattern matching. Users separated to different lists according to their status.

    """
    users_found_by_rules: bool
    users_automatched: Set[str] = field(default_factory=set)
    users_to_leave: Set[str] = field(default_factory=set)
    users_to_remove: Set[str] = field(default_factory=set)

    def update_needed(self) -> bool:
        """
        
        Returns:
            bool: True if the issue needs to be updated i. e. if at least 1 user has to be added or removed.
        """        

        return len(self.users_automatched) > 0 or len(self.users_to_remove) > 0

    def get_users_to_assign(self) -> Set[str]:
        """
        
        Returns:
            Set[str]: Set of all users that have to be in the outgoing PATCH request to have the desired effect.
        """        

        return list(self.users_automatched | self.users_to_leave)

    def get_output_list(self) -> List[str]:
        """
        Loads users from all separate lists into 1 list.
        
        Returns:
            List[str]: List of all users sorted alphabetically.
        """        

        outputList = [(UserStatus.ADD, user) for user in list(self.users_automatched)]
        outputList.extend([(UserStatus.LEAVE, user) for user in list(self.users_to_leave)])
        outputList.extend([(UserStatus.REMOVE, user) for user in list(self.users_to_remove)])
        
        return sorted(outputList, key=lambda pair: pair[1].lower())

    def has_users(self) -> bool:
        """
        
        Returns:
            bool: True if any users are specified in any list.
        """        

        return len(self.users_automatched) > 0 or len(self.users_to_remove) > 0 or len(self.users_to_leave) > 0