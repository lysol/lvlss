import commands


class Command(object):

    shortname = 'command'
    name = 'Reference Command'

    @property
    def all_commands(self):
        return commands.all_commands

    def invoke(self, player, *args):
        raise NotImplementedError("Please define this.")

    def __init__(self, world):
        self.world = world
