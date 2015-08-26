import urwid
import socket
import json


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

    def append(self, text):
        self.walker.append(urwid.Text(text))

    def parse_line(self, line):
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
            # if we're not quoted, not escaped,
            # and we hit a space, peel off a new blank token
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
        if len(self.editbox.edit_text) == 0:
            return
        data = self.editbox.edit_text
        tokens = self.parse_line(data.strip())
        command = {"command": tokens[0], "args": tokens[1:]}
        command = json.dumps(command) + "\n"
        res = self.socket.send(command)
        self.append("> %s" % self.editbox.edit_text)
        self.editbox.set_edit_text('')

    def handle_input_cb(self, key):
        if key == 'esc':
            raise urwid.ExitMainLoop()

    def read_server_data(self):
        data = self.socket.recv(4096)
        if not data:
            print 'Shutting down because we received no data.'
            self.running = False
            self.socket.close()
            raise urwid.ExitMainLoop()
        decoded = json.loads(data)
        if decoded['event_name'] == 'clientcrap':
            for line in decoded['lines']:
                self.append(line)

    def __init__(self, host='127.0.0.1', port=19820):
        self.host = host
        self.port = port
        self.running = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.socket.setblocking(0)
        self.running = True
        self.area = 'Quarry'

        self.editbox = urwid.Edit(self.area + '> ')
        # urwid.connect_signal(self.editbox, 'change', self.handle_input_cb)

        self.walker = urwid.SimpleFocusListWalker([
            urwid.Text('Welcome to lvlss.')])
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
