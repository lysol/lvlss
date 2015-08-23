

class Player(object):


    def send_messages(self, msg):
        self.world.controller.send_message(self, msg)

    def __init__(self, world, name):
        self.name = name
        self.inventory = []
        self.world = world