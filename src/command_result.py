

class CommandResult(object):

    def __init__(self, event_name, data={}):
        self.event_name = event_name
        for k in data:
            setattr(self, k, data[k])
