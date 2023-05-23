from SpiffWorkflow.bpmn.specs.event_definitions import TimerEventDefinition, NoneEventDefinition
from SpiffWorkflow.bpmn.specs.mixins.events.start_event import StartEvent
from SpiffWorkflow.spiff.specs.spiff_task import SpiffBpmnTask

from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer
from SpiffWorkflow.bpmn.serializer.task_spec import StartEventConverter
from SpiffWorkflow.spiff.serializer.task_spec import SpiffBpmnTaskConverter
from SpiffWorkflow.spiff.serializer.config import SPIFF_SPEC_CONFIG

from SpiffWorkflow.spiff.parser.event_parsers import StartEventParser
from SpiffWorkflow.spiff.parser.process import SpiffBpmnParser
from SpiffWorkflow.bpmn.parser.util import full_tag

class CustomStartEvent(StartEvent, SpiffBpmnTask):

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

    
SPIFF_SPEC_CONFIG['task_specs'].remove(StartEventConverter)
SPIFF_SPEC_CONFIG['task_specs'].append(CustomStartEventConverter)

wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter(SPIFF_SPEC_CONFIG)
serializer = BpmnWorkflowSerializer(wf_spec_converter)


parser = SpiffBpmnParser()
parser.OVERRIDE_PARSER_CLASSES[full_tag('startEvent')] = (StartEventParser, CustomStartEvent)

