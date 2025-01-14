import json
import curses, curses.ascii
from .content import Content


class Field:

    def __init__(self, name, label, default):
        self.name = name
        self.label = label
        self.value = default

    def to_str(self, value):
        return value

    def from_str(self, value):
        return value

class JsonField(Field):

    def to_str(self, value):
        return json.dumps(value, indent=2, separators=[', ', ': '])

    def from_str(self, value):
        return json.loads(value)

class SimpleField(Field):

    def __init__(self, _type, name, label, default):
        super().__init__(name, label, default)
        self._type = _type

    def to_str(self, value):
        return '' if value is None else str(value)

    def from_str(self, value):
        return None if value == '' else self._type(value)

class Option(Field):

    def __init__(self, options, name, label, default):
        super().__init__(name, label, default)
        self.options = options

    def to_str(self, value):
        return value

    def from_str(self, value):
        if value in self.options:
            return self.options[value]
        else:
            raise Exception(f'Invalid option: {value}')

class UserInput:

    def __init__(self, ui):

        self.left = Content(ui.left)
        self.right = Content(ui.right)
        self.screen = self.right.screen

        self.on_complete = lambda results: results
        self.instructions = ''
        self.fields = []

        self.current_field = 0
        self.offsets = []

        self.menu = ['[ESC] to cancel']

    def draw(self, itemno=None):

        self.left.screen.erase()
        self.right.screen.erase()
        self.left.screen.move(0, 0)
        self.right.screen.move(0, 0)

        if self.instructions != '':
            self.right.screen.addstr(2, 0, self.instructions)

        y, x = self.right.screen.getyx()
        for idx, field in enumerate(self.fields):
            offset = y + idx * 2
            self.offsets.append(offset)
            text = f'{field.label}: '
            self.left.screen.addstr(offset, self.left.region.width - len(text), text, curses.A_BOLD)
            self.right.screen.addstr(offset, 0, field.to_str(field.value))

        y, x = self.right.screen.getyx()
        offset = y + 2
        self.right.screen.addstr(offset, 0, '[Done]', curses.A_BOLD)
        self.offsets.append(offset)

        self.right.screen.move(self.offsets[itemno or 0], 0)

        self.left.screen.noutrefresh(0, 0, *self.left.region.box)
        self.right.screen.noutrefresh(0, 0, *self.right.region.box)

        curses.curs_set(1)
        curses.ungetch(curses.KEY_LEFT)

    def clear(self):
        self.instructions = ''
        self.fields = []
        self.offsets = []
        self.current_field = 0

    def handle_key(self, ch, y, x):

        if ch == curses.KEY_BACKSPACE:
            self.right.screen.move(y, max(0, x - 1))
            self.right.screen.delch(y, max(0, x - 1))
        elif ch == curses.KEY_LEFT:
            self.right.screen.move(y, max(0, x - 1))
        elif ch == curses.KEY_RIGHT:
            line = self.right.screen.instr(y, 0, self.right.region.width).decode('utf-8').rstrip()
            self.right.screen.move(y, min(len(line), x + 1))
        elif ch == curses.ascii.TAB:
            self.current_field = 0 if self.current_field == len(self.offsets) - 1 else self.current_field + 1
            self.right.screen.move(self.offsets[self.current_field], 0)
        elif curses.ascii.unctrl(ch) == '^E':
            line = self.right.screen.instr(y, 0, self.right.region.width).decode('utf-8').rstrip()
            self.right.screen.move(y, len(line))
        elif curses.ascii.unctrl(ch) == '^A':
            self.right.screen.move(y, 0)
        elif curses.ascii.unctrl(ch) == '^U':
            self.right.screen.move(y, 0)
            self.right.screen.clrtoeol()
        elif curses.ascii.isprint(ch):
            self.right.screen.echochar(ch)

        self.left.screen.noutrefresh(self.left.first_visible, 0, *self.left.region.box)
        self.right.screen.noutrefresh(self.left.first_visible, 0, *self.right.region.box)

        if ch == curses.ascii.NL:
            if self.current_field < len(self.offsets) - 1:
                field = self.fields[self.current_field]
                line = self.right.screen.instr(y, 0, self.right.region.width).decode('utf-8').rstrip()
                self.right.screen.addstr(self.offsets[self.current_field], 0, line, curses.A_ITALIC)
                field.value = field.from_str(line)
                curses.ungetch(curses.ascii.TAB)
                self.left.screen.noutrefresh(self.left.first_visible, 0, *self.left.region.box)
                self.right.screen.noutrefresh(self.left.first_visible, 0, *self.right.region.box)
            else:
                self.on_complete(dict((f.name, f.value) for f in self.fields))

    def resize(self):
        self.left.resize()
        self.right.resize()
