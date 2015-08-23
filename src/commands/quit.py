from command import Command
from event import Event


class Quit(Command):

    shortname = 'quit'
    name = 'Disconnect from the game'

    def invoke(self, player, *args):
        self.world.remove_player(player)
        return Event('quit')
