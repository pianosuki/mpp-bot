from typing import Any, Tuple

__all__ = ["ArgumentValueError", "OptionValueError", "ArgumentMissingError", "OptionMutualExclusivityError"]


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


class OptionMutualExclusivityError(Exception):
    def __init__(self, option: str, conflicting_option: str):
        self.option = option
        self.conflict = conflicting_option
        self.error = f"**Error:** Option `{self.option}` cannot be used simultaneously with option `{self.conflict}`"
        super().__init__(self.error)
