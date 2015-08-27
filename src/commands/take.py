from command import Command, is_command, CommandException


class Take(Command):

    @is_command('get')
    def get(self, player, *args):
        return self.take(player, *args)

    @is_command
    def take(self, player, *args):
        if len(args) == 0:
            raise CommandException(CommandException.NOT_ENOUGH_ARGUMENTS)
        item_index = int(args[0]) - 1
        if item_index < len(player.location.lobjects):
            item = player.location.lobjects.pop(item_index)
            player.inventory.append(item)
            self.tell_player(player, "You took: %s" % item.name)
        else:
            raise CommandException(CommandException.NO_ITEM_HERE)
