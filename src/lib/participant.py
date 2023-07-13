from src.lib import Tag, Vector2D


class Participant:
    def __init__(self, client_id: str, name: str, color: str, x: float, y: float, tag: dict = None, vanished: bool = None):
        self.client_id = client_id
        self.name = name
        self.color = color
        self.pos = Vector2D(x, y)
        self.tag = Tag(**tag) if tag is not None else None
        self.vanished = vanished

    def __str__(self):
        return f"Participant Object: (client_id={self.client_id}, name={self.name}, color={self.color}, pos={self.pos}, tag={self.tag}, vanished={self.vanished})"

    def serialize(self) -> dict:
        participant_info = {
            "id": self.client_id,
            "_id": self.client_id,
            "name": self.name,
            "color": self.color,
            "x": self.pos.x,
            "y": self.pos.y,
        }
        if self.tag is not None:
            participant_info["tag"] = self.tag.serialize()
        if self.vanished is not None:
            participant_info["vanished"] = self.vanished
        return participant_info

    @classmethod
    def deserialize(cls, participant_info: dict) -> "Participant":
        return cls(client_id=participant_info["id"],
                   name=participant_info["name"],
                   color=participant_info["color"],
                   x=float(participant_info["x"]),
                   y=float(participant_info["y"]),
                   tag=participant_info.get("tag"),
                   vanished=participant_info.get("vanished"))
