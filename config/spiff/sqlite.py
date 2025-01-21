import datetime
import logging
import os
import sqlite3

from SpiffWorkflow.spiff.parser import SpiffBpmnParser
from SpiffWorkflow.spiff.specs.defaults import UserTask, ManualTask
from SpiffWorkflow.spiff.serializer import DEFAULT_CONFIG
from SpiffWorkflow.bpmn import BpmnWorkflow
from SpiffWorkflow.bpmn.util.subworkflow import BpmnSubWorkflow
from SpiffWorkflow.bpmn.specs import BpmnProcessSpec
from SpiffWorkflow.bpmn.specs.mixins import NoneTaskMixin as NoneTask
from SpiffWorkflow.bpmn.script_engine import TaskDataEnvironment

from app.serializer import (
    SqliteSerializer,
    WorkflowConverter,
    SubworkflowConverter,
    WorkflowSpecConverter,
)
from app.engine import BpmnEngine
from .curses_handlers import UserTaskHandler, ManualTaskHandler


# Set loggers.
logger = logging.getLogger("spiff_engine")
logger.setLevel(logging.INFO)
spiff_logger = logging.getLogger("spiff")
spiff_logger.setLevel(logging.INFO)

DEFAULT_CONFIG[BpmnWorkflow] = WorkflowConverter
DEFAULT_CONFIG[BpmnSubWorkflow] = SubworkflowConverter
DEFAULT_CONFIG[BpmnProcessSpec] = WorkflowSpecConverter

# Configure serializer.
data_directory = os.environ["data_directory"]
os.makedirs(data_directory, exist_ok=True)
db_path = os.path.join(data_directory, "spiff.db")
with sqlite3.connect(db_path) as db:
    SqliteSerializer.initialize(db)
registry = SqliteSerializer.configure(DEFAULT_CONFIG)
serializer = SqliteSerializer(db_path, registry=registry)

# Configure parser.
parser = SpiffBpmnParser()

# Configure handlers.
handlers = {
    UserTask: UserTaskHandler,
    ManualTask: ManualTaskHandler,
    NoneTask: ManualTaskHandler,
}

# Configure script environment.
script_env = TaskDataEnvironment({"datetime": datetime})

# Create engine.
engine = BpmnEngine(parser, serializer, script_env)
