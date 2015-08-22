import socket
import select
import json
from time import sleep
import sys


class LvlssClient:

    how_nice = 0.010

    def __init__(self, host='localhost', port=19820):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.socket.setblocking(0)
        self.running = True

        socket_list = [sys.stdin, self.socket]
         
        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])

        while self.running:

            read_sockets, _, __ = select.select(socket_list, [], [], 0)
            for read_socket in read_sockets:
                # new request

                if read_socket == self.socket:
                    data = self.socket.recv(4096)
                    if not data:
                        print 'Shutting down.'
                        self.running = False
                        break
                    decoded = json.loads(data)
                    print decoded
                    if decoded['event_name'] == 'clientcrap':
                        for line in decoded['lines']:
                            print line
                    else:
                        sys.stdout.write(data + '\n')
                        sys.stdout.flush()
                else:
                    data = read_socket.readline()
                    if data:
                        res = self.socket.send(data)

            sleep(self.how_nice)

        self.server_socket.close()

if __name__ == "__main__":
    client = LvlssClient()
    client.start()
