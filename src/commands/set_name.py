from command import Command, is_command
from event import Event


class SetName(Command):
    name = 'Set your name'
    shortname = 'nick'
    unauthenticated = True

    @is_command
    def nick(self, player, *args):
        if self.world.player_name_exists(args[0]):
            return Event('name_collision')
        player = self.world.add_player(args[0])
        self.send_player_location(player)
        self.send_player_location_areas(player)
        self.send_player_location_inventory(player)
        self.send_player_inventory(player)
        return Event('name_set', {"player_name": args[0]})
