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
            self.world.controller.store_event(args[0], Event('clientcrap', {'lines': [msg,]}))
        else:
            prefix = "<%s> " % player.name
            for p in self.world.players:
            	msg = prefix + ' '.join(args)
                self.world.controller.store_event(p, Event('clientcrap', {'lines': [msg,]}))
