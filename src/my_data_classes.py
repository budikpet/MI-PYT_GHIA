from enum import Enum
from typing import Set, List
from dataclasses import dataclass, field

class UserStatus(Enum):
    ADD = "+"
    LEAVE = "="
    REMOVE = "-"

@dataclass
class GroupedUsers():
    users_automatched: Set[str] = field(default_factory=set)
    users_to_leave: Set[str] = field(default_factory=set)
    users_to_remove: Set[str] = field(default_factory=set)

    def update_needed(self) -> bool:
        return len(self.users_automatched) > 0 or len(self.users_to_remove) > 0

    def get_users_to_assign(self) -> Set[str]:
        return list(self.users_automatched | self.users_to_leave)

    def get_output_list(self) -> List[str]:
        outputList = [(UserStatus.ADD, user) for user in list(self.users_automatched)]
        outputList.extend([(UserStatus.LEAVE, user) for user in list(self.users_to_leave)])
        outputList.extend([(UserStatus.REMOVE, user) for user in list(self.users_to_remove)])
        
        return sorted(outputList, key=lambda pair: pair[1].lower())

    def has_users(self) -> bool:
        return len(self.users_automatched) > 0 or len(self.users_to_remove) > 0 or len(self.users_to_leave) > 0