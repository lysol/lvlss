from player import Player
from lobject import LObject
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
        self.areas[0].lobjects.append(LObject('brick', value=20))

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
        self.datastore['players'] = dict(self.players)
        self.datastore['lobjects'] = list(self.lobjects)
        self.datastore['areas'] = list(self.areas)
        self.datastore.sync()
        print 'Done.'

    def stop(self):
        self.sync()
        self.datastore.close()

    def tell_player(self, player, msg):
        if type(player) != Player:
            player = self.players[player]
        if type(msg) != list:
            msg = [msg, ]
        self.controller.store_event(player.name, Event('clientcrap',
                                                       {'lines': msg}))

    def send_player_location(self, player):
        if type(player) != Player:
            player = self.players[player]
        self.controller.store_event(player.name, Event('location', {'area': player.location.to_dict() }))

    def send_player_location_areas(self, player):
        if type(player) != Player:
            player = self.players[player]
        areas = [area.to_dict() for area in player.location.links_to]
        self.controller.store_event(player.name, Event('location_areas', {'areas': areas }))

    def send_player_inventory(self, player):
        if type(player) != Player:
            player = self.players[player]
        items = [item.to_dict() for item in player.inventory]
        self.controller.store_event(player.name, Event('inventory', {'inventory': items }))

    def send_player_location_inventory(self, player):
        if type(player) != Player:
            player = self.players[player]
        items = [item.to_dict() for item in player.location.lobjects]
        self.controller.store_event(player.name, Event('location_inventory', {'inventory': items }))


    def __init__(self, controller, datalocation):
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
            self.areas = []
            self.init_areas()
            self.init_lobjects()
            self.sync()
