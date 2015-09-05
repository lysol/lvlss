from uuid import uuid4

class Area(object):

    def __getstate__(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "links_to": self.links_to,
            "lobjects": self.lobjects,
            "script_body": self.script_body
            }

    def link_to(self, area, one_way=False):
        self.links_to[area.id] = area
        if not one_way:
            area.links_to[self.id] = self

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }

    def set_script(self, script_body):
        self.script_body = script_body

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.links_to = {}
        self.lobjects = {}
        self.players = []
        self.id = str(uuid4())
        self.script_body = ''