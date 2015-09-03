import urwid
import socket
import json
import sys

class LvlssParseError(Exception):
    pass


class ExtendedListBox(urwid.ListBox):
    """
        Listbow widget with embeded autoscroll
    """

    __metaclass__ = urwid.MetaSignals
    signals = ["set_auto_scroll"]


    def set_auto_scroll(self, switch):
        if type(switch) != bool:
            return
        self._auto_scroll = switch
        urwid.emit_signal(self, "set_auto_scroll", switch)


    auto_scroll = property(lambda s: s._auto_scroll, set_auto_scroll)


    def __init__(self, body):
        urwid.ListBox.__init__(self, body)
        self.auto_scroll = True


    def switch_body(self, body):
        if self.body:
            urwid.disconnect_signal(body, "modified", self._invalidate)

        self.body = body
        self._invalidate()

        urwid.connect_signal(body, "modified", self._invalidate)


    def keypress(self, size, key):
        urwid.ListBox.keypress(self, size, key)

        if key in ("page up", "page down"):
            if self.get_focus()[1] == len(self.body) - 1:
                self.auto_scroll = True
            else:
                self.auto_scroll = False


    def scroll_to_bottom(self):
        if self.auto_scroll:
            # at bottom -> scroll down
            self.set_focus(len(self.body) - 1)


class LvlssPile(urwid.Pile):

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

    def handle_event(self, event):
        method_name = 'handle_' + event['name']
        if method_name in dir(self):
            method = getattr(self, method_name)
            method(event)
        else:
            self.append("Unhandled event: %s" % event['name'])

    def handle_location(self, event):
        self.append("Your current location: %s" % event['area']['name'])
        self.append(event['area']['description'])

    def handle_location_areas(self, event):
        self.append("Nearby places:")
        for i, area in enumerate(event['areas']):
            self.append("%d: %s" % (i + 1, area['name']))

    def handle_inventory(self, event):
        self.append("Inventory:")
        for i, item in enumerate(event['inventory']):
            self.append("%d: %s" % (i + 1, item['name']))

    def handle_location_inventory(self, event):
        self.append("Items here:")
        for i, item in enumerate(event['inventory']):
            self.append("%d: %s" % (i + 1, item['name']))

    def append(self, text):
        self.lines.append(urwid.Text(text))

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
        self.send_command(command)
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
        if decoded['name'] == 'clientcrap':
            for line in decoded['lines']:
                self.append(line)
        else:
            self.handle_event(decoded)

    def send_command(self, data):
        self.socket.send(json.dumps(data) + "\n")

    def __init__(self, nick, host='127.0.0.1', port=19820):
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
        self.lines = [urwid.Text('Welcome to lvlss.'), ]
        self.master_frame = LvlssPile([('weight', 99, ExtendedListBox(self.lines)), (1, self.editbox)], focus_item=self.editbox)
        self.master_frame.register_enter_db(self.handle_enter)
        self.loop = urwid.MainLoop(self.master_frame,
                                   unhandled_input=self.handle_input_cb,
                                   handle_mouse=False)

        self.loop.watch_file(self.socket, self.read_server_data)
        self.send_command({'command': 'nick', 'args': [nick]})

    def start(self):
        self.loop.run()

if __name__ == "__main__":
    client = LvlssClient(sys.argv[1])
    client.start()
