from enum import Enum
from typing import List
from config import Config, RolesType

config = Config()


class Roles(Enum):
    """
        Enumeration of supported roles.

        Member datastructure:

        - Description of the role:

          - "Role description"

        Example:
            USER = "A normal user"
        """

    USER = "A normal user"

    ADMIN = "A user with administrator privileges"

    BOT = "A user with the 'BOT' tag"

    WHITELIST = "A user that is whitelisted"

    OWNER = "A user that has full ownership of the bot"


class Role:

    roles: RolesType = config.roles

    __members__ = {**{name: member.value for name, member in roles.__members__.items()}, **{"UNKNOWN": "Failsafe pseudo-member"}}

    def __init__(self, name: str, description: str):
        self.description = description

        self._name = name

    def __str__(self):
        return f"{self._name}"

    def __eq__(self, other: "Role") -> bool:
        if not isinstance(other, Role):
            return False
        return self._name == other._name

    @classmethod
    def from_name(cls, role_name: str) -> "Role":
        name, description = "UNKNOWN", cls.__members__["UNKNOWN"]
        for key, value in cls.__members__.items():
            if role_name.casefold() == key.casefold():
                name, description = key, value
        return cls(name, description)

    @classmethod
    def get_commands(cls) -> List["Role"]:
        return [member for member in cls.get_members() if member._name != "UNKNOWN"]

    @classmethod
    def get_members(cls) -> List["Role"]:
        return [cls(name, *args) for name, args in cls.__members__.items()]

    @property
    def name(self) -> str:
        return self._name.lower()
