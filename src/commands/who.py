from command import Command
from event import Event


class Who(Command):
    shortname = 'who'
    name = 'Who is on the server?'

    def invoke(self, player, *args):
        event = [self.world.players[p].name for p in self.world.players]
        return Event('clientcrap', {'lines': event})
