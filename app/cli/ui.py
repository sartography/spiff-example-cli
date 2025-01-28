import curses, curses.ascii
import sys
import logging
from datetime import datetime

from .content import Region, Content

from .menu import Menu
from .log_view import LogView
from .list_view import SpecListView, WorkflowListView
from .workflow_view import WorkflowView
from .spec_view import SpecView
from .user_input import UserInput, Field
from .task_filter_view import greedy_view, step_view

logger = logging.getLogger(__name__)

class CursesUIError(Exception):
    pass


class CursesUI:

    def __init__(self, window, engine, handlers):

        for i in range(1, int(curses.COLOR_PAIRS / 256)):
            curses.init_pair(i, i, 0)

        self.engine = engine
        self.handlers = dict((spec, handler(self)) for spec, handler in handlers.items())

        self.window = window
        y, x = self.window.getmaxyx()
        if y < 13:
            raise CursesUIError(f'A minimum height of 13 lines is required.')

        self.window.attron(curses.COLOR_WHITE)
        self.window.nodelay(True)

        self.left = Region()
        self.right = Region()
        self.top = Region()
        self.menu = Region()
        self.bottom = Region()

        self.menu_content = Content(self.menu)

        self._states = {
            'main_menu': Menu(self),
            'add_spec': SpecView(self),
            'log_view': LogView(self),
            'spec_list': SpecListView(self),
            'workflow_list': WorkflowListView(self),
            'workflow_view': WorkflowView(self),
            'user_input': UserInput(self),
        }
        self.resize()
        self._state = None
        self._escape_state = 'main_menu'
        self.state = 'main_menu'
        self.run()

    @property
    def state(self):
        return self._states[self._state]

    @state.setter
    def state(self, state):
        if state == 'log_view':
            self._escape_state = self._state
        elif state == 'user_input':
            self._escape_state = 'workflow_view'
        else:
            self._escape_state = 'main_menu'
        self._state = state
        self.menu_content.screen.erase()
        self.menu_content.screen.move(0, 0)
        if self.state.menu is not None:
            for action in self.state.menu:
                self.menu_content.screen.addstr(f'{action}  ')
        self.menu_content.screen.noutrefresh(0, 0, *self.menu.box)
        if self._state in ['spec_list', 'workflow_list']:
            self.state.refresh()
        self.state.draw()
        curses.doupdate()

    def run(self):

        while True:
            y, x = self.state.screen.getyx()
            ch = self.state.screen.getch()
            if ch == curses.KEY_RESIZE:
                self.resize()
                self.state.draw()
            elif ch == curses.ascii.ESC:
                self.state = self._escape_state
            elif chr(ch) == ';':
                self.state = 'log_view'
            else:
                try:
                    self.state.handle_key(ch, y, x)
                except Exception as exc:
                    logger.error(str(exc), exc_info=True)
            curses.doupdate()

    def start_workflow(self, spec_id, step):
        instance = self.engine.start_workflow(spec_id)
        self.set_workflow(instance, step, 'spec_list')

    def run_workflow(self, wf_id, step):
        instance = self.engine.get_workflow(wf_id)
        self.set_workflow(instance, step, 'workflow_list')

    def set_workflow(self, instance, step, prev_state):
        instance.step = step
        instance.update_task_filter(step_view.copy() if step else greedy_view.copy())
        if not step:
            instance.run_until_user_input_required()
        self._states['workflow_view'].instance = instance
        self._states['workflow_view']._previous_state = prev_state
        self.state = 'workflow_view'

    def quit(self):
        sys.exit(0)

    def resize(self):

        y, x = self.window.getmaxyx()
        div_y, div_x = y // 4, x // 3

        self.top.resize(1, 1, y - div_y - 3, x - 2)
        self.left.resize(1, 1, y - div_y - 3, div_x - 1)
        self.right.resize(1, div_x, y - div_y - 3, x - div_x - 1)
        self.menu.resize(y - div_y - 1, 1, 1, x - 2)
        self.bottom.resize(y - div_y + 1, 0, div_y - 1, x)

        for state in self._states.values():
            state.resize()
        self.menu_content.resize()

        self.window.hline(y - div_y, 0, curses.ACS_HLINE, x)
        self.window.refresh()

