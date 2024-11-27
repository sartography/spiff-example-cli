import logging

from SpiffWorkflow.spiff.parser import SpiffBpmnParser
from SpiffWorkflow.spiff.specs.defaults import UserTask, ManualTask, ServiceTask
from SpiffWorkflow.spiff.serializer.config import SPIFF_CONFIG
from SpiffWorkflow.bpmn.specs.mixins.none_task import NoneTask
from SpiffWorkflow.bpmn.script_engine import TaskDataEnvironment

from SpiffWorkflow.spiff.specs.event_definitions import ErrorEventDefinition
from SpiffWorkflow.spiff.parser.task_spec import ServiceTaskParser
from SpiffWorkflow.bpmn.parser.util import full_tag
from SpiffWorkflow.bpmn.exceptions import WorkflowTaskException
from SpiffWorkflow.bpmn import BpmnEvent

from ..serializer.file import FileSerializer
from ..engine import BpmnEngine, Instance
from .curses_handlers import UserTaskHandler, ManualTaskHandler

logger = logging.getLogger('spiff_engine')
logger.setLevel(logging.INFO)

spiff_logger = logging.getLogger('spiff') 
spiff_logger.setLevel(logging.INFO)

dirname = 'wfdata' 
FileSerializer.initialize(dirname)

handlers = {
    UserTask: UserTaskHandler,
    ManualTask: ManualTaskHandler,
    NoneTask: ManualTaskHandler,
}

class EventHandlingServiceTask(ServiceTask):

    def _execute(self, my_task):
        script_engine = my_task.workflow.script_engine
        # The param also has a type, but I don't need it
        params = dict((name, script_engine.evaluate(my_task, p['value'])) for name, p in self.operation_params.items())
        try:
            result = script_engine.call_service(
                my_task,
                operation_name=self.operation_name,
                operation_params=params
            )
            my_task.data[self.result_variable] = result
            return True
        except FileNotFoundError as exc:
            event_definition = ErrorEventDefinition('file_not_found', code='1')
            event = BpmnEvent(event_definition, payload=params['filename'])
            my_task.workflow.top_workflow.catch(event)
            return False
        except Exception as exc:
            raise WorkflowTaskException('Service Task execution error', task=my_task, exception=exc)


class ServiceTaskEnvironment(TaskDataEnvironment):

    def call_service(self, context, operation_name, operation_params):
        if operation_name == 'read_file':
            return open(operation_params['filename']).read()
        else:
            raise ValueError('Unknown Service')


parser = SpiffBpmnParser()
parser.OVERRIDE_PARSER_CLASSES[full_tag('serviceTask')] = (ServiceTaskParser, EventHandlingServiceTask)

SPIFF_CONFIG[EventHandlingServiceTask] = SPIFF_CONFIG.pop(ServiceTask)
registry = FileSerializer.configure(SPIFF_CONFIG)
serializer = FileSerializer(dirname, registry=registry)

script_env = ServiceTaskEnvironment()

engine = BpmnEngine(parser, serializer, script_env)
