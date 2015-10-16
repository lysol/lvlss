from command import Command, is_command
from event import Event

class Say(Command):
    
    shortname = 'say'
    name = 'Say something to someone, or in the public chat'

    @is_command
    def say(self, player, *args):
        if args[0] in self.world.players:
            prefix = "(private) <%s> " % player.name
            # a message to a user
            msg_base = ' '.join(args[1:])
            msg = prefix + ' '.join(args[1:])
            target_player = self.find_player(args[0])
            self.tell_player(args[0], msg)
            self.world.emit_scripting_event('say', {
                'source': player.to_dict(),
                'target': target_player.to_dict(),
                'msg': msg_base
            }, scope=[target_player])
        else:
            prefix = "<%s> " % player.name
            msg_base = ' '.join(args)
            msg = prefix + ' '.join(args)

            for p in self.world.players:
                self.tell_player(p, msg)
            self.world.emit_scripting_event('say', {
                'source': player.to_dict(),
                'target': player.location.to_dict(),
                'msg': msg_base
            }, scope=[player.location, player])