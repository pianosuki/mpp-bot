from typing import Optional, Any, Tuple, Generator
from src.commands import Command
from src.lib.exceptions import *


class CommandMessage:
    def __init__(self, command: Command, args: dict, opts: dict):
        self.type = command
        self.args = self.filter_arguments(args)
        self.opts = self.filter_options(opts)

    def __str__(self):
        return f"CommandMessage Object: (command={self.type}, args={self.args}, opts={self.opts})"

    def filter_arguments(self, args: dict) -> dict:
        filtered = args.copy()
        for i, arg in enumerate(self.type.args):
            if arg["required"] and len(args) < i + 1:
                raise ArgumentMissingError(arg["attribute"])
        return filtered

    def filter_options(self, opts: dict) -> dict:
        filtered = opts.copy()
        for opt in self.type.opts:
            if opt["name"] not in opts and opt["type"] is bool:
                filtered[opt["name"]] = False
            for conflicting_option in opt["mutually_exclusive_to"]:
                if opt["name"] in opts and conflicting_option in opts:
                    raise OptionMutualExclusivityError(opt["name"], conflicting_option)
        return filtered

    @classmethod
    def deserialize(cls, message: str) -> "CommandMessage":
        segments = message[1:].split()
        command = Command.from_name(segments.pop(0))
        arg_generator = cls.argument_parser(segments, command)
        opt_generator = cls.options_parser(segments, command)
        args = {key: value for key, value in arg_generator}
        opts = {key: value for key, value in opt_generator}
        return cls(command, args, opts)

    @classmethod
    def argument_parser(cls, segments: list, command: Command) -> Generator[Tuple[str, Any], None, Optional[str]]:
        if not command.args:
            return "Nothing to parse"
        arg_index = 0
        for i, arg in enumerate(segments):
            if cls.is_argument(i, arg, segments, command, arg_index):
                argument_name = command.get_arg_name(arg_index)
                argument_type = command.get_arg_type(arg_index)
                is_trailing = command.args[arg_index]["trailing"]
                try:
                    arg_index += 1
                    if not is_trailing:
                        value = argument_type(arg)
                    else:
                        value = argument_type(" ".join(segments[i:]))
                    yield argument_name, value
                except ValueError:
                    raise ArgumentValueError(arg, argument_type)

    @classmethod
    def options_parser(cls, segments: list, command: Command) -> Generator[Tuple[str, Optional[Any]], None, Optional[str]]:
        if not command.opts:
            return "Nothing to parse"
        arg_index = 0
        opt_index = 0
        trailing_index = None
        for i, arg in enumerate(segments):
            if cls.is_option(i, arg, command, opt_index, trailing_index):
                character = arg[1:]
                option_name = command.get_opt_name(character)
                option_type = command.get_opt_type(character)
                if option_type is not bool:
                    if i + 1 < len(segments) and not segments[i + 1].startswith("-"):
                        value = option_type(segments[i + 1])
                    else:
                        raise OptionMissingError(option_name)
                else:
                    value = True
                try:
                    opt_index += 1
                    yield option_name, value
                except ValueError:
                    raise OptionValueError((character, segments[i + 1]), option_type)
            elif cls.is_argument(i, arg, segments, command, arg_index):
                if command.args[arg_index]["trailing"]:
                    trailing_index = i
                arg_index += 1

    @staticmethod
    def is_argument(i: int, arg: str, segments: list, command: Command, arg_index: int) -> bool:
        return (
            not arg.startswith("-")
            and (
                i == 0
                or (i != 0 and not segments[i - 1].startswith("-"))
                or (segments[i - 1].startswith("-") and segments[i - 1][1:] not in command.opt_chars)
                or (segments[i - 1].startswith("-") and segments[i - 1][1:] in command.opt_chars and command.get_opt_type(segments[i - 1][1:]) is bool)
            )
            and arg_index < len(command.args)
        )

    @staticmethod
    def is_option(i: int, arg: str, command: Command, opt_index: int, trailing_index: Optional[int]) -> bool:
        return (
            (
                arg.startswith("-")
                and len(arg) > 1
                and arg[1:] in command.opt_chars
                and opt_index < len(command.opts)
            ) and (
                False if (
                    trailing_index is not None
                    and i > trailing_index
                ) else True
            )
        )
