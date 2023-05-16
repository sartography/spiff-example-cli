#!/usr/bin/env python

import sys, traceback
import json, os

from jinja2 import Template

from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer

from SpiffWorkflow.spiff.parser.process import SpiffBpmnParser, BpmnValidator
from SpiffWorkflow.spiff.serializer.config import SPIFF_SPEC_CONFIG

from SpiffWorkflow.spiff.specs.defaults import UserTask, ManualTask, NoneTask

from runner.runner import SimpleBpmnRunner
from runner.shared import create_arg_parser, configure_logging
from runner.product_info import registry
from runner.script_engine import custom_script_engine

parser = SpiffBpmnParser(validator=BpmnValidator())

wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter(SPIFF_SPEC_CONFIG)
serializer = BpmnWorkflowSerializer(wf_spec_converter, registry)

forms_dir = 'bpmn/spiff/forms'

def display_instructions(task):
    text = task.task_spec.extensions.get('instructionsForEndUser')
    print(f'\n{task.task_spec.bpmn_name}')
    if text is not None:
        template = Template(text)
        print(template.render(task.data))

def complete_user_task(task):
    display_instructions(task)
    filename = task.task_spec.extensions['properties']['formJsonSchemaFilename']
    schema = json.load(open(os.path.join(forms_dir, filename)))
    data = {}
    for field, config in schema['properties'].items():
        if 'oneOf' in config:
            option_map = dict([ (v['title'], v['const']) for v in config['oneOf'] ])
            options = "(" + ', '.join(option_map) + ")"
            prompt = f"{field} {options} "
            option = input(prompt)
            while option not in option_map:
                print(f'Invalid selection!')
                option = input(prompt)
            response = option_map[option]
        else:
            response = input(f"{config['title']} ")
            if config['type'] == 'integer':
                response = int(response)
        data[field] = response
    task.update_data(data)

def complete_manual_task(task):
    display_instructions(task)
    input("Press any key to complete task")


if __name__ == '__main__':

    arg_parser = create_arg_parser()
    args = arg_parser.parse_args()

    configure_logging(args.log_level, 'data.log')

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
