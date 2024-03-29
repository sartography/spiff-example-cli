import curses, curses.ascii
from .content import Content


class Field:

    def __init__(self, name, label, to_str, from_str, value):
        self.name = name
        self.label = label
        self.to_str = to_str
        self.from_str = from_str
        self.value = value

class UserInput:

    def __init__(self, left, right):

        self.left = Content(left)
        self.right = Content(right)
        self.screen = self.right.screen

        self.instructions = ''

        self.fields = []
        self.on_complete = None

        self.current_field = 0
        self.offsets = []

        self.menu = ['[ESC] to cancel']

    def configure(self, instructions, fields, on_complete):

        self.instructions = instructions
        self.fields = fields
        self.on_complete = on_complete
        self.offsets = []
        self.current_field = 0
        self.results = {}

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

    def handle_key(self, ch, y, x):

        if ch == curses.KEY_BACKSPACE:
            self.right.screen.move(y, max(0, x - 1))
            self.right.screen.delch(y, max(0, x - 1))
        elif ch == curses.ascii.STX:
            self.right.screen.move(y, 0)
        elif ch == curses.ascii.ETX:
            line = self.right.screen.instr(y, 0, self.right.region.width).decode('utf-8').rstrip()
            self.right.screen.move(y, len(line) - 1)
        elif ch == curses.KEY_LEFT:
            self.right.screen.move(y, max(0, x - 1))
        elif ch == curses.KEY_RIGHT:
            line = self.right.screen.instr(y, 0, self.right.region.width).decode('utf-8').rstrip()
            self.right.screen.move(y, min(len(line), x + 1))
        elif ch == curses.ascii.TAB:
            self.current_field = 0 if self.current_field == len(self.offsets) - 1 else self.current_field + 1
            self.right.screen.move(self.offsets[self.current_field], 0)
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
