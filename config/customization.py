import json
from typing import TypeVar, Type

BotType = TypeVar("BotType", bound="MPPClient")
CommandsType = TypeVar("CommandsType", bound="Enum")


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
    def schema(self) -> dict:
        SCHEMA = "config/schema.json"
        with open(SCHEMA, "r") as db_schema:
            return json.load(db_schema)
