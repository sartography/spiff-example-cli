import json
import logging
import datetime

from collections import namedtuple

from SpiffWorkflow.spiff.parser.process import SpiffBpmnParser
from SpiffWorkflow.spiff.specs.defaults import UserTask, ManualTask
from SpiffWorkflow.spiff.serializer.config import SPIFF_CONFIG
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow, BpmnSubWorkflow
from SpiffWorkflow.bpmn.specs.bpmn_process_spec import BpmnProcessSpec
from SpiffWorkflow.bpmn.specs.mixins.none_task import NoneTask
from SpiffWorkflow.bpmn.script_engine import PythonScriptEngine, TaskDataEnvironment

from ..serializer.file import FileSerializer
from ..engine import BpmnEngine
from .curses_handlers import UserTaskHandler, ManualTaskHandler

logger = logging.getLogger('spiff_engine')
logger.setLevel(logging.INFO)

ProductInfo = namedtuple('ProductInfo', ['color', 'size', 'style', 'price'])
INVENTORY = {
    'product_a': ProductInfo(False, False, False, 15.00),
    'product_b': ProductInfo(False, False, False, 15.00),
    'product_c': ProductInfo(True, False, False, 25.00),
    'product_d': ProductInfo(True, True, False, 20.00),
    'product_e': ProductInfo(True, True, True, 25.00),
    'product_f': ProductInfo(True, True, True, 30.00),
    'product_g': ProductInfo(False, False, True, 25.00),
}

def lookup_product_info(product_name):
    return INVENTORY[product_name]

def lookup_shipping_cost(shipping_method):
    return 25.00 if shipping_method == 'Overnight' else 5.00

def product_info_to_dict(obj):
    return {
        'color': obj.color,
        'size': obj.size,
        'style': obj.style,
        'price': obj.price,
    }

def product_info_from_dict(dct):
    return ProductInfo(**dct)

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

script_env = TaskDataEnvironment({
    'datetime': datetime,
    'lookup_product_info': lookup_product_info,
    'lookup_shipping_cost': lookup_shipping_cost,
})
script_engine = PythonScriptEngine(script_env)

engine = BpmnEngine(parser, serializer, handlers, script_engine)
