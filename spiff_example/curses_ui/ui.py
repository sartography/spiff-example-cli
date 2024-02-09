import curses, curses.ascii
import sys
import logging
from datetime import datetime

from .content import Region, Content

from .menu import Menu
from .log_view import LogView
from .list_view import ListView
from .workflow_view import WorkflowView, default_view, run_view
from .spec_view import SpecView
from .user_input import UserInput, Field

logger = logging.getLogger(__name__)


class CursesUI:

    def __init__(self, window, engine):

        for i in range(1, int(curses.COLOR_PAIRS / 256)):
            curses.init_pair(i, i, 0)

        self.engine = engine

        self.window = window
        self.window.attron(curses.COLOR_WHITE)
        self.window.nodelay(True)

        self.left = Region()
        self.right = Region()
        self.top = Region()
        self.menu = Region()
        self.bottom = Region()

        self.menu_content = Content(self.menu)

        self._states = {
            'main_menu': Menu(self.top, [
                ('Add spec', lambda: self.set_state('add_spec')),
                ('Start Workflow', lambda: self.set_state('start_workflow')),
                ('Resume workflow', lambda: self.set_state('resume_workflow')),
                ('List workflows', lambda: self.set_state('list_workflows')),
                ('Quit', self.quit),
            ]),
            'add_spec': SpecView(self.left, self.right, self.engine.add_spec),
            'log_view': LogView(self.bottom),
            'start_workflow': ListView(
                self.top,
                ['Name', 'Filename'],
                self.start_workflow,
                self.engine.delete_workflow_spec,
            ),
            'resume_workflow': ListView(
                self.top,
                ['Spec', 'Active tasks', 'Started', 'Updated'],
                self.run_workflow,
                self.engine.delete_workflow
            ),
            'list_workflows': ListView(
                self.top,
                ['Spec', 'Active tasks', 'Started', 'Updated', 'Ended'],
                self.view_workflow,
                self.engine.delete_workflow,
            ),
            'view_workflow': WorkflowView(self),
            'user_input': UserInput(self.left, self.right),
        }
        self.resize()
        self._state = None
        self.state = 'main_menu'
        self.run()

    @property
    def state(self):
        return self._states[self._state]

    @state.setter
    def state(self, state):
        self._state = state
        self.menu_content.screen.erase()
        if self.state.menu is not None:
            for action in self.state.menu:
                self.menu_content.screen.addstr(f'{action}  ')
        self.menu_content.screen.noutrefresh(0, 0, *self.menu.box)
        self.state.draw()
        curses.doupdate()

    def set_state(self, state):  # For callbacks on different screens
        if state == 'start_workflow':
            self._switch_to_list('start_workflow', self.engine.list_specs())
        elif state == 'resume_workflow':
            self._switch_to_list('resume_workflow', self.engine.list_workflows())
        elif state == 'list_workflows':
            self._switch_to_list('list_workflows', self.engine.list_workflows(True))
        self.state = state

    def run(self):

        while True:
            y, x = self.state.screen.getyx()
            ch = self.state.screen.getch()
            if ch == curses.KEY_RESIZE:
                self.resize()
                self.state.draw()
            elif ch == curses.ascii.ESC:
                if self._state in ['log_view', 'view_workflow']:
                    self.set_state(self.state._previous_state)
                elif self._state == 'user_input':
                    self.set_state('view_workflow')
                else:
                    self.state = 'main_menu'
            elif chr(ch) == ';':
                self._states['log_view']._previous_state = self._state
                self.state = 'log_view'
            else:
                try:
                    self.state.handle_key(ch, y, x)
                except Exception as exc:
                    logger.error(str(exc), exc_info=True)
            curses.doupdate()

    def start_workflow(self, spec_id):
        wf_id = self.engine.start_workflow(spec_id)
        self.set_workflow(wf_id, False, run_view)

    def _switch_to_list(self, state, items):
        self._states[state].items = items
        self.state = state

    def run_workflow(self, wf_id):
        self.set_workflow(wf_id, False, run_view)

    def view_workflow(self, wf_id):
        self.set_workflow(wf_id, True, default_view)

    def set_workflow(self, wf_id, step, filters):
        workflow = self.engine.get_workflow(wf_id)
        self._states['view_workflow'].set_workflow(workflow, wf_id)
        self._states['view_workflow'].step = step
        self._states['view_workflow']._previous_state = 'list_workflows' if step else 'resume_workflow'
        self._states['view_workflow'].current_filter = filters.copy()
        self._run_workflow()

    def _run_workflow(self):
        if not self._states['view_workflow'].step:
            self.engine.run_until_user_input_required(self._states['view_workflow'].workflow)
        self.state = 'view_workflow'

    def show_filters(self, fields):

        def on_complete(results):
            self._states['view_workflow'].current_filter.update(results)
            self.state = 'view_workflow'

        self._states['user_input'].configure('', fields, on_complete)
        self.state = 'user_input'

    def complete_task(self, task):

        handler = self.engine.handler(task)
        if handler is not None:
            instructions, fields = handler.get_configuration()
            def on_complete(results):
                handler.on_complete(results)
                self._run_workflow()
            self._states['user_input'].configure(instructions, fields, on_complete)
            self.state = 'user_input'
        else:
            task.run()
            self._run_workflow()

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

