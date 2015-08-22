from command import Command
from command_result import CommandResult


class SetName(Command):
    name = 'Set your name'
    shortname = 'nick'

    def invoke(self, player, *args):
        if self.world.player_name_exists(args[0]):
            return CommandResult('name_collision')
        self.world.add_player(args[0])
        return CommandResult('name_set', {"player_name": args[0]})
