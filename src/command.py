import commands


class CommandException(Exception):

    UNKNOWN_COMMAND = 0
    COMMAND_NOT_ALLOWED = 1
    NOT_ENOUGH_ARGUMENTS = 2
    IMPOSSIBLE_PATH = 3

    messages = {
        0: "Unknown command.",
        1: "You must sign in first.",
        2: "You must provide more arguments to this command.",
        3: "You can't go that way."
    }
    
    def __init__(self, value):
        self.value = value
        self.msg = self.messages[value]
        

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

    def __init__(self, world):
        self.world = world

    def _command_methods(self):
        names = filter(lambda m: hasattr(getattr(self, m), 'command_name'), dir(self))
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