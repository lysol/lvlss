from world import World
from event import Event
import commands


class ControllerException(Exception):

    UNKNOWN_COMMAND = 0
    COMMAND_NOT_ALLOWED = 1

    messages = {
        0: "Unknown command.",
        1: "You must sign in first."
    }
    
    def __init__(self, value):
        self.value = value
        self.msg = self.messages[value]


class Controller(object):

    def store_event(self, target, event):
        if target not in self.event_backlog:
            self.event_backlog[target] = []
        self.event_backlog[target].append(event)

    def get_event(self, target):
        if target in self.event_backlog and len(self.event_backlog[target]) > 0:
            return self.event_backlog[target].pop()
        else:
            return None  

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
            raise ControllerException(ControllerException.UNKNOWN_COMMAND)
            return

        if 'args' not in data:
            data['args'] = []
        if player is None and not command.unauthenticated:
            raise ControllerException(ControllerException.COMMAND_NOT_ALLOWED)
        event = command.invoke(player, *data['args'])

        return event

    def initialize_commands(self):
        self.commands = {com.shortname: com(self.world) for
                         com in commands.all_commands}

    def check_sync(self):
        self.world.check_sync()

    def remove_player(self, name):
        self.world.remove_player(name)

    def __init__(self, server, datalocation="/tmp/lvlssworld"):
        self.world = World(self, datalocation)
        self.commands = {}
        self.initialize_commands()
        self.server = server
        self.event_backlog = {}