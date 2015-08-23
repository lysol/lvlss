from command import Command
from event import Event


class Look(Command):

    shortname = 'look'
    name = 'Look around you'

    def invoke(self, player, *args):
        self.tell_player(player, [
            "You are in %s:" % player.location.name, 
            "", 
            player.location.description
            ])