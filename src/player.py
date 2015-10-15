from uuid import uuid4


class Player(object):

    def __getstate__(self):
        return {
            "id": self.id,
            "name": self.name,
            "inventory": self.inventory,
            "signed_in": False,
            "credits": self.credits
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
        self.id = uuid4()
        self.credits = 5

    def to_dict(self):
        state = self.__getstate__()
        del(state['inventory'])  # don't need it
        return state
