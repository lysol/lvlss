from uuid import uuid4

class LObject:

    def __getstate__(self):
        return {
            "id": self.id,
            "name": self.name,
            "value": self.value,
            "script_body": self.script_body
        }

    def to_dict(self):
        return self.__getstate__()

    def set_location(self, location):
        self.location = location

    def set_script(self, script_body):
        self.script_body = script_body

    def __init__(self, name, description=None, value=0):
        self.name = name
        self.value = value
        self.description = description
        self.location = None
        self.id = str(uuid4())
        self.script_body = ''