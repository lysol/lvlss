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

    def __init__(self, user_id):
        self.user_id = user_id
        self.authenticated = False

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
        responses = []
        try:
            user_id = user.get_id() if user is not None else None
            event = self.controller.handle_data(user_id, data)
        except CommandException as e:
            logging.error(e.msg)
            event = Event('clientcrap', {"lines": [e.msg]})
            if event is not None:
                responses.append(event)
        return responses

    def subscribe_room(self, room):
        self.rooms.append(room)

    def cancel_room(self, room):
        self.rooms.remove(room)

    def tick(self, sleep_time, tag):
        # logging.debug("Doing CommandHandler tick(). Checking for events")
        for room in self.rooms:
            logging.debug("Checking %s", room)
            event = self.controller.get_event(room)
            if event is not None:
                logging.debug("Emitting event %s to %s", event['event_name'], room)
                emit(event['event_name'], event, room=room)
        # logging.debug("Doing Controller.tick() now")
        self.controller.tick()
        time.sleep(sleep_time)

    def stop(self):
        self.controller.world.stop()


def run_regularly(function, intervals, sleep_time=0.1, round_length=1):
    _, init  = divmod(time.time(), 1)
    gevent.sleep(1 - init)
    while True:
        before = time.time()
        _, offset = divmod(before, round_length)
        for div in intervals:
            function(sleep_time, div)
            after = time.time() - before
            if after < (div * round_length):
                gevent.sleep((div * round_length) - after - (offset / len(intervals)))

def fire_ticker(func):
    gevent.spawn(run_regularly, func, [0.01, 0.01, 1]);

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


def handle_responses(responses):
    for response in responses:
        try:
            print repr(response)
            print dir(response)
            print response.name
            rdict = response.to_dict()
            print rdict
            emit(response.name, rdict)
        except IndexError:
            emit('clientcrap', 'Received malformed command')

@login_manager.user_loader
def load_user(user_id):
    return controller.get_user(user_id)


@app.route('/')
def root():
        return app.send_static_file('index.html')

@socketio.on('login')
def login(data):
    if 'username' in data:
        login_user(User(data['username']))
    join_room(data['username'])
    cmd_data = {"command": 'nick', "args": [data['username']]}
    responses = cmd_handler.handle_event(None, cmd_data)
    handle_responses(responses)
    emit('login-success', {"username": data['username']})

@socketio.on('logout')
@authenticated_only
def logout(data):
    if 'username' in data:
        logout_user(data['username'])
    leave_room(data['username'])

@socketio.on('cmd')
def cmd(data):
    if not current_user.is_authenticated and data['command'] != 'login':
        request.namespace.disconnect()
    responses = cmd_handler.handle_event(current_user, data)
    handle_responses(responses)

if __name__ == '__main__':
    try:
        fire_ticker(cmd_handler.tick)
        socketio.run(app, host='0.0.0.0')
    except KeyboardInterrupt:
        cmd_handler.stop()