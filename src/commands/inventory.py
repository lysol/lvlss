from command import Command, is_command, CommandException


class Inventory(Command):

    @is_command('i')
    def get(self, player, *args):
        return self.inv(player, *args)

    @is_command
    def inv(self, player, *args):
        lines = ['Inventory:', ]
        lines.extend(["%d: %s" % (i + 1, item.name) for i, item in enumerate(player.inventory)])
        self.tell_player(player, lines)