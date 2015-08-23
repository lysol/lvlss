

class Area(object):

    def __getstate__(self):
        return {"name": self.name, "description": self.description, "links_to": self.links_to, "lobjects": self.lobjects}

    def link_to(self, area, one_way=False):
        self.links_to.append(area)
        if not one_way:
            area.links_to.append(self)

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.links_to = []
        self.lobjects = []
