from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser
from SpiffWorkflow.camunda.specs.UserTask import EnumFormField, UserTask


def updateDotDict(dict,id,value):
    x = id.split('.')
    #print(x)
    if len(x) == 1:
        dict[x[0]]=value
    elif dict.get(x[0]):
        dict[x[0]][x[1]] = value
    else:
        dict[x[0]] = {x[1]:value}


def show_form(task):
    model = {}
    form = task.task_spec.form

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
        print(task.data)
        print(field.id)
        print(answer)
        updateDotDict(model,field.id,answer)
        task.update_data(model)

x = CamundaParser()
x.add_bpmn_file('step 2.bpmn')
spec = x.get_spec('step2')

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
