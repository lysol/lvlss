from __future__ import unicode_literals, division

from time import sleep
import os
import sys
import socket
import json
import select
from curtsies import FullscreenWindow, Input, FSArray, fmtstr
from curtsies.events import PasteEvent
from curtsies.fmtfuncs import red, bold, green, blue, on_blue, yellow, on_red, cyan, on_green
import curtsies.events

log = open('/tmp/client.log', 'w')


class Frame(curtsies.events.ScheduledEvent):
    pass


def lreversed(rev):
    return list(rev)


class LvlssParseError(Exception):
    pass


class LvlssClient(object):

    def _preprocess_command(self, data):
        try:
            if data['command'] in ('take', 'get'):
                target_index = int(data['args'][0]) - 1
                try:
                    item_id = self.local_items[target_index]['id']
                    data['args'][0] = item_id
                except IndexError:
                    return data
            if data['command'] == 'go':
                target_index = int(data['args'][0]) - 1
                try:
                    area_id = self.local_areas[target_index]['id']
                    data['args'][0] = area_id
                except IndexError:
                    return data
            if data['command'] in ('drop', 'script', 'getscript', 'setscript'):
                target_index = int(data['args'][0]) - 1
                try:
                    item_id = self.inventory_items[target_index]['id']
                    data['args'][0] = item_id
                except IndexError:
                    return data
            if data['command'] == 'setscript':
                data['command'] = 'script'
                if len(data['args']) > 1:
                    try:
                        script_path = os.path.realpath(
                            os.path.expanduser(data['args'][1])
                        )
                        script_body = open(script_path, 'r').read()
                        data['args'][1] = script_body
                    except IOError:
                        self.append("Couldn't read file: %s" % script_path)
        except ValueError:
            pass
        return data

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
        del self.local_areas[:]
        self.append("Nearby places:")
        for i, area in enumerate(event['areas']):
            self.append("%d: %s" % (i + 1, area['name']))
            self.local_areas.append(area)

    def handle_inventory(self, event):
        del self.inventory_items[:]
        self.append("Inventory:")
        for i, item in enumerate(event['inventory']):
            self.append("%d: %s" % (i + 1, item['name']))
            self.inventory_items.append(item)

    def handle_location_inventory(self, event):
        del self.local_items[:]
        self.append("Items here:")
        for i, item in enumerate(event['inventory']):
            self.append("%d: %s" % (i + 1, item['name']))
            self.local_items.append(item)

    def handle_script_body(self, event):
        self.append("Script for %s:" % event['thing']['name'])
        for line in event['script_body'].split("\n"):
            self.append(event['script_body'])

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
        self.command_log.append(data)
        self.command_log_cursor = len(self.command_log)
        tokens = self.parse_line(data.strip())
        command = {"command": tokens[0], "args": tokens[1:]}
        self.send_command(command)
        self.command_buffer = ''
        self.command_buffer_cursor = 0

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
            decoded = json.loads(part)
            if decoded['name'] == 'clientcrap':
                for line in decoded['lines']:
                    self.append(line)
            else:
                self.handle_event(decoded)

    def send_command(self, data):
        data = self._preprocess_command(data)
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
        self.backup_command_buffer = ''
        self.scrollback = []
        self.server_buffer = ''

        self.local_items = []
        self.inventory_items = []
        self.local_areas = []
        self.command_log = []
        self.command_log_cursor = 0
        self.command_buffer_cursor = 0

        self.send_command({'command': 'nick', 'args': [nick]})

    def build_command_buffer(self, buffer):
        prepend = '> '
        inverse_pos = len(prepend) + self.command_buffer_cursor
        full_buffer = prepend + self.command_buffer + ' '
        before = green(full_buffer[:self.command_buffer_cursor + 2])
        during = blue(on_green(full_buffer[self.command_buffer_cursor + 2]))
        after = green(full_buffer[self.command_buffer_cursor + 3:])
        return before + during + after

    def build_view(self):
        height, width = self.window.get_term_hw()
        fsa = FSArray(height, width)
        command_lines = [self.build_command_buffer(self.command_buffer)]
        for i, line in enumerate(command_lines):
            fsa[height - len(command_lines) + i] = line
        scrollback_position_start = height - len(command_lines)
        scrollback_lines = []
        for line in self.scrollback:
            if len(line) > width:
                while len(line) > 0:
                    scrollback_lines.append(line[:width])
                    line = line[width:]
            else:
                scrollback_lines.append(line)
        scrollback_lines = [fmtstr(l) for l in
                            scrollback_lines[-scrollback_position_start:]]
        for i, line in enumerate(scrollback_lines):
            fsa[i] = line
        self.window.render_to_terminal(fsa)

    def set_command_log_buffer(self):
        if self.command_log_cursor < len(self.command_log):
            self.command_buffer = self.command_log[self.command_log_cursor]
        else:
            self.command_buffer = self.backup_command_buffer
        self.command_buffer_cursor = len(self.command_buffer)

    def handle_keypress(self, e):
        if e == u'<ESC>':
            self.running = False
            self.socket.close()
            exit()
        elif e == u'<Ctrl-j>':
            self.handle_enter()
        elif e in (u'<DELETE>', u'<BACKSPACE>'):
            if self.command_buffer_cursor > 0:
                after = self.command_buffer[self.command_buffer_cursor:]
                before = self.command_buffer[:self.command_buffer_cursor - 1]
                self.command_buffer = before + after
                self.command_buffer_cursor -= 1
                if self.command_buffer_cursor < 0:
                    self.command_buffer_cursor = 0
        elif e == '<DOWN>':
            self.command_log_cursor += 1
            if self.command_log_cursor > len(self.command_log):
                self.command_log_cursor = len(self.command_log)
            self.set_command_log_buffer()
        elif e == '<UP>':
            if self.command_log_cursor == len(self.command_log):
                self.backup_command_buffer = self.command_buffer
            self.command_log_cursor -= 1
            if self.command_log_cursor < 0:
                self.command_log_cursor = 0
            self.set_command_log_buffer()
        elif e == '<LEFT>':
            self.command_buffer_cursor -= 1
            if self.command_buffer_cursor < 0:
                self.command_buffer_cursor = 0
        elif e == '<RIGHT>':
            self.command_buffer_cursor += 1
            if self.command_buffer_cursor > len(self.command_buffer):
                self.command_buffer_cursor = len(self.command_buffer)
        elif e is not None:
            if e == '<SPACE>':
                e = ' '
            after = self.command_buffer[self.command_buffer_cursor:]
            before = self.command_buffer[:self.command_buffer_cursor]
            self.command_buffer = before + e + after
            self.command_buffer_cursor += 1

    def start(self):
        self.reactor = Input()
        self.window = FullscreenWindow()

        self.build_view()

        with self.window:
            with self.reactor:
                while self.running:
                    self.build_view()
                    ready_to_read, _, _ = select.select([self.socket,
                                                        self.reactor], [], [])

                    for r in ready_to_read:
                        if r == self.socket:
                            self.read_server_data()
                        else:
                            e = self.reactor.send(0)
                            if isinstance(e, PasteEvent):
                                for key in e.events:
                                    self.handle_keypress(key)
                            else:
                                self.handle_keypress(e)
                    sleep(0.01)

if __name__ == "__main__":
    client = LvlssClient(sys.argv[1])
    client.start()
