from typing import Any, Tuple, List, Optional

__all__ = [
    "ArgumentValueError",
    "OptionValueError",
    "ArgumentMissingError",
    "OptionMissingError",
    "OptionMutualExclusivityError",
    "CommandAuthorizationError",
    "BotTermination",
    "HTTPError"
]


class ArgumentValueError(Exception):
    def __init__(self, argument: Any, target_type: Any):
        self.argument = argument
        self.target_type = target_type
        self.error = f"**Error:** Argument `{self.argument}` expected type *<{self.target_type.__name__}>* but received type *<{type(self.argument).__name__}>*"
        super().__init__(self.error)


class OptionValueError(Exception):
    def __init__(self, option: Tuple[str, Any], target_type: Any):
        self.option = option
        self.target_type = target_type
        self.error = f"**Error:** Option `-{self.option[0]} {self.option[1]}` expected type *<{self.target_type.__name__}>* but received type *<{type(self.option[1]).__name__}>*"
        super().__init__(self.error)


class ArgumentMissingError(Exception):
    def __init__(self, missing_argument: str):
        self.argument = missing_argument
        self.error = f"**Error:** Missing argument `{self.argument}`"
        super().__init__(self.error)


class OptionMissingError(Exception):
    def __init__(self, missing_option: str):
        self.option = missing_option
        self.error = f"**Error:** Option `{self.option}` is missing a value"
        super().__init__(self.error)


class OptionMutualExclusivityError(Exception):
    def __init__(self, option: str, conflicting_option: str):
        self.option = option
        self.conflict = conflicting_option
        self.error = f"**Error:** Option `{self.option}` cannot be used simultaneously with option `{self.conflict}`"
        super().__init__(self.error)


class CommandAuthorizationError(Exception):
    def __init__(self, command_name: str, command_role_names: Optional[List[str]]):
        self.command_name = command_name
        self.command_roles = command_role_names
        required_roles = ', '.join(['`' + role + '`' for role in self.command_roles]) if self.command_roles is not None else "`None`"
        self.error = f"**Error:** You are not authorized to use the command `{self.command_name}` which requires the following role(s): {required_roles}"
        super().__init__(self.error)


class BotTermination(Exception):
    def __init__(self, cause: Exception = None):
        self.cause = cause
        self.error = f"Terminating bot. Cause: {cause}"
        super().__init__(self.error)


class HTTPError(Exception):
    def __init__(self, url: str, status_code: int):
        self.url = url
        self.code = status_code
        self.error = f"**Error:** [Status Code: `{self.code}`] - Failed to retrieve webpage: *{self.url}*"
        super().__init__(self.error)
