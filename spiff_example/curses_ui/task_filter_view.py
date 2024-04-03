from datetime import datetime

from SpiffWorkflow import TaskState

from .user_input import UserInput, Field, SimpleField


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
        user_input.fields = [
            TaskStateField('state', 'State', task_filter['state']),
            SimpleField(str, 'spec_name', 'Task spec', task_filter['spec_name']),
            TimestampField('updated_ts', 'Updated on or after', task_filter['updated_ts']),
        ]
        user_input.instructions = ''

        def on_complete(results):
            self.ui._states['view_workflow'].current_filter = results
            self.ui.state = 'view_workflow'
        user_input.on_complete = on_complete

        self.ui.state = 'user_input'
