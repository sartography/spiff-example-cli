import curses, curses.ascii
from .content import Content


class SpecView:

    def __init__(self, ui):

        self.left = Content(ui.left)
        self.right = Content(ui.right)
        self.add_spec = ui.engine.add_spec

        self.bpmn_id = None
        self.bpmn_files = []
        self.dmn_files = []

        self.bpmn_id_line = 2
        self.bpmn_line = 4
        self.dmn_line = 6
        self.add_line = 8

        self.screen = self.right.screen
        self.menu = self.right.menu

    def can_edit(self, lineno):
        return lineno in [self.bpmn_id_line, self.bpmn_line, self.dmn_line]

    def bpmn_filename(self, lineno):
        return lineno > self.bpmn_line and lineno <= self.bpmn_line + len(self.bpmn_files)

    def dmn_filename(self, lineno):
        return lineno > self.dmn_line and lineno <= self.dmn_line + len(self.dmn_files)

    def draw(self, lineno=None, clear=False):

        self.bpmn_line = 2 + self.bpmn_id_line
        self.dmn_line = 2 + self.bpmn_line + len(self.bpmn_files)
        self.add_line = 2 + self.dmn_line + len(self.dmn_files)

        self.left.screen.erase()
        self.right.screen.erase()

        self.left.screen.addstr(self.bpmn_id_line, self.left.region.width - 13, 'Process ID: ')
        self.left.screen.addstr(self.bpmn_line, self.left.region.width - 13, 'BPMN files: ')
        self.left.screen.addstr(self.dmn_line, self.left.region.width - 12, 'DMN files: ')

        if self.bpmn_id is not None:
            self.right.screen.addstr(self.bpmn_id_line, 0, self.bpmn_id)
        for offset, filename in enumerate(self.bpmn_files):
            self.right.screen.addstr(self.bpmn_line + offset + 1, 0, f'[X] {filename}')
        for offset, filename in enumerate(self.dmn_files):
            self.right.screen.addstr(self.dmn_line + offset + 1, 0, f'[X] {filename}')

        self.right.screen.addstr(self.add_line, 0, '[Add]', curses.A_BOLD)
        self.right.screen.addstr('  (Press ESC to cancel)')

        self.right.screen.move(lineno or self.bpmn_id_line, 0)
        if clear:
            self.right.screen.clrtoeol()

        self.left.screen.noutrefresh(self.left.first_visible, 0, *self.left.region.box)
        self.right.screen.noutrefresh(self.right.first_visible, 0, *self.right.region.box)

        curses.curs_set(1)
        curses.ungetch(curses.KEY_LEFT)

    def handle_key(self, ch, y, x):

        if ch == curses.KEY_BACKSPACE and self.can_edit(y):
            self.right.screen.move(y, max(0, x - 1))
            self.right.screen.delch(y, max(0, x - 1))
        elif ch == curses.KEY_LEFT and self.can_edit(y):
            self.right.screen.move(y, max(0, x - 1))
        elif ch == curses.KEY_RIGHT and self.can_edit(y):
            line = self.right.screen.instr(y, 0, self.right.region.width).decode('utf-8').rstrip()
            self.right.screen.move(y, min(len(line), x + 1))
        elif ch == curses.KEY_DOWN:
            if self.bpmn_filename(y + 1) or self.dmn_filename(y + 1):
                self.right.screen.move(y + 1, 1)
        elif ch == curses.KEY_UP:
            if y - 1 == self.bpmn_line or y - 1 == self.dmn_line:
                self.right.screen.move(y - 1, 0)
            elif self.bpmn_filename(y - 1) or self.dmn_filename(y - 1):
                self.right.screen.move(y - 1, 1)
        elif ch == curses.ascii.TAB:
            if y == self.bpmn_id_line:
                self.right.screen.move(self.bpmn_line, 0)
            elif y == self.bpmn_line or self.bpmn_filename(y):
                self.right.screen.move(self.dmn_line, 0)
            elif y == self.dmn_line or self.dmn_filename(y):
                self.right.screen.move(self.add_line, 1)
            elif y == self.add_line:
                self.right.screen.move(self.bpmn_id_line, 0)
        elif ch == curses.ascii.NL:
            text = self.right.screen.instr(y, 0, x).decode('utf-8').strip()
            if y == self.bpmn_id_line and text != '':
                self.bpmn_id = text
                self.right.screen.addstr(y, 0, text, curses.A_ITALIC)
                self.right.screen.move(self.bpmn_line, 0)
            elif y == self.bpmn_line and text != '':
                self.bpmn_files.append(text)
                self.draw(self.bpmn_line, True)
            elif y == self.dmn_line and text != '':
                self.dmn_files.append(text)
                self.draw(self.dmn_line, True)
            elif self.bpmn_filename(y):
                self.bpmn_files.pop(y - self.bpmn_line - 1)
                self.draw(self.bpmn_line)
            elif self.dmn_filename(y):
                self.dmn_files.pop(y - self.dmn_line - 1)
                self.draw(self.dmn_line)
            elif y == self.add_line:
                spec_id = self.add_spec(self.bpmn_id, self.bpmn_files, self.dmn_files or None)
                self.bpmn_id = None
                self.bpmn_files = []
                self.dmn_files = []
                self.draw()
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
        self.left.screen.noutrefresh(0, 0, *self.left.region.box)
        self.right.screen.noutrefresh(0, 0, *self.right.region.box)

    def resize(self):
        self.left.resize()
        self.right.resize()
