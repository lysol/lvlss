from command import Command, is_command
from event import Event


class Look(Command):

    shortname = 'look'
    name = 'Look around you'

    @is_command
    def look(self, player, *args):
        lines = [player.location.description, '', 'Places nearby:']
        other_areas = player.location.links_to
        lines.extend(['%d: %s' % (i + 1, area.name) for i, area in enumerate(other_areas)])
        self.tell_player(player, lines)