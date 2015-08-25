from uuid import uuid4
import socket
import json


class ClientDisconnected(Exception):

    def __init__(self, underlying=None):
        self.underlying = underlying


class LvlssServerClient:

    def handle_lines(self, lines):
        for line in lines:
            print line

    def writelines(self, lines):
        print lines
        data = {"event_name": "clientcrap", "lines": lines}
        self.socket.send(json.dumps(data) + "\n")

    def readlines(self):
        while True:
            try:
                buffer = self.socket.recv(4096)
                print "Buffer: %s" % buffer
                if not buffer:
                    raise ClientDisconnected()
            except socket.error as e:
                # resource temporarily unavailable
                if e.errno in (35, 11):
                    break
                print e.msg
                raise ClientDisconnected(e)
            self.buffer += buffer
        buf = self.buffer.split("\n")
        if self.buffer[-1] != "\n":
            self.buffer = buf[-1]
        else:
            self.buffer = ''
        return buf[:-1]

    def __init__(self, socket, host, port):
        self.socket = socket
        self.host = host
        self.port = port
        self.buffer = ''
        self.id = uuid4()
        self.player_id = None
        self.authenticated = False
