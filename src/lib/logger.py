class Logger:
    def __init__(self, name: str):
        self.name = name

    def log(self, data):
        print(f"[{self.name}] {str(data).strip()}")
