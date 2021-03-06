from player import Player
from lobject import LObject
from area import Area
from event import Event
from image_handler import ImageHandler
from os.path import join
import shutil
import shelve
import os
import logging
import saulscript
import saulscript.syntax_tree

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
        if self.players[name] not in self.players[name].location.players:
            self.players[name].location.players.append(self.players[name])
        self.players[name].signed_in = True
        return self.players[name]

    def remove_player(self, player):
        if player is None:
            return
        if type(player) == str or type(player) == unicode:
            player = self.players[player]
        logging.info("Removing player: %s", player.name)
        player.signed_in = False
        player.location.players.remove(player)

    def init_lobjects(self):
        # this will be an initialization routine for the first objects
        brick = LObject('brick', value=20)
        area = self.areas[self.areas.keys()[0]]
        area.lobjects[brick.id] = brick
        brick.set_parent(area)

    def init_areas(self):
        quarry = Area('Quarry', 'You are in an empty quarry.')
        quarry_pond = Area('Quarry pond',
                           'You are wading in fetid water '
                           'inside of the quarry.')
        quarry.link_to(quarry_pond)
        self.areas[quarry.id] = quarry
        self.areas[quarry_pond.id] = quarry_pond

    def init_content(self):
        self.image_handler.init_content()

    def tick(self):
        # logging.debug("World: tick (%d, %d)", self.sync_counter, self.recharge_counter)
        self.sync_counter += 1
        self.recharge_counter += 1
        if self.sync_counter > self.SYNC_CYCLES_CHECK:
            self.sync_counter = 0
            self.sync()
        if self.recharge_counter > self.RECHARGE_RATE:
            self.recharge_counter = 0
            self.charge_things()
            self.emit_scripting_event('charge', {'charge': True})

    def sync(self):
        logging.info('Syncing...')
        self.datastore['players'] = dict(self.players)
        self.datastore['areas'] = dict(self.areas)
        self.datastore.sync()
        logging.info('Done.')

    def charge_things(self):
        logging.debug('charging up stuff')
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

    def is_area(self, obj_id):
        return obj_id in self.areas

    def find_object(self, obj_id):
        for l in self.areas:
            if obj_id in self.areas[l].lobjects:
                return self.areas[l].lobjects[obj_id]
        for p in self.players:
            if obj_id in self.players[p].inventory:
                return self.players[p].inventory[obj_id]
        return None

    def find_player(self, player_id):
        if p in self.players:
            return self.players[p]

    def tell_owner(self, source, msg):
        logging.debug("tell_owner: Checking source %s", source)
        if hasattr(source, 'id'):
            logging.debug("Source has id attr")
            source = source.id
        for l in self.areas:
            logging.debug("tell_owner: checking area %s", l)
            if source in self.areas[l].lobjects:
                logging.debug("tell_owner: area checks out")
                self.tell(self.areas[l], msg)
        for p in self.players:
            logging.debug("tell_owner: checking player %s", p)
            logging.debug("tell_owner: player %s's inventory: %s",
                          p, repr(self.players[p].inventory))
            if source in self.players[p].inventory:
                self.tell(self.players[p], msg)

    def tell(self, target, msg):
        if isinstance(target, Area):
            logging.debug("tell: target is an Area")
            self.tell_location(target, msg)
        elif isinstance(target, Player):
            if target.signed_in:
                self.tell_player(target, msg)
        else:
            logging.error("Tried to tell a bad thing to an unknown thing: %s",
                          msg)

    def tell_player(self, player, msg):
        if type(player) != Player:
            logging.debug("Ok, player is an index")
            player = self.players[player]
        if type(msg) != list:
            msg = [msg, ]
        self.controller.store_event(player.name, Event('clientcrap',
                                                       {'lines': msg}))

    def tell_location(self, location, msg):
        logging.debug("tell_location: Ok, telling %s '%s'", location, msg)
        logging.debug("tell_location: players in location: %s",
                      repr(location.players))
        for player in location.players:
            logging.debug("tell_location: telling %s", player)
            self.tell_player(player, msg)

    def send_player_location(self, player):
        if type(player) != Player:
            player = self.players[player]
        self.controller.store_event(player.name,
                                    Event('location', {
                                        'area': player.location.to_dict()
                                    }))

    def send_player_location_areas(self, player):
        if type(player) != Player:
            player = self.players[player]
        areas = [area.to_dict() for area in player.location.links_to.values()]
        self.controller.store_event(player.name,
                                    Event('location-areas', {
                                        'areas': areas
                                    }))

    def send_player_inventory(self, player):
        if type(player) != Player:
            player = self.players[player]
        items = [item.to_dict() for item in player.inventory.values()]
        self.controller.store_event(player.name, Event('inventory',
                                                       {'inventory': items}))

    def send_player_location_inventory(self, player):
        if type(player) != Player:
            player = self.players[player]
        items = [item.to_dict() for item in player.location.lobjects.values()]
        self.controller.store_event(player.name, Event('location-inventory',
                                                       {'inventory': items}))

    def send_player_status(self, player):
        if type(player) != Player:
            player = self.players[player]
        player_data = player.to_dict()
        self.controller.store_event(player.name, Event('player-status',
                                                       {'player': player_data}))

    def initialize_context(self, thing, initiator, context):
        context['initiator'] = initiator.to_dict()
        context['object'] = thing.to_dict()

        def _on(name, callback):
            logging.debug("on happening %s %s" % (name, callback))
            self.register_event_handler(thing.id, name, callback)
        context['on'] = _on

        def _owner():
            if hasattr(thing, 'parent'):
                return thing.parent.to_dict()
            else:
                return None
        context['owner'] = _owner

        def _nearby_players():
            owner = _owner()
            if isinstance(owner, Player):
                return owner.location.players
            elif isinstance(owner, Area):
                return owner.players
            else:
                return []
        context['nearby_players'] = _nearby_players

        def _nearby_items():
            owner = _owner()
            if isinstance(owner, Player):
                return owner.location.lobjects
            elif isinstance(owner, Area):
                return owner.lobjects
            else:
                return []
        context['nearby_items'] = _nearby_items

        def _tell(arg):
            arg = '<%s> %s' % (thing.name, arg)
            self.tell(initiator, str(arg))
        context['tell'] = _tell

        return context

    def register_event_handler(self, obj_id, name, callback):
        logging.debug(
            "Received a request to register an event handler for " + name)
        if isinstance(name, saulscript.syntax_tree.nodes.Node):
            name = name.value
        logging.debug("Registering event handler for %s" % name)
        if name not in self.event_handlers:
            logging.debug("Creating new list")
            self.event_handlers[name] = {}
        self.event_handlers[name][obj_id] = callback

    def in_scope(self, scope, obj):
        if type(scope) != list:
            scope = [scope]
        logging.debug("Checking if obj %s is in Scope %s", obj.id, repr(scope))

        def _in_scope(res, _scope):
            if obj.id == _scope.id:
                logging.debug("Object %s is equal to Scope", obj.id)
                return True
            if isinstance(_scope, Area):
                result = res or obj.id in _scope.lobjects
                logging.debug("Obj %s is in Area %s's items",
                              obj.id, _scope.id)
                return result
            elif isinstance(_scope, Player):
                result = res or obj.id in _scope.inventory
                logging.debug("Obj %s is in Player %s's inventory",
                              obj.id, _scope.id)
                return result

        return reduce(_in_scope, scope)

    def emit_scripting_event(self, name, data, scope=None):
        logging.debug("Emitting event %s", name)
        logging.debug("Event handlers: %s", repr(self.event_handlers))
        if name in self.event_handlers:
            logging.debug("Found event handlers for %s", name)
            for obj_id in self.event_handlers[name]:
                obj = self.find_object(obj_id)
                logging.debug("Checking %s" % repr(obj))
                try:
                    if scope is None or self.in_scope(scope, obj):
                        func = self.event_handlers[name][obj_id]
                        logging.debug("Event handler: %s(%s)", func, data)
                        func(data)
                except saulscript.exceptions.SaulException as e:
                    logging.error("Encountered scripting error: %s", e)
                    obj = self.find_object(obj_id)
                    printed_exception = "Scripting error on object %s at line %d: %s" % \
                        (obj.name, e.line_num, e.message)
                    self.tell_owner(obj_id, printed_exception)

    def initialize_script(self, thing, initiator):
        ctx = saulscript.Context()
        self.initialize_context(thing, initiator, ctx)
        ctx.set_op_limit(thing.power *
                         self.SCRIPTING_OPERATION_POWER)
        self.script_contexts[thing.id] = ctx
        try:
            self.script_objects[thing.id] = \
                ctx.execute(thing.script_body,
                            op_limit=self.SCRIPTING_OP_LIMIT,
                            time_limit=self.SCRIPTING_TIME_LIMIT)
        except saulscript.exceptions.OperationLimitReached:
            msg = "%s doesn't have enough energy to perform this action." % \
                thing.name
            self.tell(initiator, msg)
        except saulscript.exceptions.TimeLimitReached:
            msg = "%s took too long to perform this action." % thing.name
            self.tell(initiator, msg)
        thing.power -= ctx.operations_counted / \
            self.SCRIPTING_OPERATION_POWER
        logging.debug("Context: ")
        logging.debug(ctx)
        logging.debug(self.script_objects[thing.id])

    def file_exists(self, obj_id):
        return os.path.exists(join(self.data_location, 'files', obj_id))

    def save_file(self, obj_id, content):
        logging.debug('Saving file')
        files_path = join(self.data_location, 'files')
        if not os.path.exists(files_path):
            os.mkdir(files_path)
        fh = open(join(files_path, obj_id), 'w')
        fh.write(content)
        fh.close()

    def retrieve_file(self, obj_id):
        files_path = join(self.data_location, 'files')
        target = join(files_path, obj_id)
        if not os.path.exists(files_path) or not os.path.exists(target):
            raise KeyError()
        fh = open(target, 'r')
        contents = fh.read()
        fh.close()
        return contents

    def copy_file(self, old_id, new_id):
        src = join(self.data_location, 'files', old_id)
        dst = join(self.data_location, 'files', new_id)
        shutil.copyfile(src, dst)
        return True

    def save_content(self, obj_id, thing):
        if 'content' not in self.datastore:
            self.datastore['content'] = {}
        self.datastore['content'][obj_id] = thing
        self.datastore.sync()

    def retrieve_content(self, obj_id):
        return self.datastore['content'][obj_id]

    def __init__(self, controller, data_location):
        database_path = join(data_location, 'lvlss.db')
        game_exists = os.path.exists(database_path)
        self.datastore = shelve.open(database_path, writeback=True)
        self.sync_counter = 0
        self.recharge_counter = 0
        self.controller = controller
        self.image_handler = ImageHandler(self)
        self.data_location = data_location

        if game_exists:
            logging.debug('Loading existing game.')
            self.players = self.datastore['players']
            for p in self.players:
                logging.debug('setting world for %s' % p)
                self.players[p].set_world(self)
                for index, lobject in self.players[p].inventory.iteritems():
                    lobject.set_parent(self.players[p])

            self.areas = self.datastore['areas']
            for area_index, area in self.areas.iteritems():
                for lname, lobject in area.lobjects.iteritems():
                    lobject.set_parent(area)
        else:
            self.players = {}
            self.areas = {}
            self.init_areas()
            self.init_lobjects()
            self.init_content()
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
