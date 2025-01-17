import json
import os

from jinja2 import Template

from ..cli.user_input import SimpleField, Option, JsonField
from ..cli.human_task_handler import TaskHandler


class SpiffTaskHandler(TaskHandler):

    def set_instructions(self, task):
        user_input = self.ui._states["user_input"]
        user_input.instructions = f"{self.task.task_spec.bpmn_name}\n\n"
        text = self.task.task_spec.extensions.get("instructionsForEndUser")
        if text is not None:
            template = Template(text)
            user_input.instructions += template.render(self.task.data)
        user_input.instructions += "\n\n"


class ManualTaskHandler(SpiffTaskHandler):
    pass


class UserTaskHandler(SpiffTaskHandler):

    def set_fields(self, task):

        file_path = os.path.join(
            os.environ["forms_directory"],
            task.task_spec.extensions["properties"]["formJsonSchemaFilename"],
        )
        with open(file_path, encoding="utf-8") as form:
            schema = json.load(form)
        user_input = self.ui._states["user_input"]
        for name, config in schema["properties"].items():
            if "oneOf" in config:
                options = dict([(v["title"], v["const"]) for v in config["oneOf"]])
                label = f'{config["title"]} ' + "(" + ", ".join(options) + ")"
                field = Option(options, name, label, "")
            elif config["type"] == "string":
                field = SimpleField(str, name, config["title"], None)
            elif config["type"] == "integer":
                field = SimpleField(int, name, config["title"], None)
            elif config["type"] == "number":
                field = SimpleField(float, name, config["title"], None)
            elif config["type"] == "boolean":
                field = SimpleField(bool, name, config["title"], None)
            else:
                field = JsonField(name, config["title"], None)
            user_input.fields.append(field)
