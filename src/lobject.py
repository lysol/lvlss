class LObject:

    def __getstate__(self):
        return {"name": self.name, "value": self.value}

    def __init__(self, name, value):
        self.name = name
        self.value = value
