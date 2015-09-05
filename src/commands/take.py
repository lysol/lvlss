from command import Command, is_command, CommandException


class Take(Command):

    @is_command('get')
    def get(self, player, *args):
        return self.take(player, *args)

    @is_command
    def take(self, player, *args):
        if len(args) == 0:
            raise CommandException(CommandException.NOT_ENOUGH_ARGUMENTS)
        item_id = args[0]
        if item_id in player.location.lobjects:
            item = player.location.lobjects[item_id]
            player.inventory[item.id] = item
            self.tell_player(player, "You took: %s" % item.name)
            del(player.location.lobjects[item_id])
            self.send_player_location_inventory(player)
            self.send_player_inventory(player)
        else:
            raise CommandException(CommandException.NO_ITEM_HERE)

# TODO: Use guids instead of integers