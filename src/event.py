

class Event(object):

    def __init__(self, name, data={}):
        self.name = name
        for k in data:
            setattr(self, k, data[k])
