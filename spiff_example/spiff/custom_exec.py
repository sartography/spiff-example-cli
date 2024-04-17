import logging
import json
import os, subprocess

from SpiffWorkflow.spiff.parser import SpiffBpmnParser
from SpiffWorkflow.spiff.specs.defaults import UserTask, ManualTask
from SpiffWorkflow.spiff.serializer.config import SPIFF_CONFIG
from SpiffWorkflow.bpmn.specs.mixins.none_task import NoneTask
from SpiffWorkflow.bpmn.script_engine.python_environment import BasePythonScriptEngineEnvironment
from SpiffWorkflow.util.deep_merge import DeepMerge

from ..serializer.file import FileSerializer
from ..engine import BpmnEngine
from .curses_handlers import UserTaskHandler, ManualTaskHandler

from .product_info import (
    ProductInfo,
    lookup_product_info,
    lookup_shipping_cost,
    product_info_to_dict,
    product_info_from_dict,
)

logger = logging.getLogger('spiff_engine')
logger.setLevel(logging.INFO)

spiff_logger = logging.getLogger('spiff')
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

class SubprocessScriptingEnvironment(BasePythonScriptEngineEnvironment):

    def __init__(self, executable, serializer, **kwargs):
        super().__init__(**kwargs)
        self.executable = executable
        self.serializer = serializer

    def evaluate(self, expression, context, external_context=None):
        output = self.run(['eval', expression], context, external_context)
        return self.parse_output(output)

    def execute(self, script, context, external_context=None):
        output = self.run(['exec', script], context, external_context)
        DeepMerge.merge(context, self.parse_output(output))
        return True

    def run(self, args, context, external_context):
        cmd = ['python', '-m', self.executable] + args + ['-c', json.dumps(registry.convert(context))]
        if external_context is not None:
            cmd.extend(['-x', json.dumps(registry.convert(external_context))])
        return subprocess.run(cmd, capture_output=True)

    def parse_output(self, output):
        if output.stderr:
            raise Exception(output.stderr.decode('utf-8'))
        return registry.restore(json.loads(output.stdout))

executable = 'spiff_example.spiff.subprocess_engine'
script_env = SubprocessScriptingEnvironment(executable, serializer)

engine = BpmnEngine(parser, serializer, script_env)

