from command import Command
from command_result import CommandResult


class Who(Command):
    shortname = 'who'
    name = 'Who is on the server?'

    def invoke(self, player, *args):
        result = [self.world.players[p].name for p in self.world.players]
        return CommandResult('clientcrap', {'lines': result})
