import logging
import datetime

from SpiffWorkflow.spiff.parser.process import SpiffBpmnParser
from SpiffWorkflow.spiff.specs.defaults import UserTask, ManualTask
from SpiffWorkflow.spiff.serializer.config import SPIFF_CONFIG
from SpiffWorkflow.bpmn.specs.mixins.none_task import NoneTask
from SpiffWorkflow.bpmn.script_engine import TaskDataEnvironment

from ..serializer import FileSerializer
from ..engine import BpmnEngine
from .curses_handlers import UserTaskHandler, ManualTaskHandler

from .product_info import (
    ProductInfo,
    product_info_to_dict,
    product_info_from_dict,
    lookup_product_info,
    lookup_shipping_cost,
)

DIRNAME = "wfdata"

logger = logging.getLogger("spiff_engine")
logger.setLevel(logging.INFO)

spiff_logger = logging.getLogger("spiff")
spiff_logger.setLevel(logging.INFO)

FileSerializer.initialize(DIRNAME)

registry = FileSerializer.configure(SPIFF_CONFIG)
registry.register(ProductInfo, product_info_to_dict, product_info_from_dict)

serializer = FileSerializer(DIRNAME, registry=registry)

parser = SpiffBpmnParser()

handlers = {
    UserTask: UserTaskHandler,
    ManualTask: ManualTaskHandler,
    NoneTask: ManualTaskHandler,
}

script_env = TaskDataEnvironment(
    {
        "datetime": datetime,
        "lookup_product_info": lookup_product_info,
        "lookup_shipping_cost": lookup_shipping_cost,
    }
)
engine = BpmnEngine(parser, serializer, script_env)
