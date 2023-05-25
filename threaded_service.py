#!/usr/bin/env python

import sys, traceback
import time

from random import randrange
from concurrent.futures import ThreadPoolExecutor

from SpiffWorkflow.bpmn.parser.util import full_tag
from SpiffWorkflow.spiff.parser.process import SpiffBpmnParser, BpmnValidator
from SpiffWorkflow.spiff.parser.task_spec import ServiceTaskParser

from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer
from SpiffWorkflow.spiff.serializer.task_spec import SpiffBpmnTaskConverter, ServiceTaskConverter
from SpiffWorkflow.spiff.serializer.config import SPIFF_SPEC_CONFIG

from SpiffWorkflow.spiff.specs.defaults import ManualTask, NoneTask
from SpiffWorkflow.spiff.specs.spiff_task import SpiffBpmnTask
from SpiffWorkflow.bpmn.specs.mixins.service_task import ServiceTask as ServiceTaskMixin
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.exceptions import WorkflowTaskException

from runner.runner import SimpleBpmnRunner
from runner.shared import create_arg_parser, configure_logging

def wait(seconds, job_id):
    time.sleep(seconds)
    return f'{job_id} slept {seconds} seconds'

class ThreadedScriptEngine(PythonScriptEngine):

    def __init__(self, default_globals=None, scripting_additions=None, environment=None):
        super().__init__(default_globals, scripting_additions, environment)
        self.pool = ThreadPoolExecutor(max_workers=10)
        self.futures = {}

    def update_completed(self):
        finished = [f for f in self.futures if f.done()]
        for future in finished:
            task = self.futures.pop(future)
            result = future.result()
            task.data[task.task_spec._result_variable()] = result
            task.complete()

    def call_service(self, task, operation_name, operation_params):
        if operation_name == 'wait':
            seconds = randrange(1, 30)
            job_id = self.evaluate(task, operation_params['job_id']['value'])
            future = self.pool.submit(wait, seconds, job_id)
            self.futures[future] = task
        else:
            raise ValueError('Unknown service')

class ServiceTask(ServiceTaskMixin, SpiffBpmnTask):

    def __init__(self, wf_spec, name, operation_name, operation_params, result_variable, **kwargs):
        super().__init__(wf_spec, name, **kwargs)
        self.operation_name = operation_name
        self.operation_params = operation_params
        self.result_variable = result_variable

    def _result_variable(self):
        if self.result_variable is not None and len(self.result_variable) > 0:
            return self.result_variable
        escaped_spec_name = self.name.replace('-', '_')
        return f'spiff__{escaped_spec_name}_result'

    def _execute(self, task):
        try:
            task.workflow.script_engine.call_service(task, self.operation_name, self.operation_params)
        except Exception as exc:
            raise WorkflowTaskException('Execution failed', task=task, exception=exc)

class ThreadedServiceTask(SpiffBpmnTaskConverter):

    def __init__(self, registry):
        super().__init__(ServiceTask, registry)

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct['operation_name'] = spec.operation_name
        dct['operation_params'] = spec.operation_params
        dct['result_variable'] = spec.result_variable
        return dct

SPIFF_SPEC_CONFIG['task_specs'].remove(ServiceTaskConverter)
SPIFF_SPEC_CONFIG['task_specs'].append(ThreadedServiceTask)

wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter(SPIFF_SPEC_CONFIG)
serializer = BpmnWorkflowSerializer(wf_spec_converter)

parser = SpiffBpmnParser(validator=BpmnValidator())
parser.OVERRIDE_PARSER_CLASSES[full_tag('serviceTask')] = (ServiceTaskParser, ServiceTask)

custom_script_engine = ThreadedScriptEngine()

class ThreadedBpmnRunner(SimpleBpmnRunner):

    def run_workflow(self, step=False):

        while not self.workflow.is_completed():
            if not step:
                self.advance()
            self.pause(step)
            self.workflow.refresh_waiting_tasks()
            self.workflow.script_engine.update_completed()
        self.at_end()


def complete_manual_task(task):
    print(f'\n{task.task_spec.bpmn_name}')
    input("Press any key to complete task")


if __name__ == '__main__':

    arg_parser = create_arg_parser()
    args = arg_parser.parse_args()

    configure_logging(args.log_level, 'data.log')

    handlers = {
        ManualTask: complete_manual_task,
        NoneTask: complete_manual_task,
    }

    try:
        runner = ThreadedBpmnRunner(parser, serializer, script_engine=custom_script_engine, handlers=handlers)
        if args.restore is not None:
            runner.restore(args.restore)
        else:
            runner.parse(args.process or args.collaboration, args.bpmn, args.dmn, args.collaboration is not None)
        runner.run_workflow(args.step)
    except Exception as exc:
        sys.stderr.write(traceback.format_exc())
        sys.exit(1)
