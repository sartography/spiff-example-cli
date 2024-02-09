import sqlite3
import logging

from SpiffWorkflow.camunda.serializer import DEFAULT_CONFIG
from SpiffWorkflow.camunda.parser import CamundaParser
from SpiffWorkflow.camunda.specs import UserTask
from SpiffWorkflow.bpmn.specs.defaults import ManualTask, NoneTask
from SpiffWorkflow.bpmn import BpmnWorkflow
from SpiffWorkflow.bpmn.util.subworkflow import BpmnSubWorkflow
from SpiffWorkflow.bpmn.specs import BpmnProcessSpec

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

DEFAULT_CONFIG[BpmnWorkflow] = WorkflowConverter
DEFAULT_CONFIG[BpmnSubWorkflow] = SubworkflowConverter
DEFAULT_CONFIG[BpmnProcessSpec] = WorkflowSpecConverter

dbname = 'camunda.db'

with sqlite3.connect(dbname) as db:
    SqliteSerializer.initialize(db)

registry = SqliteSerializer.configure(DEFAULT_CONFIG)
serializer = SqliteSerializer(dbname, registry=registry)

parser = CamundaParser()

handlers = {
    UserTask: UserTaskHandler,
    ManualTask: ManualTaskHandler,
    NoneTask: ManualTaskHandler,
}

engine = BpmnEngine(parser, serializer, handlers)
