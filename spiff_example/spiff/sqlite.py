import sqlite3
import logging
import datetime

from SpiffWorkflow.spiff.parser.process import SpiffBpmnParser
from SpiffWorkflow.spiff.specs.defaults import UserTask, ManualTask
from SpiffWorkflow.spiff.serializer.config import SPIFF_CONFIG
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow, BpmnSubWorkflow
from SpiffWorkflow.bpmn.specs.bpmn_process_spec import BpmnProcessSpec
from SpiffWorkflow.bpmn.specs.mixins.none_task import NoneTask
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.PythonScriptEngineEnvironment import TaskDataEnvironment

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

SPIFF_CONFIG[BpmnWorkflow] = WorkflowConverter
SPIFF_CONFIG[BpmnSubWorkflow] = SubworkflowConverter
SPIFF_CONFIG[BpmnProcessSpec] = WorkflowSpecConverter

dbname = 'spiff.db'

with sqlite3.connect(dbname) as db:
    SqliteSerializer.initialize(db)

registry = SqliteSerializer.configure(SPIFF_CONFIG)
serializer = SqliteSerializer(dbname, registry=registry)

parser = SpiffBpmnParser()

handlers = {
    UserTask: UserTaskHandler,
    ManualTask: ManualTaskHandler,
    NoneTask: ManualTaskHandler,
}

script_env = TaskDataEnvironment({'datetime': datetime })
script_engine = PythonScriptEngine(script_env)

engine = BpmnEngine(parser, serializer, handlers, script_engine)
