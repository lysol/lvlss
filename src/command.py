import commands


class Command(object):

    shortname = 'command'
    name = 'Reference Command'
    unauthenticated = False

    @property
    def all_commands(self):
        return commands.all_commands

    def invoke(self, player, *args):
        raise NotImplementedError("Please define this.")

    def tell_player(self, player, msg):
        return self.world.tell_player(player, msg)

    def __init__(self, world):
        self.world = world