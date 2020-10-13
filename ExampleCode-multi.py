from jinja2 import Template
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser
from SpiffWorkflow.camunda.specs.UserTask import EnumFormField, UserTask


def show_form(task):

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
        task.update_data_var(field.id, answer)

parser = CamundaParser()
parser.add_bpmn_file('multi_instance_array.bpmn')
spec = parser.get_spec('MultiInstanceArray')

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
    workflow.do_engine_steps()
    ready_tasks = workflow.get_ready_user_tasks()
print(workflow.last_task.data)
