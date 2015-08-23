

class Player(object):

    def __getstate__(self):
        return {"name": self.name, "inventory": self.inventory}

    def send_messages(self, msg):
        self.world.controller.send_message(self, msg)

    def set_world(self, world):
        setattr(self, 'world', world)

    def __init__(self, world, name):
        self.name = name
        self.inventory = []
        self.world = world