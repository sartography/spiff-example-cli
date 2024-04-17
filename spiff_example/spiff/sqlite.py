import sqlite3
import logging
import datetime

from SpiffWorkflow.spiff.parser import SpiffBpmnParser
from SpiffWorkflow.spiff.specs.defaults import UserTask, ManualTask
from SpiffWorkflow.spiff.serializer import DEFAULT_CONFIG
from SpiffWorkflow.bpmn import BpmnWorkflow
from SpiffWorkflow.bpmn.util.subworkflow import BpmnSubWorkflow
from SpiffWorkflow.bpmn.specs import BpmnProcessSpec
from SpiffWorkflow.bpmn.specs.mixins import NoneTaskMixin as NoneTask
from SpiffWorkflow.bpmn.script_engine import TaskDataEnvironment

from ..serializer.sqlite import (
    SqliteSerializer,
    WorkflowConverter,
    SubworkflowConverter,
    WorkflowSpecConverter
)
from ..engine import BpmnEngine
from .curses_handlers import UserTaskHandler, ManualTaskHandler

logger = logging.getLogger('spiff_engine')
logger.setLevel(logging.INFO)

spiff_logger = logging.getLogger('spiff')
spiff_logger.setLevel(logging.INFO)

DEFAULT_CONFIG[BpmnWorkflow] = WorkflowConverter
DEFAULT_CONFIG[BpmnSubWorkflow] = SubworkflowConverter
DEFAULT_CONFIG[BpmnProcessSpec] = WorkflowSpecConverter

dbname = 'spiff.db'

with sqlite3.connect(dbname) as db:
    SqliteSerializer.initialize(db)

registry = SqliteSerializer.configure(DEFAULT_CONFIG)
serializer = SqliteSerializer(dbname, registry=registry)

parser = SpiffBpmnParser()

handlers = {
    UserTask: UserTaskHandler,
    ManualTask: ManualTaskHandler,
    NoneTask: ManualTaskHandler,
}

script_env = TaskDataEnvironment({'datetime': datetime })

engine = BpmnEngine(parser, serializer, script_env)
