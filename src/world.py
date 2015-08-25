from player import Player
from lobject import LObject
from lvalue import LValue
from area import Area
from event import Event
import shelve
import os


class World(object):

    SYNC_CYCLES_CHECK = 2000

    def player_name_exists(self, name):
        return name in self.players and self.players[name].signed_in

    def add_player(self, name):
        if name not in self.players:
            self.players[name] = Player(self, name)
        self.players[name].set_location(self.areas[0])
        self.players[name].signed_in = True

    def remove_player(self, player):
        if player is None:
            return
        if type(player) == str or type(player) == unicode:
            player = self.players[player]
        print "Removing player: ", player.name
        player.signed_in = False

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
        self.datastore.sync()
        print 'Done.'

    def stop(self):
        self.sync()
        self.datastore.close()

    def tell_player(self, player, msg):
        if type(player) != Player:
            player = self.players[player]
        if type(msg) != list:
            msg = [msg,]
        self.controller.store_event(player.name, Event('clientcrap', {'lines': msg}))

    def __init__(self, controller, datalocation):
        print datalocation
        game_exists = os.path.exists(datalocation + '.db')
        self.datastore = shelve.open(datalocation, writeback=True)
        self.sync_counter = 0
        self.controller = controller
        if game_exists:
            print 'Loading existing game.'
            self.players = self.datastore['players']
            for p in self.players:
                print 'setting world for %s' % p
                self.players[p].set_world(self)
            self.lobjects = self.datastore['lobjects']
            self.areas = self.datastore['areas']
        else:
            self.players = {}
            self.lobjects = []
            self.init_lobjects()
            self.areas = []
            self.init_areas()
            self.sync()
