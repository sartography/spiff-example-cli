import curses, curses.ascii
import json
from datetime import datetime

from SpiffWorkflow.util.task import TaskState

from .content import Content
from .task_filter_view import TaskFilterView


class WorkflowView:

    def __init__(self, ui):

        self.left = Content(ui.left)
        self.right = Content(ui.right)

        self.handlers = ui.handlers
        self.task_filter_view = TaskFilterView(ui)

        self.instance = None

        self.task_view = 'list'
        self.info_view = 'task'
        self.scroll = 'left'
        self.selected = 0

        self.screen = self.left.screen
        self.menu = [
            '[l]ist/tree view',
            '[w]orkflow/task data view',
            '[g]reedy/step execution',
            '[f]ilter tasks',
            '[u]pdate waiting tasks',
            '[s]ave workflow state',
        ]

        self.styles = {
            'MAYBE': curses.color_pair(4),
            'LIKELY': curses.color_pair(4),
            'FUTURE': curses.color_pair(6),
            'WAITING': curses.color_pair(3),
            'READY': curses.color_pair(2),
            'STARTED': curses.color_pair(6),
            'ERROR': curses.color_pair(1),
            'CANCELLED': curses.color_pair(5),
        }

    def draw(self):
        self.update_task_tree()
        self.update_info()

    def update_task_tree(self):

        if self.selected > len(self.instance.filtered_tasks) - 1:
            self.selected = 0
        self.left.screen.erase()
        if len(self.instance.filtered_tasks) > 0:
            self.left.content_height = len(self.instance.filtered_tasks)
            self.left.resize()
            for idx, task in enumerate(self.instance.filtered_tasks):
                task_info = self.instance.get_task_display_info(task)
                indent = 2 * task_info['depth']
                color = self.styles.get(task_info['state'], 0)
                attr = color | curses.A_BOLD if idx == self.selected else color
                name = task_info['name']
                lane = task_info['lane'] or ''
                task_info = f'{lane}{name} [{task_info["state"]}]'
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
        if self.info_view == 'task' and len(self.instance.filtered_tasks) > 0:
            self.show_task()
        else:
            self.show_workflow()

    def show_task(self):
        task = self.instance.filtered_tasks[self.selected]
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
            'Spec': self.instance.name,
            'Ready tasks': len(self.instance.ready_tasks),
            'Waiting tasks': len(self.instance.waiting_tasks),
            'Finished tasks': len(self.instance.finished_tasks),
            'Total tasks': len(self.instance.tasks),
            'Running subprocesses': len(self.instance.running_subprocesses),
            'Total subprocesses': len(self.instance.subprocesses)
        }
        self._show_details(info, self.instance.data)

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

    def complete_task(self, task):
        handler = self.handlers.get(task.task_spec.__class__)
        if handler is not None:
            handler.show(task)
        else:
            self.instance.run_task(task)

    def handle_key(self, ch, y, x):

        if chr(ch).lower() == 'l':
            self.task_view = 'tree' if self.task_view == 'list' else 'list'
            self.update_task_tree()
        elif chr(ch).lower() == 'w':
            self.info_view = 'workflow' if self.info_view == 'task' else 'task'
            self.update_info()
        elif chr(ch).lower() == 'f':
            self.task_filter_view.show(self.instance.task_filter)
        elif chr(ch).lower() == 'u':
            self.instance.run_ready_events()
            if self.instance.step is False:
                self.instance.run_until_user_input_required()
            self.update_task_tree()
        elif chr(ch).lower() == 'g':
            self.instance.step = not self.instance.step
            if self.instance.step:
                self.instance.update_task_filter({'state': TaskState.ANY_MASK})
                self.update_task_tree()
        elif chr(ch).lower() == 's':
            self.instance.save()
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
            if self.scroll == 'left' and self.selected < len(self.instance.filtered_tasks) - 1:
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
            if self.scroll == 'left' and len(self.instance.filtered_tasks) > 0:
                task = self.instance.filtered_tasks[self.selected]
                if task.state == TaskState.READY:
                    self.complete_task(task)
                    self.draw()

    def resize(self):
        self.left.resize()
        self.right.resize()
