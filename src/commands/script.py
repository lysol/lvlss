from command import Command, is_command, CommandException
from event import Event
import lupa
import os

class SetScript(Command):

    @is_command
    def setscript(self, player, *args):
        if len(args) < 2:
            raise CommandException(CommandException.NOT_ENOUGH_ARGUMENTS)

        thing_id = args[0]
        script_body_location = args[1]
        if os.path.exists(script_body_location):
            fh = open(script_body_location)
            script_body = fh.read()
        else:
            raise CommandException(CommandException.BAD_SCRIPT_PATH)

        args = list(args)
        args[1] = script_body
        print args
        return self.script(player, *args)

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
        thing.set_script(script_body)
        try:
            self.world.initialize_script(thing)
        except saulscript.exceptions.SaulException as saulerror:
            self.tell_player(player, saulerror.message)

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
        return Event('script_body', {"player_name": args[0], "script_body": script_body, "thing": thing.to_dict()})
