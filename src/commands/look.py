from command import Command, is_command


class Look(Command):

    shortname = 'look'
    name = 'Look around you'

    @is_command
    def look(self, player, *args):
        lines = [player.location.description, '', 'Places nearby:']
        other_areas = player.location.links_to
        lines.extend(['%d: %s' % (i + 1, area.name) for i, area in
                      enumerate(other_areas)])
        lines.extend(['', 'Items here:'])
        lines.extend(['%d: %s' % (i + 1, item.name) for i, item in
                      enumerate(player.location.lobjects)])
        self.tell_player(player, lines)
