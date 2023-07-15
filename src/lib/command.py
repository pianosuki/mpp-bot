from typing import Optional, Any, Tuple
from src.commands import Command
from src.exceptions import *


class CommandMessage:
    def __init__(self, command: Command, args: list, opts: dict):
        self.type = command
        self.args = self.filter_arguments(args)
        self.opts = self.filter_options(opts)

        # for i, arg in enumerate(self.type.args):
        #     if arg["required"] and len(self.args) < i + 1:
        #         raise ArgumentMissingError(arg["attribute"])
        #
        # for opt in self.type.opts:
        #     if opt["character"] not in self.opts and opt["type"] is bool:
        #         self.opts[opt] = False

    def __str__(self):
        return f"CommandMessage Object: (command={self.type}, args={self.args}, opts={self.opts})"

    def filter_arguments(self, args: list) -> list:
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
        args = [value for value in arg_generator]
        opts = {key: value for key, value in opt_generator}
        return cls(command, args, opts)

    @staticmethod
    def argument_parser(segments: list, command: Command) -> Any:
        if not command.args:
            return "Nothing to parse"
        arg_index = 0
        for i, arg in enumerate(segments):
            if not arg.startswith("-"):
                if (
                    i == 0
                    or (i - 1 > -1 and not segments[i - 1].startswith("-"))
                    or (segments[i - 1].startswith("-") and segments[i - 1][1:] not in command.opt_chars)
                    or (segments[i - 1].startswith("-") and segments[i - 1][1:] in command.opt_chars and command.get_opt_type(segments[i - 1][1:]) is bool)
                ) and arg_index < len(command.args):
                    argument_type = command.get_arg_type(arg_index)
                    is_trailing = command.args[arg_index]["trailing"]
                    try:
                        yield argument_type(arg)
                        arg_index += 1
                        if is_trailing:
                            break
                    except ValueError:
                        raise ArgumentValueError(arg, argument_type)

    @staticmethod
    def options_parser(segments: list, command: Command) -> Tuple[str, Optional[Any]]:
        if not command.opts:
            return "Nothing to parse"
        for i, arg in enumerate(segments):
            char = arg[1:]
            if arg.startswith("-") and char in command.opt_chars:
                option_name = command.get_opt_name(char)
                option_type = command.get_opt_type(char)
                if option_type is not bool:
                    if i + 1 < len(segments):
                        try:
                            yield option_name, option_type(segments[i + 1])
                        except ValueError:
                            raise OptionValueError((char, segments[i + 1]), option_type)
                else:
                    yield option_name, True
