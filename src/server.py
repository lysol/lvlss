import socket
import select
from serverclient import LvlssServerClient
import json
from controller import Controller, ControllerException
from time import sleep


class LvlssServer:

    how_nice = 0.030

    def __init__(self, host='localhost', port=19820):
        self.host = host
        self.port = port
        self.clients = {}
        self.socket_list = []
        self.socket_files = {}
        self.server_socket = None
        self.running = False
        self.controller = Controller()

    def handle_command_result(self, client, result):
        if result.event_name == 'quit':
            sindex = self.socket_list.index(client.socket)
            self.socket_list[sindex].close()
            del(self.clients[self.socket_list[sindex]])
            del(self.socket_list[sindex])
        elif result.event_name == 'clientcrap':
            client.writelines(result.lines)
        elif result.event_name == 'name_set':
            client.player_id = result.player_name

    def handle_line(self, client, line):
        # each line is a json payload
        try:
            data = json.loads(line)
            # this is bubbled up if need be
            try:
                result = self.controller.handle_data(client.player_id, data)
            except ControllerException:
                print "Invalid command"
                return
            self.handle_command_result(client, result)
            # handle result events here later
        except ValueError:
            print "Malformed payload from client ignored."

    def handle_lines(self, client, lines):
        return [self.handle_line(client, line) for line in lines]

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET,
                                      socket.SO_REUSEADDR, 1)
        self.server_socket.setblocking(0)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(10)
        self.socket_list.append(self.server_socket)
        self.running = True

        while self.running:
            read_sockets, _, __ = select.select(self.socket_list, [], [], 0)
            for read_socket in read_sockets:
                # new request
                if read_socket == self.server_socket:
                    sockfd, addr = self.server_socket.accept()
                    sockfd.setblocking(0)
                    self.socket_list.append(sockfd)
                    self.clients[sockfd] = LvlssServerClient(sockfd, *addr)
                    print "Connection from (%s, %s)" % addr
                else:
                    # client data
                    client = self.clients[read_socket]
                    self.handle_lines(client, client.readlines())
            self.controller.check_sync()
            sleep(self.how_nice)

        self.server_socket.close()

if __name__ == "__main__":
    server = LvlssServer()
    server.start()
