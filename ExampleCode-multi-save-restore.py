from jinja2 import Template
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
import os
from SpiffWorkflow.bpmn.serializer.BpmnSerializer import BpmnSerializer
from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser
from SpiffWorkflow.camunda.specs.UserTask import EnumFormField, UserTask


def show_form(task):
    model = {}
    form = task.task_spec.form
    docs = task.task_spec.documentation

    template = Template(docs)
    print(task.data)
    print(template.render(task.data))

    if task.data is None:
        task.data = {}

    for field in form.fields:
        prompt = field.label
        if isinstance(field, EnumFormField):
            prompt += "? (Options: " + ', '.join([str(option.id) for option in field.options]) + ")"
        prompt += "? "
        answer = input(prompt)
        if field.type == "long":
            answer = int(answer)
        task.update_data_var(field.id,answer)

if os.path.exists('ExampleSaveRestore.js'):
    f = open('ExampleSaveRestore.js')
    state = f.read()
    f.close()
    workflow = BpmnSerializer().deserialize_workflow(
                state, workflow_spec=None)
else:
    x = CamundaParser()
    x.add_bpmn_file('multi_instance_array.bpmn')
    spec = x.get_spec('MultiInstanceArray')

    workflow = BpmnWorkflow(spec)

workflow.do_engine_steps()
ready_tasks = workflow.get_ready_user_tasks()
while len(ready_tasks) > 0:
    for task in ready_tasks:
        if isinstance(task.task_spec, UserTask):
           show_form(task)
           print(task.data)
        else:
            print("Complete Task ", task.task_spec.name)
        workflow.complete_task_from_id(task.id)
        state = BpmnSerializer().serialize_workflow(workflow, include_spec=True)
        f = open('ExampleSaveRestore.js', 'w')
        f.write(state)
        f.close()
    workflow.do_engine_steps()
    ready_tasks = workflow.get_ready_user_tasks()
print(workflow.last_task.data)
