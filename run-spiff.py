#!/usr/bin/env python

import sys, traceback
import os
import json

from SpiffWorkflow.bpmn.specs.ManualTask import ManualTask
from SpiffWorkflow.bpmn.specs.ScriptTask import ScriptTask
from SpiffWorkflow.bpmn.specs.events.event_types import CatchingEvent, ThrowingEvent

from SpiffWorkflow.spiff.parser.process import SpiffBpmnParser
from SpiffWorkflow.spiff.specs.user_task import UserTask

from SpiffWorkflow.spiff.serializer.task_spec_converters import (
    NoneTaskConverter,
    ManualTaskConverter,
    UserTaskConverter,
    ScriptTaskConverter,
    ServiceTaskConverter,
    SubWorkflowTaskConverter,
    TransactionSubprocessConverter,
    CallActivityTaskConverter,
    StartEventConverter,
    EndEventConverter,
    IntermediateCatchEventConverter,
    IntermediateThrowEventConverter,
    BoundaryEventConverter,
    SendTaskConverter,
    ReceiveTaskConverter,
)
from SpiffWorkflow.dmn.serializer.task_spec_converters import BusinessRuleTaskConverter

from engine.custom_script import custom_data_converter

from utils import (
    create_arg_parser,
    configure_logging,
    create_serializer,
    parse_workflow,
    select_option,
    display_task,
    complete_manual_task,
    run,
    ScriptEngine
)

forms_dir = 'bpmn-spiff/forms'

def complete_user_task(task):

    display_task(task)
    if task.data is None:
        task.data = {}

    filename = task.task_spec.extensions['properties']['formJsonSchemaFilename']
    schema = json.load(open(os.path.join(forms_dir, filename)))
    for field, config in schema['properties'].items():
        if 'oneOf' in config:
            option_map = dict([ (v['title'], v['const']) for v in config['oneOf'] ])
            options = "(" + ', '.join(option_map) + ")"
            prompt = f"{field} {options} "
            option = select_option(prompt, option_map.keys())
            response = option_map[option]
        else:
            response = input(f"{config['title']} ")
            if config['type'] == 'integer':
                response = int(response)
        task.data[field] = response

handlers = {
    ManualTask: complete_manual_task,
    UserTask: complete_user_task,
}

if __name__ == '__main__':

    arg_parser = create_arg_parser()
    args = arg_parser.parse_args()

    try:
        serializer = create_serializer([
            UserTaskConverter,
            ManualTaskConverter,
            UserTaskConverter,
            ScriptTaskConverter,
            ServiceTaskConverter,
            SubWorkflowTaskConverter,
            TransactionSubprocessConverter,
            CallActivityTaskConverter,
            StartEventConverter,
            EndEventConverter,
            IntermediateCatchEventConverter,
            IntermediateThrowEventConverter,
            BoundaryEventConverter,
            SendTaskConverter,
            ReceiveTaskConverter,
            BusinessRuleTaskConverter,
            IntermediateCatchEventConverter,
            IntermediateThrowEventConverter,
        ], custom_data_converter)

        display_types = (UserTask, ManualTask, ScriptTask, ThrowingEvent, CatchingEvent)
        if args.restore is not None:
            with open(args.restore) as state:
                wf = serializer.deserialize_json(state.read())
                wf.script_engine = ScriptEngine
        else:
            parser = SpiffBpmnParser()
            wf = parse_workflow(parser, args.process, args.bpmn, args.dmn)
            wf.data['b_set_in_workflow_data'] = []
        run(wf, handlers, serializer, args.step, display_types)

    except Exception as exc:
        sys.stderr.write(traceback.format_exc())
        sys.exit(1)
