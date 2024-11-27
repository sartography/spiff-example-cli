import json
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

from .product_info import (
    ProductInfo,
    product_info_to_dict,
    product_info_from_dict,
    lookup_product_info,
    lookup_shipping_cost,
)
logger = logging.getLogger('spiff_engine')
logger.setLevel(logging.INFO)

spiff_logger = logging.getLogger('spiff_engine')
spiff_logger.setLevel(logging.INFO)

dirname = 'wfdata'
FileSerializer.initialize(dirname)

registry = FileSerializer.configure(SPIFF_CONFIG)
registry.register(ProductInfo, product_info_to_dict, product_info_from_dict)
serializer = FileSerializer(dirname, registry=registry)

parser = SpiffBpmnParser()

handlers = {
    UserTask: UserTaskHandler,
    ManualTask: ManualTaskHandler,
    NoneTask: ManualTaskHandler,
}

class ServiceTaskEnvironment(TaskDataEnvironment):

    def __init__(self):
        super().__init__({
            'product_info_from_dict': product_info_from_dict,
            'datetime': datetime,
        })

    def call_service(self, task_data, operation_name, operation_params):
        if operation_name == 'lookup_product_info':
            product_info = lookup_product_info(operation_params['product_name']['value'])
            result = product_info_to_dict(product_info)
        elif operation_name == 'lookup_shipping_cost':
            result = lookup_shipping_cost(operation_params['shipping_method']['value'])
        else:
            raise Exception("Unknown Service!")
        return json.dumps(result)

script_env = ServiceTaskEnvironment()

engine = BpmnEngine(parser, serializer, script_env)
