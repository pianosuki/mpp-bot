from .debug import Debug


class Logger:
    def __init__(self, name: str, debug: int):
        self.name = name
        self.debug = debug

    def log(self, debug_type: Debug, data: str):
        if self.debug & debug_type.value and not self.debug < 0:
            print(f"[{self.name} - {debug_type.name}] {str(data).strip()}")
