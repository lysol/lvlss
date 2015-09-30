from uuid import uuid4

class Area(object):

    def __getstate__(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "links_to": self.links_to,
            "lobjects": self.lobjects,
            "script_body": self.script_body,
            "power": self.power,
            "max_power": self.max_power,
            "recharge_rate": self.recharge_rate,
            "players": self.players
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

    def charge(self):
        self.power += self.recharge_rate
        if self.power > self.max_power:
            self.power = self.max_power

    def __init__(self, name, description, max_power=1000, recharge_rate=50, id=None):
        self.name = name
        self.description = description
        self.links_to = {}
        self.lobjects = {}
        self.players = []
        if id is None:
            id = str(uuid4())
        self.id = id
        self.script_body = ''
        self.max_power = max_power
        self.recharge_rate = recharge_rate
        self.power = max_power