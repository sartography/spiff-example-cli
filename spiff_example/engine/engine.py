import curses
import logging

from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException
from SpiffWorkflow.bpmn.specs.mixins.subworkflow_task import SubWorkflowTask
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow


logger = logging.getLogger('spiff_engine')

class BpmnEngine:
    
    def __init__(self, parser, serializer, handlers=None):

        self.parser = parser
        self.serializer = serializer
        self._handlers = handlers or {}

    def handler(self, task):
        handler = self._handlers.get(task.task_spec.__class__)
        if handler is not None:
            return handler(task)

    def add_spec(self, process_id, bpmn_files, dmn_files=None):

        try:
            self.parser.add_bpmn_files(bpmn_files)
            if dmn_files is not None:
                self.parser.add_dmn_files(dmn_files)
            spec = self.parser.get_spec(process_id)
            spec_id = self.serializer.create_workflow_spec(spec)
            logger.info(f'Added {process_id} with id {spec_id}')

            if spec_id is not None:
                specs = [(spec_id, spec)]
                while len(specs) > 0:
                    current_id, current = specs.pop(0)
                    dependencies = []
                    for task_spec in filter(lambda ts: isinstance(ts, SubWorkflowTask), current.task_specs.values()):
                        sp_spec = self.parser.get_spec(task_spec.spec)
                        sp_id = self.serializer.create_workflow_spec(sp_spec)
                        specs.append((sp_id, sp_spec))
                        dependencies.append(sp_id)
                    if len(dependencies) > 0:
                        self.serializer.set_spec_dependencies(current_id, dependencies)
                        logger.info(f'Added {len(dependencies)} for {process_id}')

            return spec_id
        except ValidationException as exc:
            # Clear the process parsers so the files can be re-added
            # There's probably plenty of other stuff that should be here
            # However, our parser makes me mad so not investigating further at this time
            self.parser.process_parsers = {}
            raise exc

    def list_specs(self):
        return self.serializer.list_specs()

    def delete_workflow_spec(self, spec_id):
        self.serializer.delete_workflow_spec(spec_id)
        logger.info(f'Deleted workflow spec with id {spec_id}')

    def start_workflow(self, spec_id):
        spec, sp_specs = self.serializer.get_workflow_spec(spec_id)
        wf = BpmnWorkflow(spec, sp_specs)
        wf_id = self.serializer.create_workflow(wf, spec_id)
        logger.info(f'Created workflow with id {wf_id}')
        return wf_id

    def get_workflow(self, wf_id):
        return self.serializer.get_workflow(wf_id)

    def update_workflow(self, workflow, wf_id):
        logger.info(f'Saved workflow {wf_id}')
        self.serializer.update_workflow(workflow, wf_id)

    def list_workflows(self, include_completed=False):
        return self.serializer.list_workflows(include_completed)

    def delete_workflow(self, wf_id):
        self.serializer.delete_workflow(wf_id)
        logger.info(f'Deleted workflow with id {wf_id}')
