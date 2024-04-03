import curses, curses.ascii
import json
from datetime import datetime

from SpiffWorkflow.util.task import TaskState

from .content import Content
from .task_filter_view import TaskFilterView

default_view = {
    'state': TaskState.READY|TaskState.WAITING,
    'spec_name': None,
    'updated_ts': 0,
}

class WorkflowView:

    def __init__(self, ui):

        self.left = Content(ui.left)
        self.right = Content(ui.right)

        self.engine = ui.engine
        self.task_filter_view = TaskFilterView(ui)
        self.complete_task = ui.complete_task

        self.workflow = None
        self.workflow_id = None
        self.current_filter = default_view.copy()
        self.step = True
        self.task_view = 'list'
        self.info_view = 'task'
        self.scroll = 'left'
        self.tasks = []
        self.selected = 0
        self._previous_state = None

        self.screen = self.left.screen
        self.menu = [
            '[l]ist/tree view',
            '[w]orkflow/task data view',
            '[f]ilter tasks',
            '[u]pdate waiting tasks',
            '[r]un/step execution',
            '[s]ave workflow state',
        ]

        self.styles = {
            TaskState.MAYBE: curses.color_pair(4),
            TaskState.LIKELY: curses.color_pair(4),
            TaskState.FUTURE: curses.color_pair(6),
            TaskState.WAITING: curses.color_pair(3),
            TaskState.READY: curses.color_pair(2),
            TaskState.STARTED: curses.color_pair(6),
            TaskState.ERROR: curses.color_pair(1),
            TaskState.CANCELLED: curses.color_pair(5),
        }

    def set_workflow(self, workflow, wf_id):
        self.workflow = workflow
        self.workflow_id = wf_id

    def draw(self):
        self.update_task_tree()
        self.update_info()

    def update_task_tree(self):

        self.tasks = [t for t in self.workflow.get_tasks(**self.current_filter)]
        if self.selected > len(self.tasks) - 1:
            self.selected = 0
        self.left.screen.erase()
        if len(self.tasks) > 0:
            self.left.content_height = len(self.tasks)
            self.left.resize()
            for idx, task in enumerate(self.tasks):
                indent = 2 * task.depth
                color = self.styles.get(task.state, 0)
                attr = color | curses.A_BOLD if idx == self.selected else color
                name = task.task_spec.bpmn_name or task.task_spec.name
                lane = f'({task.task_spec.lane}) ' if task.task_spec.lane is not None else ''
                state = TaskState.get_name(task.state)
                task_info = f'{lane}{name} [{state}]'
                if self.task_view == 'list':
                    self.left.screen.addstr(idx, 0, task_info, attr)
                else:
                    self.left.screen.addstr(idx, 0, ' ' * indent + task_info, attr)
            if self.info_view == 'task':
                self.show_task()
            self.left.screen.move(self.selected, 0)
        else:
            self.info_view = 'workflow'
            self.left.content_height = self.left.region.height - 1
            self.left.resize()
            self.left.screen.addstr(0, 0, 'No tasks available')
        self.left.screen.noutrefresh(self.left.first_visible, 0, *self.left.region.box)

    def update_info(self):
        if self.info_view == 'task' and len(self.tasks) > 0:
            self.show_task()
        else:
            self.show_workflow()

    def show_task(self):
        task = self.tasks[self.selected]
        info = {
            'Name': task.task_spec.name,
            'Bpmn ID': task.task_spec.bpmn_id or '',
            'Bpmn name': task.task_spec.bpmn_name or '',
            'Description': task.task_spec.description,
            'Last state change': datetime.fromtimestamp(task.last_state_change),
        }
        self._show_details(info, task.data)

    def show_workflow(self):
        info = {
            'Spec': self.workflow.spec.name,
            'Ready tasks': len(self.workflow.get_tasks(state=TaskState.READY)),
            'Waiting tasks': len(self.workflow.get_tasks(state=TaskState.WAITING)),
            'Finished tasks': len(self.workflow.get_tasks(state=TaskState.FINISHED_MASK)),
            'Total tasks': len(self.workflow.get_tasks()),
            'Waiting subprocesses': len([sp for sp in self.workflow.subprocesses.values() if not sp.is_completed()]),
            'Total subprocesses': len(self.workflow.subprocesses)
        }
        self._show_details(info, self.workflow.data)

    def _show_details(self, info, data=None):

        self.right.screen.erase()

        lines = len(info)
        if data is not None:
            lines += 2
            serialized = {}
            for key, value in data.items():
                serialized[key] = json.dumps(value, indent=2)
                lines += len(serialized[key].split('\n'))
        self.right.content_height = lines + 1

        for name, value in info.items():
            self.right.screen.addstr(f'{name}: ', curses.A_BOLD)
            self.right.screen.addstr(f'{value}\n')

        if data is not None:
            self.right.screen.addstr('\nData\n', curses.A_BOLD)
            for name, value in serialized.items():
                self.right.screen.addstr(f'{name}: ', curses.A_ITALIC)
                self.right.screen.addstr(f'{value}\n')

        self.right.screen.noutrefresh(self.right.first_visible, 0, *self.right.region.box)

    def handle_key(self, ch, y, x):

        if chr(ch).lower() == 'l':
            self.task_view = 'tree' if self.task_view == 'list' else 'list'
            self.update_task_tree()
        elif chr(ch).lower() == 'w':
            self.info_view = 'workflow' if self.info_view == 'task' else 'task'
            self.update_info()
        elif chr(ch).lower() == 'f':
            self.task_filter_view.show(self.current_filter)
        elif chr(ch).lower() == 'u':
            if self.step is False:
                self.engine.run_ready_events(self.workflow)
            else:
                self.workflow.refresh_waiting_tasks()
            self.update_task_tree()
        elif chr(ch).lower() == 'r':
            self.step = not self.step
        elif chr(ch).lower() == 's':
            self.engine.update_workflow(self.workflow, self.workflow_id)
        elif ch == curses.ascii.TAB:
            if self.scroll == 'right':
                self.scroll = 'left'
                self.screen = self.left.screen
                curses.curs_set(0)
            else:
                self.scroll = 'right'
                self.screen = self.right.screen
                self.right.screen.move(0, 0)
                curses.curs_set(1)
        elif ch == curses.KEY_DOWN:
            if self.scroll == 'left' and self.selected < len(self.tasks) - 1:
                self.selected += 1
                self.left.scroll_down(y)
                self.update_task_tree()
            else:
                self.right.scroll_down(y)
                self.right.screen.noutrefresh(self.right.first_visible, 0, *self.right.region.box)
        elif ch == curses.KEY_UP:
            if self.scroll == 'left' and self.selected > 0:
                self.selected -= 1
                self.left.scroll_up(y)
                self.update_task_tree()
            elif self.scroll == 'right':
                self.right.scroll_up(y)
                self.right.screen.noutrefresh(self.right.first_visible, 0, *self.right.region.box)
        elif ch == curses.ascii.NL:
            if self.scroll == 'left' and len(self.tasks) > 0:
                task = self.tasks[self.selected]
                if task.state == TaskState.READY:
                    self.complete_task(task)
                    self.draw()

    def resize(self):
        self.left.resize()
        self.right.resize()
