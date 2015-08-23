from command import Command
from event import Event


class SetName(Command):
    name = 'Set your name'
    shortname = 'nick'
    unauthenticated = True

    def invoke(self, player, *args):
        if self.world.player_name_exists(args[0]):
            return Event('name_collision')
        self.world.add_player(args[0])
        return Event('name_set', {"player_name": args[0]})
