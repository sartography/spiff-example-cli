import curses
import logging

from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException
from SpiffWorkflow.bpmn.specs.mixins.events.event_types import CatchingEvent
from SpiffWorkflow.bpmn import BpmnWorkflow
from SpiffWorkflow.bpmn.script_engine import PythonScriptEngine
from SpiffWorkflow.bpmn.util.diff import (
    SpecDiff,
    diff_dependencies,
    diff_workflow,
    filter_tasks,
    migrate_workflow,
)
from SpiffWorkflow import TaskState

from .instance import Instance


logger = logging.getLogger('spiff_engine')

class BpmnEngine:
    
    def __init__(self, parser, serializer, script_env=None, instance_cls=None):

        self.parser = parser
        self.serializer = serializer
        # Ideally this would be recreated for each instance
        self._script_engine = PythonScriptEngine(script_env)
        self.instance_cls = instance_cls or Instance

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
        return self.instance_cls(wf_id, wf, save=self.update_workflow)

    def get_workflow(self, wf_id):
        wf = self.serializer.get_workflow(wf_id)
        wf.script_engine = self._script_engine
        return self.instance_cls(wf_id, wf, save=self.update_workflow)

    def update_workflow(self, instance):
        logger.info(f'Saved workflow {instance.wf_id}')
        self.serializer.update_workflow(instance.workflow, instance.wf_id)

    def list_workflows(self, include_completed=False):
        return self.serializer.list_workflows(include_completed)

    def delete_workflow(self, wf_id):
        self.serializer.delete_workflow(wf_id)
        logger.info(f'Deleted workflow with id {wf_id}')

    def diff_spec(self, original_id, new_id):
        original, _ = self.serializer.get_workflow_spec(original_id, include_dependencies=False)
        new, _ = self.serializer.get_workflow_spec(new_id, include_dependencies=False)
        return SpecDiff(self.serializer.registry, original, new)

    def diff_dependencies(self, original_id, new_id):
        _, original = self.serializer.get_workflow_spec(original_id, include_dependencies=True)
        _, new = self.serializer.get_workflow_spec(new_id, include_dependencies=True)
        return diff_dependencies(self.serializer.registry, original, new)

    def diff_workflow(self, wf_id, spec_id):
        wf = self.serializer.get_workflow(wf_id)
        spec, deps = self.serializer.get_workflow_spec(spec_id)
        return diff_workflow(self.serializer.registry, wf, spec, deps)

    def can_migrate(self, wf_diff, sp_diffs):

        def safe(result):
            mask = TaskState.COMPLETED|TaskState.STARTED
            tasks = result.changed + result.removed
            return len(filter_tasks(tasks, state=mask)) == 0

        for diff in sp_diffs.values():
            if diff is None or not safe(diff):
                return False
        return safe(wf_diff)

    def migrate_workflow(self, wf_id, spec_id, validate=True):

        wf = self.serializer.get_workflow(wf_id)
        spec, deps = self.serializer.get_workflow_spec(spec_id)
        wf_diff, sp_diffs = diff_workflow(self.serializer.registry, wf, spec, deps)

        if validate and not self.can_migrate(wf_diff, sp_diffs):
            raise Exception('Workflow is not safe to migrate!')

        migrate_workflow(wf_diff, wf, spec)
        for sp_id, sp in wf.subprocesses.items():
            migrate_workflow(sp_diffs[sp_id], sp, deps.get(sp.spec.name))
        wf.subprocess_specs = deps

        self.serializer.delete_workflow(wf_id)
        return self.serializer.create_workflow(wf, spec_id)
