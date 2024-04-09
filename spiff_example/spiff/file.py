import logging
import datetime

from SpiffWorkflow.spiff.parser import SpiffBpmnParser
from SpiffWorkflow.spiff.specs.defaults import UserTask, ManualTask
from SpiffWorkflow.spiff.serializer.config import SPIFF_CONFIG
from SpiffWorkflow.bpmn.specs.mixins.none_task import NoneTask
from SpiffWorkflow.bpmn.script_engine import TaskDataEnvironment

from ..serializer.file import FileSerializer
from ..engine import BpmnEngine
from .curses_handlers import UserTaskHandler, ManualTaskHandler

logger = logging.getLogger('spiff_engine')
logger.setLevel(logging.INFO)

spiff_logger = logging.getLogger('spiff')
spiff_logger.setLevel(logging.INFO)

dirname = 'wfdata'
FileSerializer.initialize(dirname)

registry = FileSerializer.configure(SPIFF_CONFIG)
serializer = FileSerializer(dirname, registry=registry)

parser = SpiffBpmnParser()

handlers = {
    UserTask: UserTaskHandler,
    ManualTask: ManualTaskHandler,
    NoneTask: ManualTaskHandler,
}

script_env = TaskDataEnvironment({'datetime': datetime })
engine = BpmnEngine(parser, serializer, script_env)
