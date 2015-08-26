from command import Command, is_command
from event import Event


class Quit(Command):

    shortname = 'quit'
    name = 'Disconnect from the game'

    @is_command
    def quit(self, player, *args):
        self.world.remove_player(player)
        return Event('quit')
