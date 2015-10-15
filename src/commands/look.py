from command import Command, is_command


class Look(Command):

    shortname = 'look'
    name = 'Look around you'

    @is_command('l')
    def l(self, player, *args):
        return self.look(player, *args)

    @is_command
    def look(self, player, *args):
        self.send_player_location(player)
        self.send_player_location_areas(player)
        self.send_player_location_inventory(player)
        self.send_player_status(player)