from player import Player
from lobject import LObject
from area import Area
from event import Event
import shelve
import os
import lupa
from lupa import LuaRuntime


class World(object):

    SYNC_CYCLES_CHECK = 2000

    def player_name_exists(self, name):
        return name in self.players and self.players[name].signed_in

    def add_player(self, name):
        if name not in self.players:
            self.players[name] = Player(self, name)
        self.players[name].set_location(self.areas[self.areas.keys()[0]])
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
        brick = LObject('brick', value=20)
        self.areas[self.areas.keys()[0]].lobjects[brick.id] = brick

    def init_areas(self):
        quarry = Area('Quarry', 'You are in an empty quarry.')
        quarry_pond = Area('Quarry pond',
                           'You are wading in fetid water '
                           'inside of the quarry.')
        quarry.link_to(quarry_pond)
        self.areas[quarry.id] = quarry
        self.areas[quarry_pond.id] = quarry_pond

    def check_sync(self):
        self.sync_counter += 1
        if self.sync_counter > self.SYNC_CYCLES_CHECK:
            self.sync_counter = 0
            self.sync()

    def sync(self):
        print 'Syncing...',
        self.datastore['players'] = dict(self.players)
        self.datastore['areas'] = dict(self.areas)
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
        self.controller.store_event(player.name, Event('location',
                                                       {'area': player.location.to_dict() }))

    def send_player_location_areas(self, player):
        if type(player) != Player:
            player = self.players[player]
        areas = [area.to_dict() for area in player.location.links_to.values()]
        self.controller.store_event(player.name,
                                    Event('location_areas',
                                    {'areas': areas }))

    def send_player_inventory(self, player):
        if type(player) != Player:
            player = self.players[player]
        items = [item.to_dict() for item in player.inventory.values()]
        self.controller.store_event(player.name, Event('inventory',
                                                       {'inventory': items }))

    def send_player_location_inventory(self, player):
        if type(player) != Player:
            player = self.players[player]
        items = [item.to_dict() for item in player.location.lobjects.values()]
        self.controller.store_event(player.name, Event('location_inventory',
                                                       {'inventory': items }))

    def initialize_script(self, thing):
        ctx = LuaRuntime(unpack_returned_tuples=True)
        self.script_contexts[thing.id] = ctx
        ctx.execute(thing.script_body)

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
            self.areas = self.datastore['areas']
        else:
            self.players = {}
            self.areas = {}
            self.init_areas()
            self.init_lobjects()
            self.sync()
        self.scripting = LuaRuntime(unpack_returned_tuples=True)
        self.script_contexts = {}

        # bootstrap all scripts
        for area in self.areas.values():
            if len(area.script_body) > 0:
                self.initialize_script(area)
            for lobject in area.lobjects.values():
                if len(lobject.script_body) > 0:
                    self.initialize_script(lobject)
        for player in self.players.values():
            for lobject in player.inventory.values():
                if len(lobject.script_body) > 0:
                    self.initialize_script(lobject)
