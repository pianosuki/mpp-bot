from enum import Enum
from typing import List, Dict, Any, Optional
from src.roles import Role
from config import Config, CommandsType

config = Config()


class Commands(Enum):
    """
    Enumeration of supported commands.

    Member datastructure:

    - Description of the command:

      - "Command description"

    - Role(s) required for the command:

      - ["List", "of", "roles"] (None for no role requirement)

    - List of dictionaries for each argument:

      - "name": <str>,
      - "type": <python type to store as>, (Used for type casting)
      - "required": <bool>,
      - "trailing": <bool> (Allows spaces by forcing it as the last argument)

    - List of dictionaries for each option:

      - "name": <str>,
      - "type": <python_type_to_store_as>,
      - "character": <str>
      - "mutually_exclusive_to" [OPTIONAL]: <list of other options' "name" values> (Ensures that this option cannot be used simultaneously with any of the specified options)

    Example:
        ECHO = (
            "Echos a message back to the user",\n
            ["user"]\n
            [{"name": "message", "type": str, "required": True, "trailing": True}],\n
            [{"name": "uppercase", "type": bool, "character": "u", "mutually_exclusive_to": ["lowercase"]},\n
            {"name": "lowercase", "type": bool, "character": "l", "mutually_exclusive_to": ["uppercase"]}]\n
        )

    Notes:
        - The "name" values must be unique across both the arguments and options.
        - There cannot be more than one "trailing" argument.
    """

    HELP = (
        "Prints usage of supported commands",
        None,
        [],
        []
    )

    ECHO = (
        "Echos a message back to the user",
        ["user"],
        [{"name": "message", "type": str, "required": True, "trailing": True}],
        [
            {"name": "uppercase", "type": bool, "character": "u", "mutually_exclusive_to": ["lowercase"]},
            {"name": "lowercase", "type": bool, "character": "l", "mutually_exclusive_to": ["uppercase"]}
        ]
    )

    GAMING = (
        "Rhythm gaming brought straight to your piano! Provide a link to or filename of a .mid and get rewarded with score based on your performance accuracy",
        ["user"],
        [{"name": "midi", "type": str, "required": False, "trailing": True}],
        [
            {"name": "list", "type": bool, "character": "l"},
            {"name": "output", "type": str, "character": "o"}
        ]
    )


class Command:

    commands: CommandsType = config.commands

    __members__ = {**{name: member.value for name, member in commands.__members__.items()}, **{"UNKNOWN": ("Failsafe pseudo-member", None, [], [])}}

    def __init__(self, name: str, description: str, roles: Optional[List[str]], args: List[Dict[str, Any]], opts: List[Dict[str, Any]]):
        self.description = description
        self.args = args
        self.opts = opts

        self._name = name
        self._roles = roles

    def __str__(self):
        return f"{self._name}"

    def get_arg_type(self, argument_index: int) -> Optional[Any]:
        argument_type = None
        if argument_index < len(self.args):
            argument_type = self.args[argument_index]["type"]
        return argument_type

    def get_arg_name(self, argument_index: int) -> Optional[str]:
        argument_name = None
        if argument_index < len(self.args):
            argument_name = self.args[argument_index]["name"]
        return argument_name

    def get_opt_type(self, character: str) -> Optional[Any]:
        option_type = None
        for opt in self.opts:
            if opt["character"] == character:
                option_type = opt["type"]
                break
        return option_type

    def get_opt_name(self, character: str) -> Optional[str]:
        option_name = None
        for opt in self.opts:
            if opt["character"] == character:
                option_name = opt["name"]
                break
        return option_name

    @classmethod
    def from_name(cls, command_name: str) -> "Command":
        name, args = "UNKNOWN", cls.__members__["UNKNOWN"]
        for key, value in cls.__members__.items():
            if command_name.casefold() == key.casefold():
                name, args = key, value
        return cls(name, *args)

    @classmethod
    def get_commands(cls) -> List["Command"]:
        return [member for member in cls.get_members() if member._name != "UNKNOWN"]

    @classmethod
    def get_members(cls) -> List["Command"]:
        return [cls(name, *args) for name, args in cls.__members__.items()]

    @property
    def name(self) -> str:
        return self._name.lower()

    @property
    def roles(self) -> Optional[List[Role]]:
        return [Role.from_name(role) for role in self._roles] if self._roles is not None else None

    @property
    def opt_chars(self) -> List[str]:
        return [opt["character"] for opt in self.opts]
