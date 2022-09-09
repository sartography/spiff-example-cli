#!/usr/bin/env python
"""This module provides basic understanding on how to use SpiffWorkflow.

Refer to the BPMN in this repository and the comments below.
"""

# Standard Library
import argparse
import json
import sys
import traceback

# Dependencies
from jinja2 import Template
from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer
from SpiffWorkflow.bpmn.specs.events.event_types import CatchingEvent, ThrowingEvent
from SpiffWorkflow.bpmn.specs.ManualTask import ManualTask
from SpiffWorkflow.bpmn.specs.ScriptTask import ScriptTask
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser
from SpiffWorkflow.camunda.serializer.task_spec_converters import UserTaskConverter
from SpiffWorkflow.camunda.specs.UserTask import EnumFormField, UserTask
from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from SpiffWorkflow.dmn.serializer.task_spec_converters import BusinessRuleTaskConverter
from SpiffWorkflow.task import TaskState

# Local Modules
from .custom_script_engine import CustomScriptEngine

wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter(
    [UserTaskConverter, BusinessRuleTaskConverter]
)
serializer = BpmnWorkflowSerializer(wf_spec_converter)


class Parser(BpmnDmnParser):
    """Customized Parser for this example."""

    OVERRIDE_PARSER_CLASSES = BpmnDmnParser.OVERRIDE_PARSER_CLASSES
    OVERRIDE_PARSER_CLASSES.update(CamundaParser.OVERRIDE_PARSER_CLASSES)


def parse(process, bpmn_files, dmn_files):
    """
    Parse the provided files based on the process to generate a Workflow.

    :param process: Name of the process to parse.
    :type process: str
    :param bpmn_files: BPMN files to be added to the parser.
    :type bpmn_files: list[str]
    :param dmn_files: DMN files to be added to the parser.
    :type dmn_files: list[str]
    :return: Workflow object of the process.
    :rtype: SpiffWorkflow.bpmn.workflow.BpmnWorkflow
    """
    my_parser = Parser()
    my_parser.add_bpmn_files(bpmn_files)
    if dmn_files:
        my_parser.add_dmn_files(dmn_files)
    return BpmnWorkflow(my_parser.get_spec(process), script_engine=CustomScriptEngine)


def select_option(prompt, options):
    """
    Request the user to select an option from the list.

    :param prompt: Text to show the user to request an option.
    :type prompt: str
    :param options: List of options to select from.
    :type options: _dict_keys
    :return: The selected option.
    :rtype: str
    """
    option = input(prompt)
    while option not in options:
        print("Invalid selection")
        option = input(prompt)
    return option


def display_task(task):
    """
    Display the task description and documentation.

    :param task: Task to show the information.
    :type task: SpiffWorkflow.task.Task
    """
    print(f"\n{task.task_spec.description}")
    if task.task_spec.documentation is not None:
        template = Template(task.task_spec.documentation)
        print(template.render(task.data))


def format_task(task, include_state=True):
    """
    Convert a task in a string format.

    :param task: Task to convert.
    :type task: SpiffWorkflow.task.Task
    :param include_state: Whether to include the state of the task or not.
    :type include_state: bool
    :return: Task short information.
    :rtype: str
    """
    if hasattr(task.task_spec, "lane") and task.task_spec.lane is not None:
        lane = f"[{task.task_spec.lane}]"
    else:
        lane = ""
    task_state = f"[{task.get_state_name()}]" if include_state else ""
    return f"{lane} {task.task_spec.description} ({task.task_spec.name}) {task_state}"


def complete_user_task(task):
    """
    Process a user task to completion.

    :param task: Task to complete.
    :type task: SpiffWorkflow.task.Task
    """
    display_task(task)
    if task.data is None:
        task.data = {}

    for field in task.task_spec.form.fields:
        if isinstance(field, EnumFormField):
            option_map = {opt.name: opt.id for opt in field.options}
            options = "(" + ", ".join(option_map) + ")"
            prompt = f"{field.label} {options} "
            option = select_option(prompt, option_map.keys())
            response = option_map[option]
        else:
            response = input(f"{field.label} ")
            if field.type == "long":
                response = int(response)
        task.update_data_var(field.id, response)


def complete_manual_task(task):
    """
    Process a manual task to completion.

    :param task: Task to complete.
    :type task: SpiffWorkflow.task.Task
    """
    display_task(task)
    input("Press any key to mark task complete")


def print_state(workflow):
    """
    Print the current state of the workflow.

    :param workflow: Workflow to show the state of.
    :type workflow: SpiffWorkflow.bpmn.workflow.BpmnWorkflow
    """
    task = workflow.last_task
    print("\nLast Task")
    print(format_task(task))
    print(json.dumps(task.data, indent=2, separators=[", ", ": "]))

    display_types = (UserTask, ManualTask, ScriptTask, ThrowingEvent, CatchingEvent)
    all_tasks = [
        task
        for task in workflow.get_tasks()
        if isinstance(task.task_spec, display_types)
    ]
    upcoming_tasks = [
        task for task in all_tasks if task.state in [TaskState.READY, TaskState.WAITING]
    ]

    print("\nUpcoming Tasks")
    for _, task in enumerate(upcoming_tasks):
        print(format_task(task))

    if input("\nShow all tasks? ").lower() == "y":
        for _, task in enumerate(all_tasks):
            print(format_task(task))


def run(workflow, step):
    """
    Run the workflow, step by step.

    :param workflow: Workflow to run.
    :type workflow: SpiffWorkflow.bpmn.workflow.BpmnWorkflow
    :param step: Showing the steps or not?
    :type step: bool
    """
    workflow.do_engine_steps()

    while not workflow.is_completed():

        ready_tasks = workflow.get_ready_user_tasks()
        options = {}
        print()
        for idx, task in enumerate(ready_tasks):
            option = format_task(task, False)
            options[str(idx + 1)] = task
            print(f"{idx + 1}. {option}")

        selected = None
        while selected not in options and selected not in ["", "D", "d"]:
            selected = input(
                "Select task to complete, enter to wait, "
                "or D to dump the workflow state: "
            )

        if selected.lower() == "d":
            filename = input("Enter filename: ")
            workflow_state = serializer.serialize_json(workflow)
            with open(filename, "w", encoding="utf-8") as dump:
                dump.write(workflow_state)
        elif selected != "":
            next_task = options[selected]
            if isinstance(next_task.task_spec, UserTask):
                complete_user_task(next_task)
                next_task.complete()
            elif isinstance(next_task.task_spec, ManualTask):
                complete_manual_task(next_task)
                next_task.complete()
            else:
                next_task.complete()

        workflow.refresh_waiting_tasks()
        workflow.do_engine_steps()
        if step:
            print_state(workflow)

    print("\nWorkflow Data")
    print(json.dumps(workflow.data, indent=2, separators=[", ", ": "]))


if __name__ == "__main__":

    parser = argparse.ArgumentParser("Simple BPMN runner")
    parser.add_argument(
        "-p", "--process", dest="process", help="The top-level BPMN Process ID"
    )
    parser.add_argument(
        "-b", "--bpmn", dest="bpmn", nargs="+", help="BPMN files to load"
    )
    parser.add_argument("-d", "--dmn", dest="dmn", nargs="*", help="DMN files to load")
    parser.add_argument(
        "-r",
        "--restore",
        dest="restore",
        metavar="FILE",
        help="Restore state from %(metavar)s",
    )
    parser.add_argument(
        "-s",
        "--step",
        dest="step",
        action="store_true",
        help="Display state after each step",
    )
    args = parser.parse_args()

    try:
        if args.restore is not None:
            with open(args.restore, encoding="utf-8") as state:
                wf = serializer.deserialize_json(state.read())
                # We need to reset the script engine to the workflow.
                # See https://github.com/sartography/spiff-example-cli/issues/13
                wf.script_engine = CustomScriptEngine
        else:
            wf = parse(args.process, args.bpmn, args.dmn)
        run(wf, args.step)
    except Exception as exc:  # pylint: disable=broad-except
        sys.stderr.write(traceback.format_exc())
        sys.exit(1)
