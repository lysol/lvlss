from command import Command
from event import Event

class Say(Command):
    
    shortname = 'say'
    name = 'Say something to someone, or in the public chat'

    def invoke(self, player, *args):
        if args[0] in self.world.players:
            prefix = "(private) <%s> " % player.name
            # a message to a user
            msg = prefix + ' '.join(args[1:])
            self.tell_player(args[0], msg)
        else:
            prefix = "<%s> " % player.name
            for p in self.world.players:
            	msg = prefix + ' '.join(args)
                self.tell_player(p, msg)
