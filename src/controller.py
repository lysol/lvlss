from world import World
import commands


class ControllerException(Exception):
    pass


class Controller(object):

    def handle_result(self, player, result):
        pass

    def handle_data(self, player_id, data):
        # this is needed for the set_name command
        if player_id is not None:
            print player_id
            player = self.world.players[player_id]
        else:
            player = None

        try:
            command = self.commands[data['command']]
        except KeyError:
            raise ControllerException("No such command")
            return

        if 'args' not in data:
            data['args'] = []
        result = command.invoke(player, *data['args'])
        self.handle_result(player, result)
        return result

    def initialize_commands(self):
        self.commands = {com.shortname: com(self.world) for
                         com in commands.all_commands}

    def check_sync(self):
        self.world.check_sync()

    def __init__(self, datalocation="/tmp/lvlssworld"):
        self.world = World(datalocation)
        self.commands = {}
        self.initialize_commands()
