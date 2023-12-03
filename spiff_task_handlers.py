import curses, curses.ascii
import os, json
import logging

from jinja2 import Template

from curses_app.user_input import Field

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
            option_map = dict([ (v['title'], v['const']) for v in config['oneOf'] ])
            label = f'{config["title"]} ' + '(' + ', '.join(option_map) + ')'
            def validate(value):
                if value not in option_map:
                    raise Exception(f'Invalid option: {value}')
                else:
                    return option_map[value]
            field = Field(name, label, lambda v: v, validate, '')
        elif config['type'] == 'integer':
            field = Field(name, config['title'], lambda v: str(v) if v is not None else '', int, None)
        else:
            field = Field(name, config['title'], str, str, '')
        return field

    def get_fields(self):
        filename = self.task.task_spec.extensions['properties']['formJsonSchemaFilename']
        schema = json.load(open(os.path.join(forms_dir, filename)))
        return [self.create_field(name, config) for name, config in schema['properties'].items()]

    def on_complete(self, results):
        self.task.update_data(results)
        super().on_complete(results)

