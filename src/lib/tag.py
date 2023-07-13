class Tag:
    def __init__(self, text: str, color: str):
        self.text = text
        self.color = color

    def __str__(self):
        return f"Tag Object: (text={self.text}, color={self.color})"

    def serialize(self) -> dict:
        return {"text": self.text, "color": self.color}
