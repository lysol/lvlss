from player import Player
from lobject import LObject
from area import Area
from event import Event
import shelve
import os
import logging
import saulscript

class World(object):

    SYNC_CYCLES_CHECK = 2000
    SCRIPTING_OP_LIMIT = 50000
    SCRIPTING_TIME_LIMIT = 3
    SCRIPTING_OPERATION_POWER = 10
    RECHARGE_RATE = 500

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
        logging.debug("Removing player: " + player.name)
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

    def tick(self):
        self.sync_counter += 1
        self.recharge_counter += 1
        if self.sync_counter > self.SYNC_CYCLES_CHECK:
            self.sync_counter = 0
            self.sync()
        if self.recharge_counter > self.RECHARGE_RATE:
            self.recharge_counter = 0
            self.charge_things()
            self.trigger_event('charge', {'charge': True})

    def sync(self):
        print 'Syncing...',
        self.datastore['players'] = dict(self.players)
        self.datastore['areas'] = dict(self.areas)
        self.datastore.sync()
        print 'Done.'

    def charge_things(self):
        print 'charging up stuff'
        for l in self.areas:
            self.areas[l].charge()
            for i in self.areas[l].lobjects:
                self.areas[l].lobjects[i].charge()
        for p in self.players:
            for i in self.players[p].inventory:
                self.players[p].inventory[i].charge()

    def stop(self):
        self.sync()
        self.datastore.close()

    def tell(self, target, msg):
        if isinstance(target, Area):
            self.tell_location(target, msg)
        elif isinstance(target, Player):
            self.tell_player(target, msg)
        else:
            print "Tried to tell a bad thing to an unknown thing: ", msg

    def tell_player(self, player, msg):
        if type(player) != Player:
            player = self.players[player]
        if type(msg) != list:
            msg = [msg, ]
        self.controller.store_event(player.name, Event('clientcrap',
                                                       {'lines': msg}))

    def tell_location(self, location, msg):
        for player in location.players:
            self.tell_player(player, msg)

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

    def initialize_context(self, context):
        def _on(name, callback):
            print "on happening %s %s" % (name, callback)
            self.register_event_handler(name, callback)
        context['on'] = _on
        return context

    def register_event_handler(self, name, callback):
        print "Registering event handler for %s" % name
        if name not in self.event_handlers:
            print "Creating new list"
            self.event_handlers[name] = {} 
        self.event_handlers[name][obj.id] = callback

    def trigger_event(self, name, data):
        print "Triggering events %s" % name
        print self.event_handlers
        if name in self.event_handlers:
            print "name in event handlers"
            for obj_id, callback in self.event_handlers[name].iteritems():
                print "callin"
                callback(data)

    def initialize_script(self, thing, initiator):
        ctx = saulscript.Context()
        self.initialize_context(ctx)
        ctx.set_op_limit(thing.power *
            self.SCRIPTING_OPERATION_POWER)
        self.script_contexts[thing.id] = ctx
        try:
            self.script_objects[thing.id] = \
                    ctx.execute(thing.script_body,
                                op_limit=self.SCRIPTING_OP_LIMIT,
                                time_limit=self.SCRIPTING_TIME_LIMIT)
        except saulscript.exceptions.OperationLimitReached:
            msg = "%s doesn't have enough energy to perform this action." % thing.name
            self.tell(initiator, msg)
        except saulscript.exceptions.TimeLimitReached:
            msg = "%s took too long to perform this action." % thing.name
            self.tell(initiator, msg)
        thing.power -= ctx.operations_counted / \
            self.SCRIPTING_OPERATION_POWER
        print "Context: "
        print ctx
        print self.script_objects[thing.id]

    def __init__(self, controller, datalocation):
        game_exists = os.path.exists(datalocation + '.db')
        self.datastore = shelve.open(datalocation, writeback=True)
        self.sync_counter = 0
        self.recharge_counter = 0
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
        self.scripting = saulscript.Context()
        self.script_contexts = {}
        self.script_objects = {}
        self.event_handlers = {}

        # bootstrap all scripts
        for area in self.areas.values():
            if len(area.script_body) > 0:
                self.initialize_script(area, area)
            for lobject in area.lobjects.values():
                if len(lobject.script_body) > 0:
                    self.initialize_script(lobject, area)
        for player in self.players.values():
            for lobject in player.inventory.values():
                if len(lobject.script_body) > 0:
                    self.initialize_script(lobject, player)
