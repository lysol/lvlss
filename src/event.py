

class Event(object):

    def __init__(self, name, data={}):
        self.saved_attrs = []
        self.name = name
        for k in data:
            setattr(self, k, data[k])
            self.saved_attrs.append(k)

    def to_dict(self):
        base = {k: getattr(self, k) for k in self.saved_attrs}
        base['name'] = self.name
        return base