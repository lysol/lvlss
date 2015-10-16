from command import Command, is_command, CommandException
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
            old_location = player.location
            old_location.players.remove(player)
            player.location = old_location.links_to[area_id]
            player.location.players.append(player)
            self.world.emit_scripting_event('depart', {
                'area': old_location.to_dict(),
                'player': player.to_dict()
            }, scope=[old_location])
            self.world.emit_scripting_event('arrive', {
                'area': player.location.to_dict(),
                'player': player.to_dict()
            }, scope=[player.location])
            # hacky thing....maybe needs a better interface
            look = Look(self.world)
            return look.look(player)
        else:
            raise CommandException(CommandException.IMPOSSIBLE_PATH)
