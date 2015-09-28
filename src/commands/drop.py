from command import Command, is_command, CommandException


class Drop(Command):

    @is_command('d')
    def d(self, player, *args):
        return self.drop(player, *args)

    @is_command
    def drop(self, player, *args):
        if len(args) == 0:
            raise CommandException(CommandException.NOT_ENOUGH_ARGUMENTS)
        item_id = args[0]
        if item_id in player.inventory:
            item = player.inventory[item_id]
            player.location.lobjects[item.id] = item
            del player.inventory[item_id]
            self.world.emit_event('drop', {
                'item': item.to_dict(), 
                'player': player.to_dict(),
                'area': player.location.to_dict()
                }, scope=[player.location, player])
            self.tell_player(player, "You dropped: %s" % item.name)
            self.send_player_location_inventory(player)
            self.send_player_inventory(player)
        else:
            raise CommandException(CommandException.NO_ITEM_IN_INVENTORY)
