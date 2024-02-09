import curses, curses.ascii
from .content import Content


class Menu(Content):

    def __init__(self, region, menu_items):

        super().__init__(region)

        self.current_option = 0
        self.options, self.handlers  = zip(*menu_items)
        self.menu = None

    def draw(self):

        curses.curs_set(0)
        self.screen.erase()
        mid_x = self.region.width // 2
        mid_y = self.region.height // 2
        self.screen.move(1, mid_x)
        for idx, option in enumerate(self.options):
            attr = curses.A_BOLD if idx == self.current_option else 0
            self.screen.addstr(mid_y + idx, mid_x - len(option) // 2, f'{option}\n', attr)
        self.screen.noutrefresh(self.first_visible, 0, *self.region.box)

    def handle_key(self, ch, y, x):

        if ch == curses.KEY_DOWN and self.current_option < len(self.options) - 1:
            self.current_option += 1
            self.draw()
            self.screen.noutrefresh(self.first_visible, 0, *self.region.box)
        elif ch == curses.KEY_UP and self.current_option > 0:
            self.current_option -= 1
            self.draw()
            self.screen.noutrefresh(self.first_visible, 0, *self.region.box)
        elif ch == curses.ascii.NL:
            self.handlers[self.current_option]()


