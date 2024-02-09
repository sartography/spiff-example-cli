from jinja2 import Template

from SpiffWorkflow.util.deep_merge import DeepMerge
from SpiffWorkflow.camunda.specs.user_task import EnumFormField

from ..curses_ui.user_input import Field

class TaskHandler:

    def __init__(self, task):
        self.task = task

    def get_documentation(self):
        text = f'{self.task.task_spec.bpmn_name}'
        if self.task.task_spec.documentation is not None:
            template = Template(self.task.task_spec.documentation)
            text += template.render(self.task.data)
        text += '\n\n'
        return text

    def update_data(self, dct, name, value):
        path = name.split('.')
        current = dct
        for component in path[:-1]:
            if component not in current:
                current[component] = {}
            current = current[component]
        current[path[-1]] = value

    def on_complete(self, results):
        self.task.run()


class ManualTaskHandler(TaskHandler):

    def get_configuration(self):
        return self.get_documentation(), []


class UserTaskHandler(TaskHandler):

    def get_configuration(self):
        return self.get_documentation(), self.get_fields()

    def create_field(self, field):
        if isinstance(field, EnumFormField):
            option_map = dict((opt.name, opt.id) for opt in field.options)
            label = field.label + ' (' + ', '.join(option_map) + ')'
            def validate(value):
                if value not in option_map:
                    raise Exception(f'Invalid option: {value}')
                else:
                    return option_map[value]
            field = Field(field.id, label, lambda v: v, validate, '')
        elif field.type == 'long':
            field = Field(field.id, field.label, lambda v: str(v) if v is not None else '', int, None)
        else:
            field = Field(field.id, field.label, str, str, '')
        return field

    def get_fields(self):
        return [self.create_field(f) for f in self.task.task_spec.form.fields]

    def on_complete(self, results):
        dct = {}
        for name, value in results.items():
            self.update_data(dct, name, value)
        DeepMerge.merge(self.task.data, dct)
        super().on_complete(results)
