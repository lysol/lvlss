from uuid import uuid4
import socket
import json

class ClientDisconnected(Exception):
    pass

class LvlssServerClient:

    def handle_lines(self, lines):
        for line in lines:
            print line

    def writelines(self, lines):
        self.socket.send(json.dumps({"event_name": "clientcrap", "lines": lines}) + "\n")

    def readlines(self):
        while True:
            try:
                buffer = self.socket.recv(4096)
                if not buffer:
                    raise ClientDisconnected()
            except socket.error as e:
                if e.errno == 35:  # Resource temp. unavailable, done reading for now
                    break
                raise ClientDisconnected()
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
