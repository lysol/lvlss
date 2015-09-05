

class Player(object):

    def __getstate__(self):
        return {
            "name": self.name,
            "inventory": self.inventory,
            "signed_in": False
            }

    def send_messages(self, msg):
        self.world.controller.send_message(self, msg)

    def set_world(self, world):
        setattr(self, 'world', world)

    def set_location(self, area):
        self.location = area

    def __init__(self, world, name):
        self.name = name
        self.inventory = {}
        self.world = world
        self.signed_in = False