from __future__ import unicode_literals, division

from time import sleep
import sys, socket, json, select
from curtsies import FullscreenWindow, Input, FSArray, fmtstr
from curtsies.fmtfuncs import red, bold, green, on_blue, yellow, on_red, cyan
from curtsies.formatstring import linesplit
import curtsies.events

log = open('/tmp/client.log', 'w')

class Frame(curtsies.events.ScheduledEvent):
    pass

def lreversed(rev):
    return list(rev)

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
        self.scrollback.append(text)

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
        if len(self.command_buffer) == 0:
            return
        data = self.command_buffer
        tokens = self.parse_line(data.strip())
        command = {"command": tokens[0], "args": tokens[1:]}
        self.send_command(command)
        self.command_buffer = ''

    def read_server_data(self):
        data = self.socket.recv(4096)
        if not data:
            print 'Shutting down because we received no data.'
            self.running = False
            self.socket.close()
            exit()
        self.server_buffer += data
        parts = self.server_buffer.split("\n")
        if parts[-1] != '':
            # doesn't terminate in \n
            self.server_buffer = parts[-1]
        else:
            parts.pop()
            self.server_buffer = ''
        for part in parts:
            log.write("Part split: %s\n" % part)
            decoded = json.loads(part)
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
        self.command_buffer = ''
        self.scrollback = []
        self.server_buffer = ''

        self.send_command({'command': 'nick', 'args': [nick]})

    def build_view(self):
        height, width = self.window.get_term_hw()
        fsa = FSArray(height, width)
        command_lines = [green('> ' + self.command_buffer)]
        for i, line in enumerate(command_lines):
            fsa[height - len(command_lines) + i] = line
        scrollback_position_start = height - len(command_lines)
        scrollback_lines = [fmtstr(line) for line in self.scrollback[-scrollback_position_start:]]
        for i, line in enumerate(scrollback_lines[-scrollback_position_start:]):
            log.write(repr(line) + "\n")
            log.write("%d %d / %d %d / %d\n" % (width, height, scrollback_position_start, i, len(line)))
            log.write("offset: %d\n" % (height - scrollback_position_start - i))
            fsa[i] = line
        self.window.render_to_terminal(fsa)

    def start(self):
        self.reactor = Input()
        self.window = FullscreenWindow()

        self.build_view()

        with self.window:
            with self.reactor:
                while self.running:
                    ready_to_read, _, _ = select.select([self.socket, self.reactor], [], [])

                    for r in ready_to_read:
                        if r == self.socket:
                            self.read_server_data()
                        else:
                            e = self.reactor.send(0)
                            if e == u'<ESC>':
                                self.running = False
                                self.socket.close()
                                exit()
                            elif e == u'<Ctrl-j>':
                                self.handle_enter()
                            elif e in (u'<DELETE>', u'<BACKSPACE>') and len(self.command_buffer) > 0:
                                self.command_buffer = self.command_buffer[:-1]
                            elif e == '<SPACE>':
                                self.command_buffer += ' '
                            elif e is not None:
                                self.command_buffer += e
                    self.build_view()
                    sleep(0.01)

if __name__ == "__main__":
    client = LvlssClient(sys.argv[1])
    client.start()