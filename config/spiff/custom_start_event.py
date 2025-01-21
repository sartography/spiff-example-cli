import logging
import os

from RestrictedPython import safe_globals

from SpiffWorkflow.spiff.parser import SpiffBpmnParser
from SpiffWorkflow.spiff.specs.defaults import UserTask, ManualTask
from SpiffWorkflow.spiff.serializer.config import SPIFF_CONFIG
from SpiffWorkflow.bpmn.specs.mixins.none_task import NoneTask
from SpiffWorkflow.bpmn.script_engine import TaskDataEnvironment

from SpiffWorkflow.bpmn.specs.event_definitions import NoneEventDefinition
from SpiffWorkflow.bpmn.specs.event_definitions.timer import TimerEventDefinition
from SpiffWorkflow.bpmn.specs.mixins import StartEventMixin
from SpiffWorkflow.spiff.specs import SpiffBpmnTask

from SpiffWorkflow.spiff.parser.event_parsers import StartEventParser
from SpiffWorkflow.bpmn.parser.util import full_tag
from SpiffWorkflow.spiff.serializer.task_spec import SpiffBpmnTaskConverter

from app.serializer import FileSerializer
from app.engine import BpmnEngine
from .curses_handlers import UserTaskHandler, ManualTaskHandler


# Class definitions.
class CustomStartEvent(StartEventMixin, SpiffBpmnTask):

    def __init__(self, wf_spec, bpmn_id, event_definition, **kwargs):

        if isinstance(event_definition, TimerEventDefinition):
            super().__init__(wf_spec, bpmn_id, NoneEventDefinition(), **kwargs)
            self.timer_event = event_definition
        else:
            super().__init__(wf_spec, bpmn_id, event_definition, **kwargs)
            self.timer_event = None


class CustomStartEventConverter(SpiffBpmnTaskConverter):

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct["event_definition"] = self.registry.convert(spec.event_definition)
        dct["timer_event"] = self.registry.convert(spec.timer_event)
        return dct

    def from_dict(self, dct):
        spec = super().from_dict(dct)
        spec.event_definition = self.registry.restore(dct["event_definition"])
        spec.timer_event = self.registry.restore(dct["timer_event"])
        return spec


# Set loggers.
logger = logging.getLogger("spiff_engine")
logger.setLevel(logging.INFO)
spiff_logger = logging.getLogger("spiff")
spiff_logger.setLevel(logging.INFO)


# Configure serializer.
data_directory = os.environ["data_directory"]
FileSerializer.initialize(data_directory)
SPIFF_CONFIG[CustomStartEvent] = CustomStartEventConverter
registry = FileSerializer.configure(SPIFF_CONFIG)
serializer = FileSerializer(data_directory, registry=registry)

# Configure parser.
parser = SpiffBpmnParser()
parser.OVERRIDE_PARSER_CLASSES[full_tag("startEvent")] = (
    StartEventParser,
    CustomStartEvent,
)

# Configure handlers.
handlers = {
    UserTask: UserTaskHandler,
    ManualTask: ManualTaskHandler,
    NoneTask: ManualTaskHandler,
}

# Configure script environment.
script_env = TaskDataEnvironment(safe_globals)

# Create engine.
engine = BpmnEngine(parser, serializer, script_env)
