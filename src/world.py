from player import Player
from lobject import LObject
from lvalue import LValue
from area import Area
import shelve
import os


class World(object):

    SYNC_CYCLES_CHECK = 2000

    def player_name_exists(self, name):
        return name in self.players

    def add_player(self, name):
        self.players[name] = Player(name)

    def remove_player(self, player):
        del(self.players[player.name])

    def init_lobjects(self):
        # this will be an initialization routine for the first objects
        self.lobjects = []
        self.lobjects.append(LObject('brick', 20))

    def init_areas(self):
        self.areas.append(Area('Quarry', 'You are in an empty quarry.'))
        self.areas.append(Area('Quarry pond',
                               'You are wading in fetid water '
                               'inside of the quarry.'))
        self.areas[0].link_to(self.areas[1])

    def check_sync(self):
        self.sync_counter += 1
        if self.sync_counter > self.SYNC_CYCLES_CHECK:
            self.sync_counter = 0
            self.sync()

    def sync(self):
        print 'Syncing...',
        self.datastore['players'] = self.players
        self.datastore['lobjects'] = self.lobjects
        self.datastore['areas'] = self.areas
        print 'Done.'

    def __init__(self, datalocation):
        game_exists = os.path.exists(datalocation)
        self.datastore = shelve.open(datalocation)
        self.sync_counter = 0
        if game_exists:
            self.players = self.datastore['players']
            self.lobjects = self.datastore['lobjects']
            self.areas = self.datastore['areas']
        else:
            self.players = {}
            self.lobjects = []
            self.init_lobjects()
            self.areas = []
            self.init_areas()
            self.sync()
