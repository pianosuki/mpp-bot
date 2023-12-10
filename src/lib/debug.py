from enum import Enum


class Debug(Enum):
    NONE = -1
    ERROR = 0
    CONNECTION = 1
    DATABASE = 2
    INBOUND = 4
    OUTBOUND = 8
    FILESYSTEM = 16

    @staticmethod
    def from_string(debug: str) -> int:
        match debug:
            case "all" | "All" | "ALL":
                return sum(member.value for member in Debug)
            case "none" | "None" | "NONE":
                return -1
            case integer if debug.isdigit():
                return integer
            case _:
                return 0
