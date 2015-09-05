from command import Command, is_command, CommandException
from event import Event
from look import Look

class Go(Command):
    
    @is_command('1')
    def one(self, player, *args):
        return self.go(player, '1')

    @is_command('2')
    def two(self, player, *args):
        return self.go(player, '2')

    @is_command('3')
    def three(self, player, *args):
        return self.go(player, '3')

    @is_command('4')
    def four(self, player, *args):
        return self.go(player, '4')

    @is_command
    def go(self, player, *args):
        if len(args) == 0:
            raise CommandException(CommandException.NOT_ENOUGH_ARGUMENTS)
        area_id = args[0]
        if area_id in player.location.links_to:
            player.location = player.location.links_to[area_id]
            # hacky thing....maybe needs a better interface
            look = Look(self.world)
            return look.look(player)
        else:
            raise CommandException(CommandException.IMPOSSIBLE_PATH)

