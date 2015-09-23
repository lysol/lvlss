from world import World
from event import Event
import commands
from command import CommandException

class Controller(object):

    def store_event(self, target, event):
        if target not in self.event_backlog:
            self.event_backlog[target] = []
        self.event_backlog[target].append(event)
        print self.event_backlog

    def get_event(self, target):
        if target in self.event_backlog and len(self.event_backlog[target]) > 0:
            return self.event_backlog[target].pop(0)
        else:
            return None  

    def handle_data(self, player_id, data):
        # this is needed for the set_name command
        if player_id is not None:
            player = self.world.players[player_id]
        else:
            player = None

        if 'command' not in data:
            raise CommandException(CommandException.UNKNOWN_COMMAND)

        for command in self.commands:
            if command.invoked_by(data['command']):
                if 'args' not in data:
                    data['args'] = []
                if player is None and not command.unauthenticated:
                    raise CommandException(CommandException.COMMAND_NOT_ALLOWED)
                func = command.retrieve(data['command'])
                event = func(player, *data['args'])
                return event
        raise CommandException(CommandException.UNKNOWN_COMMAND)


    def initialize_commands(self):
        self.commands = [com(self.world) for
                         com in commands.all_commands]

    def tick(self):
        self.world.tick()

    def remove_player(self, name):
        self.world.remove_player(name)

    def __init__(self, server, datalocation="/tmp/lvlssworld"):
        self.world = World(self, datalocation)
        self.commands = []
        self.initialize_commands()
        self.server = server
        self.event_backlog = {}