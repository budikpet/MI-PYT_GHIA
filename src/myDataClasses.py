from enum import Enum
from typing import Set, List
from dataclasses import dataclass, field

class UserStatus(Enum):
    ADD = "+"
    LEAVE = "="
    REMOVE = "-"

@dataclass
class GroupedUsers():
    usersAutoMatched: Set[str] = field(default_factory=set)
    usersToLeave: Set[str] = field(default_factory=set)
    usersToRemove: Set[str] = field(default_factory=set)

    def updateNeeded(self) -> bool:
        return len(self.usersAutoMatched) > 0 or len(self.usersToRemove) > 0

    def getUsersToAssign(self) -> Set[str]:
        return list(self.usersAutoMatched | self.usersToLeave)

    def getOutputList(self) -> List[str]:
        outputList = [(UserStatus.ADD, user) for user in list(self.usersAutoMatched)]
        outputList.extend([(UserStatus.LEAVE, user) for user in list(self.usersToLeave)])
        outputList.extend([(UserStatus.REMOVE, user) for user in list(self.usersToRemove)])
        
        return sorted(outputList, key=lambda pair: pair[1].lower())

    def hasUsers(self) -> bool:
        return len(self.usersAutoMatched) > 0 or len(self.usersToRemove) > 0 or len(self.usersToLeave) > 0