import curses, curses.ascii
from .content import Content


class ListView(Content):

    def __init__(self, region, header, select_action, delete_action, refresh_action):

        super().__init__(region)
        self.header = header
        self.select_action = select_action
        self.delete_action = delete_action
        self.refresh_action = refresh_action

        self.items = []
        self.item_ids = []
        self.selected = 0
        self.selected_attr = curses.color_pair(6) | curses.A_BOLD

        self.menu = [
            '[ENTER] run',
            '[s]tep',
            '[d]elete',
        ] + self.menu

    def refresh(self):
        items = self.refresh_action()
        if len(items) > 0:
            item_ids, items = zip(*[(item[0], item[1:]) for item in items])
            self.item_ids = list(item_ids)
            self.items = [ [str(v) if v is not None else '' for v in item] for item in items ]
        else:
            self.items, self.item_ids = [], []

    def draw(self):

        self.screen.erase()
        self.screen.move(0, 0)
        col_widths = [2] + [max([len(val) for val in item]) for item in zip(*[self.header] + list(self.items))]
        fmt = '  '.join([ f'{{{idx}:{w}s}}' for idx, w in enumerate(col_widths) ])
        self.screen.addstr(fmt.format('', *self.header) + '\n', curses.A_BOLD)

        for idx, item in enumerate(self.items):
            attr = self.selected_attr if idx == self.selected else 0
            self.screen.addstr('\n' + fmt.format('*', *item), attr)

        self.screen.move(self.selected + 2, 0)
        self.screen.noutrefresh(self.first_visible, 0, *self.region.box)

    def handle_key(self, ch, y, x):
        if ch == curses.ascii.NL:
            item_id = self.item_ids[self.selected]
            self.select_action(item_id, step=False)
        elif chr(ch).lower() == 's':
            item_id = self.item_ids[self.selected]
            self.select_action(item_id, step=True)
        elif ch == curses.KEY_DOWN and self.selected < len(self.items) - 1:
            self.selected += 1
            self.draw()
        elif ch == curses.KEY_UP and self.selected > 0:
            self.selected -= 1
            self.draw()
        elif chr(ch).lower() == 'd':
            item_id = self.item_ids[self.selected]
            self.delete_action(item_id)
            self.items.pop(self.selected)
            self.item_ids.pop(self.selected)
            if self.selected == len(self.item_ids):
                self.selected = max(0, self.selected - 1)
            self.draw()


class SpecListView(ListView):
    def __init__(self, ui):
        super().__init__(
            ui.top,
            ['Name', 'Filename'],
            ui.start_workflow,
            ui.engine.delete_workflow_spec,
            ui.engine.list_specs,
        )

class WorkflowListView(ListView):
    def __init__(self, ui):
        super().__init__(
            ui.top,
            ['Spec', 'Active tasks', 'Started', 'Updated', 'Ended'],
            ui.run_workflow,
            ui.engine.delete_workflow,
            lambda: ui.engine.list_workflows(self.include_completed),
        )
        self.include_completed = False
        self.menu.insert(-1, '[i]nclude/exclude completed')

    def handle_key(self, ch, y, x):
        if chr(ch).lower() == 'i':
            self.include_completed = not self.include_completed
            self.refresh()
            self.draw()
        else:
            super().handle_key(ch, y, x)
