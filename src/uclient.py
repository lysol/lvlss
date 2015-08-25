import urwid
import socket
import select
import json
from time import sleep
import sys

# class LogListWalker(urwid.ListWalker):

#     def __init__(self):
#         self.lines = []
#         self.focus = 0

#     def read_next_line(self):
#         next_line = self.file.readline()

#         if not next_line or next_line[-1:] != '\n':
#             # no newline on last line of file
#             self.file = None
#         else:
#             # trim newline characters
#             next_line = next_line[:-1]

#         expanded = next_line.expandtabs()

#         edit = urwid.Edit("", expanded, allow_tab=True)
#         edit.set_edit_pos(0)
#         edit.original_text = next_line
#         self.lines.append(edit)

#         return next_line

class LvlssParseError(Exception):
    pass


class LvlssFrame(urwid.Frame):

    entercb = []

    def keypress(self, size, key):
        key = super(LvlssFrame, self).keypress(size, key)
        if key == 'enter':
            for cb in self.entercb:
                cb()
        if key == 'esc':
            raise urwid.ExitMainLoop()

    def register_enter_db(self, cb):
        self.entercb.append(cb)



class LvlssClient(object):

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

    def handle_enter(self):
        data = self.editbox.edit_text
        tokens = self.parse_line(data.strip())
        command = {"command": tokens[0], "args": tokens[1:]}
        command = json.dumps(command) + "\n"

        if data:
            res = self.socket.send(command)
        self.editbox.set_edit_text('')


    def handle_input_cb(self, newtext):
        footer = self.master_frame.contents['footer'][0]
        if key == 'esc':
            raise urwid.ExitMainLoop()
        # elif key == 'enter':
        #     # send shit
        #     data = footer.text
        #     tokens = self.parse_line(data.strip())
        #     command = {"command": tokens[0], "args": tokens[1:]}
        #     command = json.dumps(command) + "\n"

        #     if data:
        #         res = self.socket.send(command)
        #     footer.set_text('')
        # else:
        #     footer.set_text(footer.text + key)

    def read_server_data(self):
        body = self.master_frame.contents['body'][0]
        data = self.socket.recv(4096)
        if not data:
            print 'Shutting down.'
            self.running = False
            self.server_socket.close()
            raise urwid.ExitMainLoop()
        decoded = json.loads(data)
        if decoded['event_name'] == 'clientcrap':
            for line in decoded['lines']:
                pos = body.focus_position
                self.walker.insert(pos + 1, urwid.Text(line))


    def __init__(self, host='localhost', port=19820):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.socket.setblocking(0)
        self.running = True
        self.area = 'Quarry'

        self.editbox = urwid.Edit(self.area + '> ')
        # urwid.connect_signal(self.editbox, 'change', self.handle_input_cb)

        self.walker = urwid.SimpleFocusListWalker([urwid.Text('Welcome to lvlss.')])
        self.master_frame = LvlssFrame(body=urwid.ListBox(self.walker),
                                        header=None,
                                        footer=self.editbox,
                                        focus_part='footer')
        self.master_frame.register_enter_db(self.handle_enter)
        self.loop = urwid.MainLoop(self.master_frame,
                                   unhandled_input=self.handle_input_cb,
                                   handle_mouse=False)

        self.loop.watch_file(self.socket, self.read_server_data)

    def start(self):
        self.loop.run()

if __name__ == "__main__":
    client = LvlssClient()
    client.start()
