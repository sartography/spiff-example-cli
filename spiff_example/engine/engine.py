import curses
import logging

from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException
from SpiffWorkflow.bpmn.specs.mixins.events.event_types import CatchingEvent
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.util.task import TaskState


logger = logging.getLogger('spiff_engine')

class BpmnEngine:
    
    def __init__(self, parser, serializer, handlers=None, script_engine=None):

        self.parser = parser
        self.serializer = serializer
        self._script_engine = script_engine or PythonScriptEngine()
        self._handlers = handlers or {}

    def handler(self, task):
        handler = self._handlers.get(task.task_spec.__class__)
        if handler is not None:
            return handler(task)

    def add_spec(self, process_id, bpmn_files, dmn_files):
        self.add_files(bpmn_files, dmn_files)
        try:
            spec = self.parser.get_spec(process_id)
            dependencies = self.parser.get_subprocess_specs(process_id)
        except ValidationException as exc:
            # Clear the process parsers so the files can be re-added
            # There's probably plenty of other stuff that should be here
            # However, our parser makes me mad so not investigating further at this time
            self.parser.process_parsers = {}
            raise exc
        spec_id = self.serializer.create_workflow_spec(spec, dependencies)
        logger.info(f'Added {process_id} with id {spec_id}')
        return spec_id

    def add_collaboration(self, collaboration_id, bpmn_files, dmn_files=None):
        self.add_files(bpmn_files, dmn_files)
        try:
            spec, dependencies = self.parser.get_collaboration(collaboration_id)
        except ValidationException as exc:
            self.parser.process_parsers = {}
            raise exc
        spec_id = self.serializer.create_workflow_spec(spec, dependencies)
        logger.info(f'Added {collaboration_id} with id {spec_id}')
        return spec_id

    def add_files(self, bpmn_files, dmn_files):
        self.parser.add_bpmn_files(bpmn_files)
        if dmn_files is not None:
            self.parser.add_dmn_files(dmn_files)

    def list_specs(self):
        return self.serializer.list_specs()

    def delete_workflow_spec(self, spec_id):
        self.serializer.delete_workflow_spec(spec_id)
        logger.info(f'Deleted workflow spec with id {spec_id}')

    def start_workflow(self, spec_id):
        spec, sp_specs = self.serializer.get_workflow_spec(spec_id)
        wf = BpmnWorkflow(spec, sp_specs, script_engine=self._script_engine)
        wf_id = self.serializer.create_workflow(wf, spec_id)
        logger.info(f'Created workflow with id {wf_id}')
        return wf_id

    def get_workflow(self, wf_id):
        wf = self.serializer.get_workflow(wf_id)
        wf.script_engine = self._script_engine
        return wf

    def update_workflow(self, workflow, wf_id):
        logger.info(f'Saved workflow {wf_id}')
        self.serializer.update_workflow(workflow, wf_id)

    def list_workflows(self, include_completed=False):
        return self.serializer.list_workflows(include_completed)

    def delete_workflow(self, wf_id):
        self.serializer.delete_workflow(wf_id)
        logger.info(f'Deleted workflow with id {wf_id}')

    def run_until_user_input_required(self, workflow):
        task = workflow.get_next_task(state=TaskState.READY, manual=False)
        while task is not None:
            task.run()
            self.run_ready_events(workflow)
            task = workflow.get_next_task(state=TaskState.READY, manual=False)

    def run_ready_events(self, workflow):
        workflow.refresh_waiting_tasks()
        task = workflow.get_next_task(state=TaskState.READY, spec_class=CatchingEvent)
        while task is not None:
            task.run()
            task = workflow.get_next_task(state=TaskState.READY, spec_class=CatchingEvent)
