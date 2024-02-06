from SpiffWorkflow.bpmn.specs.event_definitions import NoneEventDefinition
from SpiffWorkflow.bpmn.specs.event_definitions.timer import TimerEventDefinition
from SpiffWorkflow.bpmn.specs.mixins import StartEventMixin
from SpiffWorkflow.spiff.specs import SpiffBpmnTask

from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer
from SpiffWorkflow.bpmn.serializer.default import EventConverter
from SpiffWorkflow.spiff.serializer.task_spec import SpiffBpmnTaskConverter
from SpiffWorkflow.spiff.serializer import DEFAULT_CONFIG

from SpiffWorkflow.spiff.parser import SpiffBpmnParser
from SpiffWorkflow.spiff.parser.event_parsers import StartEventParser
from SpiffWorkflow.bpmn.parser.util import full_tag

class CustomStartEvent(StartEventMixin, SpiffBpmnTask):

    def __init__(self, wf_spec, bpmn_id, event_definition, **kwargs):

        if isinstance(event_definition, TimerEventDefinition):
            super().__init__(wf_spec, bpmn_id, NoneEventDefinition(), **kwargs)
            self.timer_event = event_definition
        else:
            super().__init__(wf_spec, bpmn_id, event_definition, **kwargs)
            self.timer_event = None

class CustomStartEventConverter(SpiffBpmnTaskConverter):

    def __init__(self, registry):
        super().__init__(CustomStartEvent, registry)

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        if spec.timer_event is not None:
            dct['event_definition'] = self.registry.convert(spec.timer_event)
        else:
            dct['event_definition'] = self.registry.convert(spec.event_definition)
        return dct

DEFAULT_CONFIG['task_specs'].remove(StartEventConverter)
DEFAULT_CONFIG['task_specs'].append(CustomStartEventConverter)
registry = BpmnWorkflowSerializer.configure(DEFAULT_CONFIG)
serializer = BpmnWorkflowSerializer(registry)

parser = SpiffBpmnParser()
parser.OVERRIDE_PARSER_CLASSES[full_tag('startEvent')] = (StartEventParser, CustomStartEvent)
