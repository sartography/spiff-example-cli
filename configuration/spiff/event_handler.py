import logging
import os

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

from ..serializer import FileSerializer
from ..engine import BpmnEngine
from .curses_handlers import UserTaskHandler, ManualTaskHandler


# Class definitions.
class EventHandlingServiceTask(ServiceTask):

    def _execute(self, my_task):
        script_engine = my_task.workflow.script_engine
        # The param also has a type, but I don't need it
        params = dict(
            (name, script_engine.evaluate(my_task, p["value"]))
            for name, p in self.operation_params.items()
        )
        try:
            result = script_engine.call_service(
                my_task, operation_name=self.operation_name, operation_params=params
            )
            my_task.data[self.result_variable] = result
            return True
        except FileNotFoundError:
            event_definition = ErrorEventDefinition("file_not_found", code="1")
            event = BpmnEvent(event_definition, payload=params["filename"])
            my_task.workflow.top_workflow.catch(event)
            return False
        except Exception as exc:
            raise WorkflowTaskException(
                "Service Task execution error", task=my_task, exception=exc
            )


class ServiceTaskEnvironment(TaskDataEnvironment):

    def call_service(self, context, operation_name, operation_params):
        if operation_name == "read_file":
            return open(operation_params["filename"], encoding="utf-8").read()
        raise ValueError("Unknown Service")


# Set loggers.
logger = logging.getLogger("spiff_engine")
logger.setLevel(logging.INFO)
spiff_logger = logging.getLogger("spiff")
spiff_logger.setLevel(logging.INFO)

# Configure serializer.
data_directory = os.environ["data_directory"]
FileSerializer.initialize(data_directory)
SPIFF_CONFIG[EventHandlingServiceTask] = SPIFF_CONFIG.pop(ServiceTask)
registry = FileSerializer.configure(SPIFF_CONFIG)
serializer = FileSerializer(data_directory, registry=registry)

# Configure parser.
parser = SpiffBpmnParser()
parser.OVERRIDE_PARSER_CLASSES[full_tag("serviceTask")] = (
    ServiceTaskParser,
    EventHandlingServiceTask,
)

# Configure handlers.
handlers = {
    UserTask: UserTaskHandler,
    ManualTask: ManualTaskHandler,
    NoneTask: ManualTaskHandler,
}

# Configure script environment.
script_env = ServiceTaskEnvironment()

# Create engine.
engine = BpmnEngine(parser, serializer, script_env)
