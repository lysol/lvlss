from command import Command
from command_result import CommandResult


class SetName(Command):
    name = 'Set your name'
    shortname = 'nick'

    def invoke(self, player, **kwargs):
        print kwargs
        if self.world.player_name_exists(kwargs['nick']):
            return CommandResult('name_collision')
        self.world.add_player(kwargs['nick'])
        return CommandResult('name_set', {"player_name": kwargs['nick']})
