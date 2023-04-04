import argparse
import logging
import json

from jinja2 import Template

from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer

from custom_script_engine import CustomScriptEngine as ScriptEngine

def create_arg_parser():

    parser = argparse.ArgumentParser('Simple BPMN runner')
    parser.add_argument('-p', '--process', dest='process', help='The top-level BPMN Process ID')
    parser.add_argument('-b', '--bpmn', dest='bpmn', nargs='+', help='BPMN files to load')
    parser.add_argument('-d', '--dmn', dest='dmn', nargs='*', help='DMN files to load')
    parser.add_argument('-r', '--restore', dest='restore', metavar='FILE',  help='Restore state from %(metavar)s')
    parser.add_argument('-s', '--step', dest='step', action='store_true', help='Display state after each step')
    parser.add_argument('-l', '--log-level', dest='log_level', metavar='LEVEL', help='Use log level %(metavar)s', default='WARN')
    return parser

def configure_logging(log_level, filename):

    logging.addLevelName(15, 'DATA_LOG')

    def get_logger(name, fmt):
        logger = logging.getLogger(name)
        formatter = logging.Formatter(fmt)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    spiff_log = get_logger('spiff', '%(asctime)s [%(name)s:%(levelname)s] (%(workflow)s:%(task_spec)s) %(message)s')
    metrics_log = get_logger('spiff.metrics', '%(asctime)s [%(name)s:%(levelname)s] (%(task_type)s:%(action)s) %(elapsed)2.4f')
    metrics_log.propagate = False

    def log_updates(rec):
        with open(filename, 'a') as fh:
            fh.write(json.dumps({
                'task_id': str(rec.task_id),
                'timestamp': rec.created,
                'data': rec.data,
            }))
            fh.write('\n')
        return 0

    data_log = logging.getLogger('spiff.data')
    data_log.addFilter(log_updates)
    spiff_log.setLevel(log_level)

def create_serializer(task_types, data_converter=None):

    wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter(task_types)
    serializer = BpmnWorkflowSerializer(wf_spec_converter, data_converter)
    serializer.VERSION = 1.1
    return serializer

def parse_workflow(parser, process, bpmn_files, dmn_files, load_all=True):

    parser.add_bpmn_files(bpmn_files)
    if dmn_files:
        parser.add_dmn_files(dmn_files)
    top_level = parser.get_spec(process)
    if load_all:
        subprocesses = parser.find_all_specs()
    else:
        subprocesses = parser.get_subprocess_specs(process)
    return BpmnWorkflow(top_level, subprocesses, script_engine=ScriptEngine)

def select_option(prompt, options):

    option = input(prompt)
    while option not in options:
        print("Invalid selection")
        option = input(prompt)
    return option

def display_task(task):

    print(f'\n{task.task_spec.description}')
    if task.task_spec.documentation is not None:
        template = Template(task.task_spec.documentation)
        print(template.render(task.data))

def format_task(task, include_state=True):
    
    if hasattr(task.task_spec, 'lane') and task.task_spec.lane is not None:
        lane = f'[{task.task_spec.lane}]' 
    else:
        lane = ''
    state = f'[{task.get_state_name()}]' if include_state else ''
    return f'{lane} {task.task_spec.description} ({task.task_spec.name}) {state}'

def complete_manual_task(task):

    display_task(task)
    input("Press any key to mark task complete")

def print_state(workflow, task, display_types):

    print('\nLast Task')
    print(format_task(task))
    print(json.dumps(task.data, indent=2, separators=[ ', ', ': ' ]))

    all_tasks = [ task for task in workflow.get_tasks() if isinstance(task.task_spec, display_types) ]
    upcoming_tasks = [ task for task in all_tasks if task.state in [TaskState.READY, TaskState.WAITING] ]

    print('\nUpcoming Tasks')
    for idx, task in enumerate(upcoming_tasks):
        print(format_task(task))

    if input('\nShow all tasks? ').lower() == 'y':
        for idx, task in enumerate(all_tasks):
            print(format_task(task))

def run(workflow, task_handlers, serializer, step, display_types):

    workflow.do_engine_steps()

    while not workflow.is_completed():

        ready_tasks = workflow.get_ready_user_tasks()
        options = { }
        print()
        for idx, task in enumerate(ready_tasks):
            option = format_task(task, False)
            options[str(idx + 1)] = task
            print(f'{idx + 1}. {option}')

        selected = None
        while selected not in options and selected not in ['', 'D', 'd']:
            selected = input('Select task to complete, enter to wait, or D to dump the workflow state: ')

        if selected.lower() == 'd':
            filename = input('Enter filename: ')
            state = serializer.serialize_json(workflow)
            with open(filename, 'w') as dump:
                dump.write(state)
        elif selected != '':
            next_task = options[selected]
            handler = task_handlers.get(type(next_task.task_spec))
            if handler is not None:
                handler(next_task)
            next_task.complete()

        workflow.refresh_waiting_tasks()
        workflow.do_engine_steps()
        if step:
            print_state(workflow, next_task, display_types)

    print('\nWorkflow Data')
    print(json.dumps(workflow.data, indent=2, separators=[ ', ', ': ' ]))
