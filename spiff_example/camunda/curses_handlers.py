from jinja2 import Template

from SpiffWorkflow.util.deep_merge import DeepMerge
from SpiffWorkflow.camunda.specs.user_task import EnumFormField

from ..curses_ui.user_input import Field, Option, SimpleField
from ..curses_ui.human_task_handler import TaskHandler

class CamundaTaskHandler(TaskHander):

    def set_instructions(self, task):
        text = f'{self.task.task_spec.bpmn_name}'
        if self.task.task_spec.documentation is not None:
            template = Template(self.task.task_spec.documentation)
            text += template.render(self.task.data)
        text += '\n\n'
        self.ui._states['user_input'].instructions = text


class ManualTaskHandler(TaskHandler):
    pass


class UserTaskHandler(TaskHandler):

    def set_fields(self, task):
        for field in task.task_spec.form.fields:
            if isinstance(field, EnumFormField):
                options = dict((opt.name, opt.id) for opt in field.options)
                label = field.label + ' (' + ', '.join(options) + ')'
                field = Option(options, field.id, label, '')
            elif field.type == 'long':
                field = SimpleField(int, field.id, field.label, '')
            else:
                field = Field(field.id, field.label, '')
            self.ui._states['user_input'].fields.append(field)

   def update_data(self, dct, name, value):
        path = name.split('.')
        current = dct
        for component in path[:-1]:
            if component not in current:
                current[component] = {}
            current = current[component]
        current[path[-1]] = value

    def on_complete(self, results):
        dct = {}
        for name, value in results.items():
            self.update_data(dct, name, value)
        DeepMerge.merge(self.task.data, dct)
        super().on_complete({})
