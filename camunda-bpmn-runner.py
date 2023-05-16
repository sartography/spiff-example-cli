#!/usr/bin/env python

import sys, traceback

from jinja2 import Template

from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer
from SpiffWorkflow.bpmn.specs.defaults import ManualTask, NoneTask
from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser
from SpiffWorkflow.camunda.specs.user_task import UserTask, EnumFormField
from SpiffWorkflow.camunda.serializer.config import CAMUNDA_SPEC_CONFIG

from SpiffWorkflow.util.deep_merge import DeepMerge

from runner.runner import SimpleBpmnRunner
from runner.shared import create_arg_parser
from runner.product_info import registry
from runner.script_engine import custom_script_engine

parser = CamundaParser()

wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter(CAMUNDA_SPEC_CONFIG)
serializer = BpmnWorkflowSerializer(wf_spec_converter, registry)

def update_data(dct, name, value):
    path = name.split('.')
    current = dct
    for component in path[:-1]:
        if component not in current:
            current[component] = {}
        current = current[component]
    current[path[-1]] = value

def display_task(task):
    print(f'\n{task.task_spec.bpmn_name}')
    if task.task_spec.documentation is not None:
        template = Template(task.task_spec.documentation)
        print(template.render(task.data))

def complete_user_task(task):
    display_task(task)
    dct = {}
    for field in task.task_spec.form.fields:
        if isinstance(field, EnumFormField):
            option_map = dict([ (opt.name, opt.id) for opt in field.options ])
            options = "(" + ', '.join(option_map) + ")"
            prompt = f"{field.label} {options} "
            option = input(prompt)
            while option not in option_map:
                print(f'Invalid selection!')
                option = input(prompt)
            response = option_map[option]
        else:
            response = input(f"{field.label} ")
            if field.type == "long":
                response = int(response)
        update_data(dct, field.id, response)
    DeepMerge.merge(task.data, dct)

def complete_manual_task(task):
    display_task(task)
    input("Press any key to complete task.")

if __name__ == '__main__':

    arg_parser = create_arg_parser()
    args = arg_parser.parse_args()

    handlers = {
        UserTask: complete_user_task,
        ManualTask: complete_manual_task,
        NoneTask: complete_manual_task,
    }

    try:
        runner = SimpleBpmnRunner(parser, serializer, script_engine=custom_script_engine, handlers=handlers)
        if args.restore is not None:
            runner.restore(args.restore)
        else:
            runner.parse(args.process or args.collaboration, args.bpmn, args.dmn, args.collaboration is not None)
        runner.run_workflow(args.step)
    except Exception as exc:
        sys.stderr.write(traceback.format_exc())
        sys.exit(1)
