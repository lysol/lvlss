from command import Command, is_command, CommandException
from lobject import LObject
import copy

class Make(Command):

    @is_command('m')
    def m(self, player, *args):
        return self.make(player, *args)

    @is_command
    def make(self, player, *args):
        if len(args) < 2:
            raise CommandException(CommandException.NOT_ENOUGH_ARGUMENTS)

        arglist = list(args)
        try:
            if len(arglist) > 2:
                arglist[2] = int(arglist[2])
            else:
                arglist.append(0)
        except ValueError:
            raise CommandException(CommandException.NOT_A_NUMBER, 3)

        if player.credits < 1:
            raise CommandException(CommandException.NOT_ENOUGH_CREDITS, 1)
        item = LObject(arglist[0], description=arglist[1], value=arglist[2])
        player.inventory[item.id] = item
        player.credits -= 1
        item.set_parent(player)
        self.tell_player(player, "You made: %s" % item.name)
        self.send_player_location(player)
        self.send_player_location_areas(player)
        self.send_player_inventory(player)
        self.send_player_status(player)

    @is_command
    def copy(self, player, *args):
        if len(args) < 1:
            raise CommandException(CommandException.NOT_ENOUGH_ARGUMENTS)

        arglist = list(args)

        if player.credits < 1:
            raise CommandException(CommandException.NOT_ENOUGH_CREDITS, 1)

        original = self.world.find_object(args[0])
        if original is None:
            raise CommandException(CommandException.NO_ITEM_HERE)
        if original.parent.id != player.id:
            raise CommandException(CommandException.NO_ITEM_IN_INVENTORY)
        copied = original.clone()
        self.world.image_handler.copy_image(original.id, copied.id)

        player.inventory[copied.id] = copied
        player.credits -= 1
        copied.set_parent(player)
        self.tell_player(player, "You copied: %s" % copied.name)
        self.send_player_location(player)
        self.send_player_location_areas(player)
        self.send_player_inventory(player)
        self.send_player_status(player)
