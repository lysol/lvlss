import commands


class CommandException(Exception):

    UNKNOWN_COMMAND = 0
    COMMAND_NOT_ALLOWED = 1
    NOT_ENOUGH_ARGUMENTS = 2
    IMPOSSIBLE_PATH = 3
    NO_ITEM_HERE = 4
    NO_ITEM_IN_INVENTORY = 5
    NEED_A_NUMBER = 6
    BAD_SCRIPT_PATH = 7
    UNKNOWN_ITEM = 8

    messages = {
        0: "Unknown command.",
        1: "You must sign in first.",
        2: "You must provide more arguments to this command.",
        3: "You can't go that way.",
        4: "That item is not here.",
        5: "That item is not in your inventory.",
        6: "The argument at position %d must be a number.",
        7: "No such file.",
        8: "Unknown item."
    }

    def __init__(self, value, interp=None):
        self.value = value
        if interp is None:
            self.msg = self.messages[value]
        else:
            self.msg = self.messages[value] % interp


def is_command(func):
    if callable(func):
        name = func.__name__

        def _invoker(obj, player, *args):
            result = func(obj, player, *args)
            return result
        setattr(_invoker, 'command_name', name)
        return _invoker
    else:
        name = func

        def _invoker2(func2):
            func = func2

            def _invoker(obj, player, *args):
                result = func(obj, player, *args)
                return result
            setattr(_invoker, 'command_name', name)
            return _invoker
        return _invoker2


class Command(object):

    unauthenticated = False

    @property
    def all_commands(self):
        return commands.all_commands

    def tell_player(self, player, msg):
        return self.world.tell_player(player, msg)

    def send_player_location(self, player):
        return self.world.send_player_location(player)

    def send_player_location_areas(self, player):
        return self.world.send_player_location_areas(player)

    def send_player_inventory(self, player):
        return self.world.send_player_inventory(player)

    def send_player_location_inventory(self, player):
        return self.world.send_player_location_inventory(player)

    def __init__(self, world):
        self.world = world

    def _command_methods(self):
        names = filter(lambda m: hasattr(getattr(self, m), 'command_name'),
                       dir(self))
        return [getattr(self, n) for n in names]

    def invoked_by(self, name):
        for func in self._command_methods():
            if func.command_name == name:
                return True
        return False

    def retrieve(self, name):
        for func in self._command_methods():
            if func.command_name == name:
                return func
        return None
