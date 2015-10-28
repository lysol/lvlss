from flask import Flask, request, send_from_directory, session, make_response, abort
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
from datetime import datetime
from uuid import uuid4


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


class LvlssMiddleware(object):

    def __init__(self, app):
        self.rooms = []
        self.controller = Controller(self)
        self.app = app
        self.sessions = {}

    def handle_event(self, user, data):
        try:
            user_id = user.get_id() if user is not None else None
            logging.debug("Handling event %s for user %s", repr(data), str(user_id))
            event = self.controller.handle_data(user_id, data)
        except CommandException as e:
            logging.error(e.msg)
            event = Event('clientcrap', {"lines": [e.msg]})
        return event

    def _subscribe_room(self, room):
        self.rooms.append(room)

    def _cancel_room(self, room):
        if room in self.rooms:
            self.rooms.remove(room)

    def tick(self):
        # logging.debug("Doing LvlssMiddleware tick(). Checking for events")
        for room in self.rooms:
            # logging.debug("Checking %s", room)
            while True:
                event = self.controller.get_event(room)
                if event is None:
                    break
                logging.debug("Emitting event %s to %s", event.name, room)
                socketio.emit(event.name, event.to_dict(), room=room, namespace='/lvlss')

        # logging.debug("Doing Controller.tick() now")
        self.controller.tick()


    def get_user(self, username):
        return self.controller.get_user(username)

    def stop(self):
        self.controller.world.stop()

    def register_user_session(self, session_id, user_id):
        self.sessions[session_id] = user_id
        self._subscribe_room(user_id)
        join_room(user_id)

    def remove_user_session(self, session_id):
        logging.debug("Removing session " + str(session_id))
        try:
            user_id = self.sessions[session_id]
            self._cancel_room(user_id)
            leave_room(user_id)
            logout_user()
            self.controller.remove_player(user_id)
            del(self.sessions[session_id])
        except KeyError:
            logging.debug("Couldn't find user ID for session " + str(session_id))

    def retrieve_content(self, obj_id):
        return self.controller.world.retrieve_content(obj_id)



def run_regularly(function, delay=0.25):
    while True:
        function()
        gevent.sleep(delay)


def fire_ticker(func):
    gevent.spawn(run_regularly, func)


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated():
            request.namespace.disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


def nocache(f):
    @functools.wraps(f)
    def no_cache(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = \
            'no-store, no-cache, must-revalidate, ' + \
            'post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return functools.update_wrapper(no_cache, f)

# set that shit _up_
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'dlkgjfdlkgfgkdjfglkfjglkdjfglk23423423#@###'
socketio = SocketIO(app)
cmd_handler = LvlssMiddleware(app)
login_manager = LoginManager()
login_manager.init_app(app)


def handle_response(response):
    if response is None:
        logging.debug("Handling None")
        return
    try:
        logging.debug("Handling response")
        rdict = response.to_dict()
        emit(response.name, rdict, namespace='/lvlss')
    except IndexError:
        emit('clientcrap', 'Received malformed command', namespace='/lvlss')


@login_manager.user_loader
def load_user(user_id):
    player = cmd_handler.get_user(user_id)
    return User(user_id, player=player)


@app.route('/')
def root():
        return app.send_static_file('index.html')


@socketio.on('login', namespace='/lvlss')
def login(data):
    if 'username' in data:
        login_user(User(data['username']))
    cmd_data = {"command": 'nick', "args": [data['username']]}
    response_event = cmd_handler.handle_event(None, cmd_data)
    logging.debug(response_event)
    if response_event is not None and response_event.name == 'name-set':
        handle_response(response_event)
        emit('login-success', {"username": data['username']}, namespace='/lvlss')
        cmd_handler.register_user_session(session['id'], data['username'])
    else:
        emit('login-failure', {"username": data['username']}, namespace='/lvlss')


@socketio.on('logout', namespace='/lvlss')
@authenticated_only
def logout(data):
    cmd_handler.remove_user_session(session['id'])


@socketio.on('connect', namespace='/lvlss')
def connect():
    session['id'] = str(uuid4())
    logging.debug("New session: " + str(session['id']))


@socketio.on('disconnect', namespace='/lvlss')
def disconnect():
    cmd_handler.remove_user_session(session['id'])


@socketio.on('cmd', namespace='/lvlss')
def cmd(data):
    if not current_user.is_authenticated:
        request.namespace.disconnect()
    response_event = cmd_handler.handle_event(current_user, data)
    handle_response(response_event)


@app.route('/get-img/<img_id>')
def get_img(img_id):
    try:
        img = cmd_handler.retrieve_content(img_id)
        logging.debug("retrieved image")
    except KeyError:
        logging.debug("sending default image")
        img = cmd_handler.retrieve_content('default')
    response = make_response(img)
    response.headers['Content-Type'] = 'image/png'
    return response


@app.route("/<path:path>")
@nocache
def catchall(path):
    return send_from_directory(app.static_folder, path)


if __name__ == '__main__':
    try:
        fire_ticker(cmd_handler.tick)
        socketio.run(app, host='0.0.0.0')
    except KeyboardInterrupt:
        cmd_handler.stop()
