#!/usr/bin/env python

import os, json
from hashlib import sha256

from SpiffWorkflow.spiff.parser.process import SpiffBpmnParser
from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer
from SpiffWorkflow.bpmn.serializer.default.workflow import (
    TaskConverter as DefaultTaskConverter,
    BpmnWorkflowConverter as DefaultWorkflowConverter
)
from SpiffWorkflow.task import Task
from SpiffWorkflow.spiff.serializer.config import SPIFF_CONFIG
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.util.task import TaskState

class TaskConverter(DefaultTaskConverter):
    def to_dict(self, task):
        return {
            'state': task.state,
            'task_spec': task.task_spec.name,
            'triggered': task.triggered,
            'internal_data': self.registry.convert(task.internal_data),
            'data': self.registry.convert(self.registry.clean(task.data)),
        }

class WorkflowConverter(DefaultWorkflowConverter):
    def to_dict(self, workflow):
        dct = super().to_dict(workflow)
        dct['tasks'] = list(dct['tasks'].values())
        dct.pop('last_task')
        dct.pop('root')
        return dct

SPIFF_CONFIG[Task] = TaskConverter
SPIFF_CONFIG[BpmnWorkflow] = WorkflowConverter

parser = SpiffBpmnParser()
registry = BpmnWorkflowSerializer.configure(SPIFF_CONFIG)
serializer = BpmnWorkflowSerializer(registry=registry)

process = 'Process_distributed'
bpmn_file = 'distributed.bpmn'

parser.add_bpmn_files([bpmn_file])
spec = parser.get_spec(process)

steps = []

def checksum(data):
    data_json = json.dumps(data, sort_keys=True)
    return sha256(data_json.encode("utf8")).hexdigest()

wf = BpmnWorkflow(spec)
step = 0
cs = checksum(serializer.to_dict(wf))
steps.append(cs)
print(step, cs)

while not wf.is_completed():
    task = wf.get_next_task(state=TaskState.READY)
    task.run()
    step += 1
    cs = checksum(serializer.to_dict(wf))
    steps.append(cs)
    print(step, cs)

print(checksum(steps))
with open('wf.json', 'w') as fh:
    fh.write(json.dumps(serializer.to_dict(wf), sort_keys=True, indent=2))

