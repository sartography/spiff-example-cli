#!/usr/bin/env python

import sys, traceback

from SpiffWorkflow.bpmn.specs.ManualTask import ManualTask
from SpiffWorkflow.bpmn.specs.ScriptTask import ScriptTask
from SpiffWorkflow.bpmn.specs.events.event_types import CatchingEvent, ThrowingEvent

from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser
from SpiffWorkflow.camunda.specs.UserTask import EnumFormField, UserTask

from SpiffWorkflow.camunda.serializer.task_spec_converters import (
    UserTaskConverter,
    StartEventConverter,
    EndEventConverter,
    IntermediateCatchEventConverter,
    IntermediateThrowEventConverter,
    BoundaryEventConverter,
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
    ScriptEngine,
)

def complete_user_task(task):

    display_task(task)
    if task.data is None:
        task.data = {}

    for field in task.task_spec.form.fields:
        if isinstance(field, EnumFormField):
            option_map = dict([ (opt.name, opt.id) for opt in field.options ])
            options = "(" + ', '.join(option_map) + ")"
            prompt = f"{field.label} {options} "
            option = select_option(prompt, option_map.keys())
            response = option_map[option]
        else:
            response = input(f"{field.label} ")
            if field.type == "long":
                response = int(response)
        task.update_data_var(field.id, response)

handlers = {
    ManualTask: complete_manual_task,
    UserTask: complete_user_task,
}

if __name__ == '__main__':

    arg_parser = create_arg_parser()
    args = arg_parser.parse_args()

    try:
        configure_logging(args.log_level, 'data.log')
        serializer = create_serializer([
            UserTaskConverter,
            StartEventConverter,
            EndEventConverter,
            IntermediateCatchEventConverter,
            IntermediateThrowEventConverter,
            BoundaryEventConverter,
            BusinessRuleTaskConverter,
        ], custom_data_converter)
        display_types = (UserTask, ManualTask, ScriptTask, ThrowingEvent, CatchingEvent)
        if args.restore is not None:
            with open(args.restore) as state:
                wf = serializer.deserialize_json(state.read())
                wf.script_engine = ScriptEngine
        else:
            parser = CamundaParser()
            wf = parse_workflow(parser, args.process, args.bpmn, args.dmn)
        run(wf, handlers, serializer, args.step, display_types)
    except Exception as exc:
        sys.stderr.write(traceback.format_exc())
        sys.exit(1)
