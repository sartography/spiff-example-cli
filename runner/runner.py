import json

from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow


class SimpleBpmnRunner:

    def __init__(self, parser, serializer, script_engine=None, handlers=None):

        self.parser = parser
        self.serializer = serializer
        self.script_engine = script_engine
        self.handlers = handlers or {}
        self.workflow = None

    def parse(self, name, bpmn_files, dmn_files=None, collaboration=False):

        self.parser.add_bpmn_files(bpmn_files)
        if dmn_files:
            self.parser.add_dmn_files(dmn_files)

        if collaboration:
            top_level, subprocesses = self.parser.get_collaboration(name)
        else:
            top_level = self.parser.get_spec(name)
            subprocesses = self.parser.get_subprocess_specs(name)
        self.workflow = BpmnWorkflow(top_level, subprocesses, script_engine=self.script_engine)

    def restore(self, filename):
        with open(filename) as fh:
            self.workflow = self.serializer.deserialize_json(fh.read())
            if self.script_engine is not None:
                self.workflow.script_engine = self.script_engine

    def dump(self):
        filename = input('Enter filename: ')
        with open(filename, 'w') as fh:
            dct = self.serializer.workflow_to_dict(self.workflow)
            dct[self.serializer.VERSION_KEY] = self.serializer.VERSION
            fh.write(json.dumps(dct, indent=2, separators=[', ', ': ']))

    def get_task_description(self, task, include_state=True):
        
        task_spec = task.task_spec
        lane = f'{task_spec.lane}' if task_spec.lane is not None else '-'
        name = task_spec.bpmn_name if task_spec.bpmn_name is not None else '-'
        description = task_spec.description if task_spec.description is not None else 'Task'
        state = f'{task.get_state_name()}' if include_state else ''
        return f'[{lane}] {name} ({description}: {task_spec.bpmn_id}) {state}'

    def get_task_details(self, task):
        print(self.get_task_description(task))
        print(json.dumps(self.serializer.data_converter.convert(task.data), indent=2, separators=[', ', ': ']))

    def list_tasks(self, tasks, heading, include_state=True):
        print(f'\n{heading}\n')
        for task in tasks:
            print(f'{self.get_task_description(task, include_state)}')

    def show_prompt(self, prompt, options):

        print()
        for action, description in options.items():
            print(f'\t<{action}> {description}')
        action = input(prompt)
        while action not in options:
            print("Invalid selection")
            action = input(prompt)
        return action

    def show_workflow_options(self, ready_tasks):

        options = {}
        if len(ready_tasks):
            options['r'] = 'Run a task'
        options['p'] = 'List past tasks'
        options['f'] = 'List future tasks'
        options['a'] = 'List all tasks'
        options['d'] = 'Dump workflow state'
        options['w'] = 'Wait'
        return self.show_prompt('\nSelect action: ', options)

    def select_task(self, tasks, heading=None):
        if heading is not None:
            print(f'\n{heading}')
        options = {}
        for idx, task in enumerate(tasks):
            options[str(idx + 1)] = self.get_task_description(task, False)
        value = self.show_prompt('\nSelect task: ', options)
        return tasks[int(value) - 1]

    def advance(self):
        engine_tasks = [t for t in self.workflow.get_tasks(TaskState.READY) if not t.task_spec.manual]
        while len(engine_tasks) > 0:
            for task in engine_tasks:
                task.run()
            self.workflow.refresh_waiting_tasks()
            engine_tasks = [t for t in self.workflow.get_tasks(TaskState.READY) if not t.task_spec.manual]

    def run_workflow(self, step=False):

        while not self.workflow.is_completed():

            if not step:
                self.advance()

            tasks = self.workflow.get_tasks(TaskState.READY|TaskState.WAITING)
            runnable = [t for t in tasks if t.state == TaskState.READY]
            human_tasks = [t for t in runnable if t.task_spec.manual]
            current_tasks = human_tasks if not step else runnable

            self.list_tasks(tasks, 'Ready and Waiting Tasks')
            if len(current_tasks) > 0:
                action = self.show_workflow_options(current_tasks)
            else:
                action = None
                if len(tasks) > 0:
                    input("\nPress any key to update task list")

            if action == 'r':
                task = self.select_task(current_tasks)
                handler = self.handlers.get(type(task.task_spec))
                if handler is not None:
                    handler(task)
                task.run()
            elif action == 'p':
                finished = [t for t in self.workflow.get_tasks(TaskState.FINISHED_MASK) if t.task_spec.bpmn_id is not None]
                task = self.select_task(finished, 'View Task Details')
                self.get_task_details(task)
            elif action == 'a':
                self.list_tasks([t for t in self.workflow.get_tasks() if t.task_spec.bpmn_id is not None], 'All Tasks')
            elif action == 'f':
                self.list_tasks([t for t in self.workflow.get_tasks(TaskState.FUTURE) if t.task_spec.bpmn_id is not None], 'Future Tasks')
            elif action == 'd':
                self.dump()

            self.workflow.refresh_waiting_tasks()

        while action != 'q':
            action = self.show_prompt('\nSelect action: ', {
                'a': 'List all tasks',
                'v': 'View workflow data',
                'q': 'Quit',
            })
            if action == 'a':
                self.list_tasks([t for t in self.workflow.get_tasks() if t.task_spec.bpmn_id is not None], "All Tasks")
            elif action == 'v':
                dct = self.serializer.data_converter.convert(self.workflow.data)
                print('\n' + json.dumps(dct, indent=2, separators=[', ', ': ']))
