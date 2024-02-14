import os, json
import logging

from jinja2 import Template

from ..curses_ui.user_input import SimpleField, Option, JsonField

forms_dir = 'bpmn/tutorial/forms'

class TaskHandler:

    def __init__(self, task):
        self.task = task

    def get_instructions(self):
        instructions = f'{self.task.task_spec.bpmn_name}\n\n'
        text = self.task.task_spec.extensions.get('instructionsForEndUser')
        if text is not None:
            template = Template(text)
            instructions += template.render(self.task.data)
        instructions += '\n\n'
        return instructions

    def on_complete(self, results):
        self.task.run()


class ManualTaskHandler(TaskHandler):

    def get_configuration(self):
        return self.get_instructions(), []


class UserTaskHandler(TaskHandler):

    def get_configuration(self):
        return self.get_instructions(), self.get_fields()

    def create_field(self, name, config):
        if 'oneOf' in config:
            options = dict([ (v['title'], v['const']) for v in config['oneOf'] ])
            label = f'{config["title"]} ' + '(' + ', '.join(options) + ')'
            field = Option(options, name, label, '')
        elif config['type'] == 'string':
            field = SimpleField(str, name, config['title'], None)
        elif config['type'] == 'integer':
            field = SimpleField(int, name, config['title'], None)
        elif config['type'] == 'number':
            field = SimpleField(float, name, config['title'], None)
        elif config['type'] == 'boolean':
            field = SimpleField(bool, name, config['title'], None)
        else:
            field = JsonField(name, config['title'], None)
        return field

    def get_fields(self):
        filename = self.task.task_spec.extensions['properties']['formJsonSchemaFilename']
        schema = json.load(open(os.path.join(forms_dir, filename)))
        return [self.create_field(name, config) for name, config in schema['properties'].items()]

    def on_complete(self, results):
        self.task.set_data(**results)
        super().on_complete(results)

