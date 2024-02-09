import json, re
import os
import logging
from uuid import uuid4, UUID
from datetime import datetime

from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer
from SpiffWorkflow.bpmn.serializer.default.workflow import BpmnWorkflowConverter, BpmnSubWorkflowConverter
from SpiffWorkflow.bpmn.serializer.default.process_spec import BpmnProcessSpecConverter

logger = logging.getLogger(__name__)

class FileSerializer(BpmnWorkflowSerializer):

    @staticmethod
    def initialize(dirname):
        try:
            os.makedirs(dirname, exist_ok=True)
            os.mkdir(os.path.join(dirname, 'spec'))
            os.mkdir(os.path.join(dirname, 'instance'))
        except FileExistsError:
            pass

    def __init__(self, dirname, **kwargs):
        super().__init__(**kwargs)
        self.dirname = dirname
        self.fmt = {'indent': 2, 'separators': [', ', ': ']}

    def create_workflow_spec(self, spec, dependencies):

        spec_dir = os.path.join(self.dirname, 'spec')
        if spec.file is not None:
            dirname = os.path.join(spec_dir, os.path.dirname(spec.file), spec.name)
        else:
            dirname = os.path.join(spec_dir, spec.name)
        filename = os.path.join(dirname, f'{spec.name}.json')
        try:
            os.makedirs(dirname, exist_ok=True)
            with open(filename, 'x') as fh:
                fh.write(json.dumps(self.to_dict(spec), **self.fmt))
            if len(dependencies) > 0:
                os.mkdir(os.path.join(dirname, 'dependencies'))
                for name, sp in dependencies.items():
                    with open(os.path.join(dirname, 'dependencies', f'{name}.json'), 'w') as fh:
                        fh.write(json.dumps(self.to_dict(sp), **self.fmt))
        except FileExistsError:
            pass
        return filename

    def delete_workflow_spec(self, filename):
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass

    def get_workflow_spec(self, filename, **kwargs):
        dirname = os.path.dirname(filename)
        with open(filename) as fh:
            spec = self.from_dict(json.loads(fh.read()))
        subprocess_specs = {}
        depdir = os.path.join(os.path.dirname(filename), 'dependencies')
        if os.path.exists(depdir):
            for f in os.listdir(depdir):
                name = re.sub('\.json$', '', os.path.basename(f))
                with open(os.path.join(depdir, f)) as fh:
                    subprocess_specs[name] = self.from_dict(json.loads(fh.read()))
        return spec, subprocess_specs

    def list_specs(self):
        library = []
        for root, dirs, files in os.walk(os.path.join(self.dirname, 'spec')):
            if 'dependencies' not in root:
                for f in files:
                    filename = os.path.join(root, f)
                    name = re.sub('\.json$', '', os.path.basename(f))
                    path = re.sub(os.path.join(self.dirname, 'spec'), '', filename).lstrip('/')
                    library.append((filename, name, path))
        return library

    def create_workflow(self, workflow, spec_id):
        name = re.sub('\.json$', '', os.path.basename(spec_id))
        dirname = os.path.join(self.dirname, 'instance', name)
        os.makedirs(dirname, exist_ok=True)
        wf_id = uuid4()
        with open(os.path.join(dirname, f'{wf_id}.json'), 'w') as fh:
            fh.write(json.dumps(self.to_dict(workflow), **self.fmt))
        return os.path.join(dirname, f'{wf_id}.json')

    def get_workflow(self, filename, **kwargs):
        with open(filename) as fh:
            return self.from_dict(json.loads(fh.read()))

    def update_workflow(self, workflow, filename):
        with open(filename, 'w') as fh:
            fh.write(json.dumps(self.to_dict(workflow), **self.fmt))

    def delete_workflow(self, filename):
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass

    def list_workflows(self, include_completed):
        instances = []
        for root, dirs, files in os.walk(os.path.join(self.dirname, 'instance')):
            for f in files:
                filename = os.path.join(root, f)
                name = os.path.split(os.path.dirname(filename))[-1]
                stat = os.lstat(filename)
                created = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%^m-%d %H:%M:%S')
                updated = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%^m-%d %H:%M:%S')
                # '?' is active tasks -- we can't know this unless we reydrate the workflow
                # We also have to lose the ability to filter out completed workflows
                instances.append((filename, name, '-', created, updated, '-'))
        return instances


