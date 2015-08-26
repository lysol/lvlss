from command import Command, is_command, CommandException
from lobject import LObject

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
                arglist[2] = 0
        except ValueError:
            raise CommandException(CommandException.NOT_A_NUMBER, 3)

        item = LObject(arglist[0], description=arglist[1], value=arglist[2])
        player.location.lobjects.append(item)
        self.tell_player(player, "You made: %s" % item.name)