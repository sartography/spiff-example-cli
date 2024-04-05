import os, json
import logging

from jinja2 import Template

from ..curses_ui.user_input import SimpleField, Option, JsonField

forms_dir = 'bpmn/tutorial/forms'

class TaskHandler:

    def __init__(self, ui):
        self.ui = ui
        self.task = None

    def set_instructions(self, task):
        user_input = self.ui._states['user_input']
        user_input.instructions = f'{self.task.task_spec.bpmn_name}\n\n'
        text = self.task.task_spec.extensions.get('instructionsForEndUser')
        if text is not None:
            template = Template(text)
            user_input.instructions += template.render(self.task.data)
        user_input.instructions += '\n\n'

    def on_complete(self, results):
        self.ui._states['user_input'].fields = []
        instance = self.ui._states['workflow_view'].instance
        instance.run_task(self.task, results)
        self.ui.state = 'workflow_view'

    def show(self, task):
        self.task = task
        self.set_instructions(task)
        self.ui._states['user_input'].on_complete = self.on_complete
        self.ui.state = 'user_input'

class ManualTaskHandler(TaskHandler):
    pass

class UserTaskHandler(TaskHandler):

    def set_fields(self, task):

        filename = task.task_spec.extensions['properties']['formJsonSchemaFilename']
        schema = json.load(open(os.path.join(forms_dir, filename)))
        user_input = self.ui._states['user_input']
        for name, config in schema['properties'].items():
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
            user_input.fields.append(field)

    def show(self, task):
        self.set_fields(task)
        super().show(task)

