from command import Command
from command_result import CommandResult


class Quit(Command):

    shortname = 'quit'
    name = 'Disconnect from the game'

    def invoke(self, player, **kwargs):
        self.world.remove_player(player)
        return CommandResult('quit')
