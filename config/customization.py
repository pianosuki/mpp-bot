import json
from typing import TypeVar, Type

BotType = TypeVar("BotType", bound="MPPClient")
CommandsType = TypeVar("CommandsType", bound="Enum")
RolesType = TypeVar("RolesType", bound="Enum")


class Config:
    def __init__(self):
        pass

    @property
    def bot(self) -> Type[BotType]:
        from src.client import MPPClient
        BOT_CLASS = MPPClient
        return BOT_CLASS

    @property
    def commands(self) -> Type[CommandsType]:
        from src.commands import Commands
        COMMANDS = Commands
        return COMMANDS

    @property
    def roles(self) -> Type[RolesType]:
        from src.roles import Roles
        ROLES = Roles
        return ROLES

    @property
    def schema(self) -> dict:
        SCHEMA = "config/schema.json"
        with open(SCHEMA, "r") as db_schema:
            return json.load(db_schema)

    @property
    def defaults(self) -> dict:
        DEFAULTS = "config/defaults.json"
        with open(DEFAULTS, "r") as db_defaults:
            return json.load(db_defaults)

    @property
    def max_retry_delay(self) -> int:
        MAX_DELAY = 120
        return MAX_DELAY
