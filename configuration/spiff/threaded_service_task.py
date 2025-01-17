import logging
import os
import time

from random import randrange
from concurrent.futures import ThreadPoolExecutor

from SpiffWorkflow.spiff.parser import SpiffBpmnParser
from SpiffWorkflow.spiff.specs.defaults import UserTask, ManualTask, ServiceTask
from SpiffWorkflow.spiff.serializer.config import SPIFF_CONFIG
from SpiffWorkflow.bpmn.specs.mixins.none_task import NoneTask
from SpiffWorkflow.bpmn.script_engine import TaskDataEnvironment

from SpiffWorkflow.spiff.parser.task_spec import ServiceTaskParser
from SpiffWorkflow.bpmn.parser.util import full_tag
from SpiffWorkflow.bpmn.exceptions import WorkflowTaskException

from ..serializer import FileSerializer
from ..engine import BpmnEngine, Instance
from .curses_handlers import UserTaskHandler, ManualTaskHandler


# Function definitions.
def wait(seconds, job_id):
    time.sleep(seconds)
    return f"{job_id} slept {seconds} seconds"


# Class definitions.
class ServiceTaskEnvironment(TaskDataEnvironment):

    def __init__(self):
        super().__init__()
        self.pool = ThreadPoolExecutor(max_workers=10)
        self.futures = {}

    def call_service(self, context, operation_name, operation_params):
        if operation_name == "wait":
            seconds = randrange(1, 30)
            return self.pool.submit(wait, seconds, operation_params["job_id"])

        raise ValueError("Unknown Service!")


class ThreadedServiceTask(ServiceTask):

    def _execute(self, my_task):
        script_engine = my_task.workflow.script_engine
        params = dict(
            (name, script_engine.evaluate(my_task, p["value"]))
            for name, p in self.operation_params.items()
        )
        try:
            future = script_engine.call_service(
                my_task,
                operation_name=self.operation_name,
                operation_params=params,
            )
            script_engine.environment.futures[future] = my_task
        except Exception as exc:
            raise WorkflowTaskException(
                "Service Task execution error", task=my_task, exception=exc
            )


class ThreadInstance(Instance):

    def update_completed_futures(self):
        futures = self.workflow.script_engine.environment.futures
        finished = [f for f in futures if f.done()]
        for future in finished:
            task = futures.pop(future)
            result = future.result()
            task.data[task.task_spec.result_variable] = result
            task.complete()

    def run_ready_events(self):
        self.update_completed_futures()
        super().run_ready_events()


# Set loggers.
logger = logging.getLogger("spiff_engine")
logger.setLevel(logging.INFO)
spiff_logger = logging.getLogger("spiff")
spiff_logger.setLevel(logging.INFO)

# Configure serializer.
data_directory = os.environ["data_directory"]
FileSerializer.initialize(data_directory)
SPIFF_CONFIG[ThreadedServiceTask] = SPIFF_CONFIG.pop(ServiceTask)
registry = FileSerializer.configure(SPIFF_CONFIG)
serializer = FileSerializer(data_directory, registry=registry)

# Configure parser.
parser = SpiffBpmnParser()
parser.OVERRIDE_PARSER_CLASSES[full_tag("serviceTask")] = (
    ServiceTaskParser,
    ThreadedServiceTask,
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
engine = BpmnEngine(parser, serializer, script_env, instance_cls=ThreadInstance)
