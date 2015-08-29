class LObject:

    def __getstate__(self):
        return {"name": self.name, "value": self.value}

    def to_dict(self):
        return self.__getstate__()

    def set_location(self, location):
        self.location = location

    def __init__(self, name, description=None, value=0):
        self.name = name
        self.value = value
        self.description = description
        self.location = None
