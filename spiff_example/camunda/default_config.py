import sqlite3
import logging

from SpiffWorkflow.camunda.serializer.config import CAMUNDA_CONFIG
from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser
from SpiffWorkflow.camunda.specs.user_task import UserTask
from SpiffWorkflow.bpmn.specs.defaults import ManualTask, NoneTask
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow, BpmnSubWorkflow
from SpiffWorkflow.bpmn.specs.bpmn_process_spec import BpmnProcessSpec

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

CAMUNDA_CONFIG[BpmnWorkflow] = WorkflowConverter
CAMUNDA_CONFIG[BpmnSubWorkflow] = SubworkflowConverter
CAMUNDA_CONFIG[BpmnProcessSpec] = WorkflowSpecConverter

dbname = 'camunda.db'

with sqlite3.connect(dbname) as db:
    SqliteSerializer.initialize(db)

registry = SqliteSerializer.configure(CAMUNDA_CONFIG)
serializer = SqliteSerializer(dbname, registry=registry)

parser = CamundaParser()

handlers = {
    UserTask: UserTaskHandler,
    ManualTask: ManualTaskHandler,
    NoneTask: ManualTaskHandler,
}

engine = BpmnEngine(parser, serializer, handlers)
