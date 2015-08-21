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

        print data, self.commands

        try:
            command = self.commands[data['command']]
        except KeyError:
            raise ControllerException("No such command")
            return

        print 'command: ', command
        result = command.invoke(player, **data['data'])
        print 'commandResult: ', result
        self.handle_result(player, result)
        return result

    def initialize_commands(self):
        self.commands = {com.shortname: com(self.world) for
                         com in commands.all_commands}

    def __init__(self, world=None):
        if world is None:
            world = World()
        self.world = world
        self.commands = {}
        self.initialize_commands()
