from command import Command, is_command, CommandException
from event import Event
import saulscript


class SetScript(Command):

    @is_command
    def script(self, player, *args):
        if len(args) < 2:
            raise CommandException(CommandException.NOT_ENOUGH_ARGUMENTS)

        thing_id = args[0]
        script_body = args[1]

        if thing_id in player.inventory:
            thing = player.inventory[thing_id]
        elif thing_id in player.location.lobjects:
            thing = player.location.lobjects[thing_id]
        elif thing_id == player.location.id:
            thing = player.location
        else:
            raise CommandException(CommandException.UNKNOWN_ITEM)
        thing.set_script(script_body)
        try:
            self.world.initialize_script(thing, player)
            return Event('script_saved', {
                "thing": thing.to_dict()
                })
        except saulscript.exceptions.SaulException as saulerror:
            return Event('script_error', {
                "error": "Error at line %d: %s" % (saulerror.line_num, saulerror.message)
                })


class GetScript(Command):

    @is_command
    def getscript(self, player, *args):
        if len(args) < 1:
            raise CommandException(CommandException.NOT_ENOUGH_ARGUMENTS)

        thing_id = args[0]

        if thing_id in player.inventory:
            thing = player.inventory[thing_id]
        elif thing_id in player.location.lobjects:
            thing = player.location.lobjects[thing_id]
        elif thing_id == player.location.id:
            thing = player.location
        script_body = thing.script_body
        return Event('script_body', {
            "player_name": args[0],
            "script_body": script_body,
            "thing": thing.to_dict()
        })
