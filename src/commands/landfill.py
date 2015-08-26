from command import Command, is_command, CommandException
from area import Area
from look import Look

class Landfill(Command):

    @is_command('lf')
    def lf(self, player, *args):
        return self.landfill(player, *args)

    @is_command
    def landfill(self, player, *args):
        if len(args) < 2:
            raise CommandException(CommandException.NOT_ENOUGH_ARGUMENTS)

        arglist = list(args)

        one_way = len(arglist) > 2 and arglist[2] == 'oneway'

        area = Area(args[0], args[1])
        player.location.link_to(area, one_way=one_way)

        self.tell_player(player, "Wow. You made a new place.")
        look = Look(self.world)
        return look.look(player)