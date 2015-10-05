from flask import Flask, request
from flask.ext.login import current_user, login_user, logout_user, LoginManager
from flask.ext.socketio import SocketIO, emit, send, join_room, leave_room
from event import Event
from serverclient import LvlssServerClient, ClientDisconnected
import json
from controller import Controller
from command import CommandException
import logging
import functools
import gevent
import time


class User(object):

    def __init__(self, user_id, player=None):
        self.user_id = user_id
        self.authenticated = False
        self.player = player

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.user_id


class CommandHandler(object):

    def __init__(self, app):
        self.rooms = []
        self.controller = Controller(self)
        self.app = app

    def handle_event(self, user, data):
        try:
            user_id = user.get_id() if user is not None else None
            logging.debug("Handling event %s for user %s", repr(data), str(user_id))
            event = self.controller.handle_data(user_id, data)
        except CommandException as e:
            logging.error(e.msg)
            event = Event('clientcrap', {"lines": [e.msg]})
        return event

    def subscribe_room(self, room):
        self.rooms.append(room)

    def cancel_room(self, room):
        if room in self.rooms:
            self.rooms.remove(room)

    def tick(self):
        # logging.debug("Doing CommandHandler tick(). Checking for events")
        for room in self.rooms:
            # logging.debug("Checking %s", room)
            event = self.controller.get_event(room)
            if event is not None:
                logging.debug("Emitting event %s to %s", event.name, room)
                socketio.emit(event.name, event.to_dict(), room=room)
        # logging.debug("Doing Controller.tick() now")
        self.controller.tick()


    def get_user(self, username):
        return self.controller.get_user(username)

    def stop(self):
        self.controller.world.stop()


def run_regularly(function, delay=0.25):
    while True:
        function()
        gevent.sleep(delay)

def fire_ticker(func):
    gevent.spawn(run_regularly, func);

def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated():
            request.namespace.disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

# set that shit _up_
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'dlkgjfdlkgfgkdjfglkfjglkdjfglk23423423#@###'
socketio = SocketIO(app)
cmd_handler = CommandHandler(app)
login_manager = LoginManager()
login_manager.init_app(app)


def handle_response(response):
    if response is None:
        logging.debug("Handling None")
        return
    try:
        rdict = response.to_dict()
        emit(response.name, rdict)
    except IndexError:
        emit('clientcrap', 'Received malformed command')


@login_manager.user_loader
def load_user(user_id):
    player = cmd_handler.get_user(user_id)
    return User(user_id, player=player)


@app.route('/')
def root():
        return app.send_static_file('index.html')


@socketio.on('login')
def login(data):
    if 'username' in data:
        login_user(User(data['username']))
    join_room(data['username'])
    cmd_data = {"command": 'nick', "args": [data['username']]}
    response_event = cmd_handler.handle_event(None, cmd_data)
    logging.debug(response_event)
    if response_event is not None and response_event.name == 'name_set':
        handle_response(response_event)
        emit('login-success', {"username": data['username']})
        cmd_handler.subscribe_room(data['username'])
    else:
        emit('login-failure', {"username": data['username']})


@socketio.on('logout')
@authenticated_only
def logout(data):
    if 'username' in data:
        logout_user(data['username'])
        cmd_handler.cancel_room(data['username'])
    leave_room(data['username'])


@socketio.on('cmd')
def cmd(data):
    if not current_user.is_authenticated:
        request.namespace.disconnect()
    response_event = cmd_handler.handle_event(current_user, data)
    handle_response(response_event)


if __name__ == '__main__':
    try:
        fire_ticker(cmd_handler.tick)
        socketio.run(app, host='0.0.0.0')
    except KeyboardInterrupt:
        cmd_handler.stop()