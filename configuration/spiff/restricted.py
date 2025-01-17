import logging
import os

from RestrictedPython import safe_globals

from SpiffWorkflow.spiff.parser import SpiffBpmnParser
from SpiffWorkflow.spiff.specs.defaults import UserTask, ManualTask
from SpiffWorkflow.spiff.serializer.config import SPIFF_CONFIG
from SpiffWorkflow.bpmn.specs.mixins.none_task import NoneTask
from SpiffWorkflow.bpmn.script_engine import TaskDataEnvironment

from ..serializer import FileSerializer
from ..engine import BpmnEngine
from .curses_handlers import UserTaskHandler, ManualTaskHandler


# Set loggers.
logger = logging.getLogger("spiff_engine")
logger.setLevel(logging.INFO)
spiff_logger = logging.getLogger("spiff")
spiff_logger.setLevel(logging.INFO)

# Configure serializer.
data_directory = os.environ["data_directory"]
FileSerializer.initialize(data_directory)
registry = FileSerializer.configure(SPIFF_CONFIG)
serializer = FileSerializer(data_directory, registry=registry)

# Configure parser.
parser = SpiffBpmnParser()

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
