import curses, curses.ascii

class Region:

    def __init__(self):
        self.top = 0
        self.left = 0
        self.height = 1
        self.width = 1

    @property
    def bottom(self):
        return self.top + self.height - 1

    @property
    def right(self):
        return self.left + self.width - 1

    @property
    def box(self):
        return self.top, self.left, self.bottom, self.right

    def resize(self, top, left, height, width):
        self.top, self.left, self.height, self.width = top, left, height, width


class Content:

    def __init__(self, region):

        self.region = region

        self.screen = curses.newpad(self.region.height, self.region.width)
        self.screen.keypad(True)
        self.screen.scrollok(True)
        self.screen.idlok(True)
        self.screen.attron(curses.COLOR_WHITE)

        self.content_height = 1
        self.first_visible = 0

        self.menu = ['[ESC] return to main menu']

    @property
    def last_visible(self):
        return self.first_visible + self.region.height - 1

    def scroll_up(self, y):
        if self.first_visible > 0 and y == self.first_visible:
            self.first_visible -= 1
        self.screen.move(max(0, y - 1), 0)

    def scroll_down(self, y):
        if self.last_visible < self.content_height - 1 and y == self.last_visible - 1:
            self.first_visible += 1
        self.screen.move(min(self.content_height - 1, y + 1), 0)

    def page_up(self, y):
        self.first_visible = max(0, y - self.region.height)
        self.screen.move(self.first_visible, 0)

    def page_down(self, y):
        self.first_visible = min(self.content_height - self.region.height, y + self.region.height)
        self.screen.move(self.first_visible, 0)

    def draw(self):
        pass

    def handle_key(self, ch, y, x):
        pass

    def resize(self):
        self.screen.resize(max(self.region.height, self.content_height), self.region.width)
        self.screen.noutrefresh(self.first_visible, 0, *self.region.box)

