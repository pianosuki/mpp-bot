import json, re
from enum import Enum
from typing import Union, Any, List, Optional


class MPPMessage:

    class ServerBound(Enum):
        MESSAGE = "a", {"message": str}, {"reply_to": str}
        DISCONNECT = "bye", {}, {}
        SETCHANNEL = "ch", {"_id": str}, {"set": dict}
        CROWN = "chown", {}, {"_id": str}
        CHANNELSETTINGS = "chset", {"set": dict}, {}
        CUSTOM = "custom", {"data": Any}, {"target": dict}
        DEVICES = "devices", {"list": list}, {}
        DIRECTMESSAGE = "dm", {"message": str, "_id": str}, {"reply_to": str}
        CONNECT = "hi", {}, {"token": str, "code": str, "login": dict}
        KICKBAN = "kickban", {"_id": str, "ms": int}, {}
        UNBAN = "unban", {"_id": str}, {}
        USERSET = "userset", {"set": dict}, {}
        MOUSE = "m", {"x": float, "y": float}, {}
        NOTES = "n", {"t": int, "n": list}, {}
        PING = "t", {}, {"e": int}
        SUBCUSTOM = "+custom", {}, {}
        SUBROOMLIST = "+ls", {}, {}
        UNSUBCUSTOM = "-custom", {}, {}
        UNSUBROOMLIST = "-ls", {}, {}
        UNKNOWN = "unknown", {}, {}

        def __init__(self, message_name: str, required_arguments: dict, optional_arguments: dict):
            self.m = message_name
            self.required_args = required_arguments
            self.optional_args = optional_arguments

    class ClientBound(Enum):
        MESSAGE = "a", {"id": str, "t": int, "a": str, "p": dict}, {"r": str}
        DIRECTMESSAGE = "dm", {"id": str, "t": int, "a": str, "sender": dict, "recipient": dict}, {"r": str}
        VERIFY = "b", {"code": str}, {}
        DISCONNECT = "bye", {"p": str}, {}
        CHATHISTORY = "c", {"c": list}, {}
        CHANNELINFO = "ch", {"p": str, "ppl": list, "ch": dict}, {}
        CUSTOM = "custom", {"data": Any, "p": str}, {}
        CONNECT = "hi", {"t": int, "u": dict, "permissions": dict, "accountInfo": dict}, {"token": str}
        ROOMLIST = "ls", {"c": bool, "u": list}, {}
        MOUSE = "m", {"id": str, "x": str, "y": str}, {}
        NOTES = "n", {"t": int, "p": str, "n": list}, {}
        NOTIFICATION = "notification", {}, {"duration": int, "class": str, "id": str, "title": str, "text": str, "html": str, "target": str}
        NOTEQUOTA = "nq", {"allowance": int, "max": int, "maxHistLen": int}, {}
        PARTICIPANTADDED = "p", {"id": str, "_id": str, "name": str, "color": str, "x": float, "y": float}, {"tag": dict, "vanished": bool}
        PONG = "t", {"t": int}, {"e": int}
        UNKNOWN = "unknown", {}, {}

        def __init__(self, message_name, required_arguments, optional_arguments):
            self.m = message_name
            self.required_args = required_arguments
            self.optional_args = optional_arguments

    def __init__(self, message_type: Union[ServerBound, ClientBound], **kwargs):
        self.type = message_type
        self.payload = kwargs

    def __str__(self):
        return f"MPPMessage Object: (type={self.type}, {', '.join(['{}={}'.format(key, value) for key, value in self.payload.items()])})"

    def serialize(self) -> dict:
        json_msg = {key: value for key, value in self.payload.items()}
        json_msg["m"] = self.type.m
        return json_msg

    def search(self, pattern, obj=None) -> Optional[str]:
        if obj is None:
            obj = self.payload
        if isinstance(obj, dict):
            for key, value in obj.items():
                result = self.search(pattern, value)
                if result:
                    return result
        elif isinstance(obj, list):
            for item in obj:
                result = self.search(pattern, item)
                if result:
                    return result
        else:
            if isinstance(obj, str):
                match = re.search(pattern, obj)
                if match:
                    return str(match.group())
        return None

    @classmethod
    def deserialize(cls, data: str) -> List["MPPMessage"]:
        messages = []
        json_msgs = json.loads(data)
        for json_msg in json_msgs:
            try:
                m = json_msg.pop("m")
                message_type = None
                for member in MPPMessage.ClientBound:
                    if member.value[0] == m:
                        message_type = member
                        break
                if message_type is None:
                    raise ValueError(f"No such message type '{m}'")
            except (KeyError, ValueError):
                message_type = MPPMessage.ClientBound.UNKNOWN
            messages.append(cls(message_type, **json_msg))
        return messages

    @property
    def sender(self) -> Optional[str]:
        pattern = r"^[0-9a-f]{24}$"
        return self.search(pattern)
