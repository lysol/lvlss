from player import Player


class World(object):

    def player_name_exists(self, name):
        return name in self.players

    def add_player(self, name):
        self.players[name] = Player(name)

    def remove_player(self, player):
        del(self.players[player.name])

    def __init__(self):
        self.players = {}
