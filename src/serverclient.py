from uuid import uuid4
import socket
import json


class LvlssServerClient:

    def handle_lines(self, lines):
        for line in lines:
            print line

    def writelines(self, lines):
        for line in lines:
            self.socket.send(json.dumps({"clientcrap": line}) + "\n")

    def readlines(self):
        while True:
            try:
                buffer = self.socket.recv(4096)
            except socket.error:
                break
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
