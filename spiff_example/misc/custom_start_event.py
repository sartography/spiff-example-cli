import logging

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
from SpiffWorkflow.bpmn.serializer.default import EventConverter
from SpiffWorkflow.spiff.serializer.task_spec import SpiffBpmnTaskConverter

from ..serializer.file import FileSerializer
from ..engine import BpmnEngine
from .curses_handlers import UserTaskHandler, ManualTaskHandler

logger = logging.getLogger('spiff_engine')
logger.setLevel(logging.INFO)

spiff_logger = logging.getLogger('spiff')
spiff_logger.setLevel(logging.INFO)

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
        dct['event_definition'] = self.registry.convert(spec.event_definition)
        dct['timer_event'] = self.registry.convert(spec.timer_event)
        return dct

    def from_dict(self, dct):
        spec = super().from_dict(dct)
        spec.event_definition = self.registry.restore(dct['event_definition'])
        spec.timer_event = self.registry.restore(dct['timer_event'])
        return spec

dirname = 'wfdata'
FileSerializer.initialize(dirname)

SPIFF_CONFIG[CustomStartEvent] = CustomStartEventConverter

registry = FileSerializer.configure(SPIFF_CONFIG)
serializer = FileSerializer(dirname, registry=registry)

parser = SpiffBpmnParser()
parser.OVERRIDE_PARSER_CLASSES[full_tag('startEvent')] = (StartEventParser, CustomStartEvent)

handlers = {
    UserTask: UserTaskHandler,
    ManualTask: ManualTaskHandler,
    NoneTask: ManualTaskHandler,
}

script_env = TaskDataEnvironment(safe_globals)

engine = BpmnEngine(parser, serializer, script_env)

