from command import Command, is_command, CommandException


class Drop(Command):

    @is_command('d')
    def d(self, player, *args):
        return self.drop(player, *args)

    @is_command
    def drop(self, player, *args):
        if len(args) == 0:
            raise CommandException(CommandException.NOT_ENOUGH_ARGUMENTS)
        item_index = int(args[0]) - 1
        if item_index < len(player.inventory):
            item = player.inventory.pop(item_index)
            player.location.lobjects.append(item)
            self.tell_player(player, "You dropped: %s" % item.name)
        else:
            raise CommandException(CommandException.NO_ITEM_IN_INVENTORY)
