import logging
from world import World
import commands
from command import CommandException


class Controller(object):

    def get_user(self, username):
        return self.world.players[username] if username in self.world.players else None 

    def store_event(self, target, event):
        if target not in self.event_backlog:
            self.event_backlog[target] = []
        self.event_backlog[target].append(event)
        for event in self.event_backlog:
            logging.debug("Event backlog: %s", repr(event))

    def get_event(self, target):
        # logging.debug("Getting an event for %s", target)
        if target in self.event_backlog and \
                len(self.event_backlog[target]) > 0:
            logging.debug("Sending event to %s", target)
            return self.event_backlog[target].pop(0)
        else:
            # logging.debug("None found.")
            return None

    def handle_data(self, player_id, data):
        logging.debug("Controller: Handle data: %s, %s", player_id, repr(data))
        # this is needed for the set_name command
        if player_id is not None:
            player = self.world.players[player_id]
        else:
            player = None

        if 'command' not in data:
            logging.error("Malformed command: %s", repr(data))
            raise CommandException(CommandException.UNKNOWN_COMMAND)

        for command in self.commands:
            if command.invoked_by(data['command']):
                if 'args' not in data:
                    data['args'] = []
                if player is None and not command.unauthenticated:
                    raise CommandException(
                        CommandException.COMMAND_NOT_ALLOWED)
                func = command.retrieve(data['command'])
                event = func(player, *data['args'])
                return event
        logging.info("Received invalid command: %s", data['command'])
        raise CommandException(CommandException.UNKNOWN_COMMAND)

    def initialize_commands(self):
        self.commands = [com(self.world) for
                         com in commands.all_commands]

    def tick(self):
        # logging.debug("Controller: tick")
        self.world.tick()

    def remove_player(self, name):
        self.world.remove_player(name)

    def __init__(self, server, datalocation=None):
        if datalocation is None:
            from os.path import join, expanduser
            datalocation = join(expanduser('~'), '.lvlss')
        self.world = World(self, datalocation)
        self.commands = []
        self.initialize_commands()
        self.server = server
        self.event_backlog = {}
