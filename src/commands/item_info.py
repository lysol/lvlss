from command import Command, is_command, CommandException
from event import Event


class ItemInfo(Command):

    @is_command
    def item_info(self, player, *args):
        if len(args) == 0:
            raise CommandException(CommandException.NOT_ENOUGH_ARGUMENTS)
        item_id = args[0]
        if item_id in player.inventory:
            item = player.inventory[item_id]
        elif item_id in player.location.lobjects:
            item = player.location.lobjects[item_id]
        else:
            raise CommandException(CommandException.UNKNOWN_ITEM)

        return Event('item-info', {"item": item.to_dict()})