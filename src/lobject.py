from uuid import uuid4
import copy
import random

class LObject:

    def __getstate__(self):
        return {
            "id": self.id,
            "name": self.name,
            "value": self.value,
            "script_body": self.script_body,
            "power": self.power,
            "max_power": self.max_power,
            "recharge_rate": self.recharge_rate
        }

    def to_dict(self):
        return self.__getstate__()

    def set_location(self, location):
        self.location = location

    def set_script(self, script_body):
        self.script_body = script_body

    def charge(self):
        self.power += self.recharge_rate
        if self.power > self.max_power:
            self.power = self.max_power

    def set_parent(self, parent):
        self.parent = parent

    def clone(self):
        copied = copy.deepcopy(self)
        copied.id = str(uuid4())
        copied.max_power -= random.randint(0,2)
        return copied

    def __init__(self, name, description=None, value=0, max_power=1000, recharge_rate=50, parent=None):
        self.name = name
        self.value = value
        self.description = description
        self.location = None
        self.id = str(uuid4())
        self.script_body = ''
        self.max_power = max_power
        self.recharge_rate = recharge_rate
        self.power = max_power
        self.parent = parent