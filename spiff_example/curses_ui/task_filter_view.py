from datetime import datetime

from SpiffWorkflow import TaskState

from .user_input import UserInput, Field, SimpleField

greedy_view = {
    'state': TaskState.READY|TaskState.WAITING,
    'spec_name': None,
    'updated_ts': 0,
}

step_view = {
    'state': TaskState.ANY_MASK,
    'spec_name': None,
    'updated_ts': 0
}


class TaskStateField(Field):
    def to_str(self, value): return TaskState.get_name(value)
    def from_str(self, value): return TaskState.get_value(value)

class TimestampField(Field):
    def to_str(self, value): return datetime.fromtimestamp(value).isoformat()
    def from_str(self, value): return datetime.fromisoformat(value).timestamp()

class TaskFilterView:

    def __init__(self, ui):
        self.ui = ui

    def show(self, task_filter):
        user_input = self.ui._states['user_input']
        user_input.clear()
        user_input.fields = [
            TaskStateField('state', 'State', task_filter['state']),
            SimpleField(str, 'spec_name', 'Task spec', task_filter['spec_name']),
            TimestampField('updated_ts', 'Updated on or after', task_filter['updated_ts']),
        ]
        user_input.instructions = ''

        def on_complete(results):
            self.ui._states['workflow_view'].instance.update_task_filter(results)
            self.ui.state = 'workflow_view'
        user_input.on_complete = on_complete

        self.ui.state = 'user_input'
