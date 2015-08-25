import socket
import select
import json
from time import sleep
import sys

class LvlssParseError(Exception):
    pass

class LvlssClient:

    how_nice = 0.030

    def __init__(self, host='localhost', port=19820):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False

    def parse_line(self, line):
        pos = 0
        escaped = False
        in_quotes = False
        tokens = ['']

        for x in line:
            # If we hit a \ and we didn't already escape the last round (\\)
            if x == '\\' and not escaped:
                escaped = True
                continue
            # If we hit a quote and it's not escaped \"
            elif x == '"' and not escaped:
                in_quotes = not in_quotes
            # if we're not quoted, not escaped, and we hit a space, peel off a new blank token
            elif not in_quotes and not escaped and x == ' ':
                tokens.append('')
            # otherwise, append the character to the current token
            else:
                tokens[-1] += x
            escaped = False
        if in_quotes:
            raise LvlssParseError("Unterminated quote")
        return tokens

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
                    if decoded['event_name'] == 'clientcrap':
                        for line in decoded['lines']:
                            print line
                    else:
                        sys.stdout.write(data + '\n')
                        sys.stdout.flush()
                else:
                    data = read_socket.readline()
                    tokens = self.parse_line(data.strip())
                    command = {"command": tokens[0], "args": tokens[1:]}
                    command = json.dumps(command) + "\n"

                    if data:
                        res = self.socket.send(command)

            sleep(self.how_nice)

        self.socket.close()

if __name__ == "__main__":
    client = LvlssClient()
    client.start()
