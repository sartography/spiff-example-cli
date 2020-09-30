from jinja2 import Template
from SpiffWorkflow import Task as SpiffTask, Workflow
from SpiffWorkflow.bpmn.BpmnScriptEngine import BpmnScriptEngine
from SpiffWorkflow.bpmn.serializer.BpmnSerializer import BpmnSerializer
from SpiffWorkflow.bpmn.specs.EndEvent import EndEvent
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser
from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from SpiffWorkflow.operators import Operator
from SpiffWorkflow.serializer.xml import XmlSerializer
from SpiffWorkflow.camunda.specs.UserTask import EnumFormField, UserTask



def show_form(task):
    form = task.task_spec.form

    if task.data is None:
        task.data = {}

    for field in form.fields:
        #print("Please complete the following questions:")
        prompt = field.label
        if isinstance(field, EnumFormField):
            prompt += "? (Options: " + ', '.join([str(option.id) for option in field.options]) + ")"
        prompt += "? "
        answer = input(prompt)
        task.update_data_var(field.id,answer)



ser = BpmnSerializer()


x = CamundaParser()
x.add_bpmn_file('lanes.bpmn')
spec = x.get_spec('lanes')
count = 0

    
def printTaskTree(tree,currentID,data):
    print("\n\n\n")
    print("Current Tree")
    print("-------------")
    lookup = {'COMPLETED':'* ',
              'READY':'> ',
              'LIKELY':'0 ',
              'NOOP': '  '
              }
    for x in tree:
        if x['id'] == currentID:
            print('>>', end='')
        else:
            print(lookup.get(x['state'],'O '),end='')
        print("  "*x['indent'], end='')
        print(x['description'], end = '')
        if x['task_id'] is not None:
            print(' ---> ',end='')
            print(str(x['lane']),end='')
        if x.get('is_decision') and x.get('backtracks') is not None:
            print()
            print('  ' * x['indent'] + '   Returns to '+x['backtracks'][1],end='')
        elif x.get('is_decision') and x.get('child_count',0)==0:
            print()
            print('  '*x['indent']+'   Do Nothing', end='')
        print()
    print('\n\nCurrent Data')
    print('-----------------')
    print(str(data),end='')
    print('\n\nReady Tasks')
    print('-----------------')

    for lane in ['A','B']:
        print(lane+' Tasks')
        for x in workflow.get_ready_user_tasks(lane=lane):
            print('    ' + x.get_name())
    print('\n\n\n')
    





workflow = BpmnWorkflow(spec)

while not workflow.is_completed():
    workflow.do_engine_steps()

    ready_tasks = workflow.get_ready_user_tasks()
    while len(ready_tasks) > 0:
        for task in ready_tasks:
            printTaskTree(workflow.get_nav_list(),task.task_spec.id,task.data)
            if isinstance(task.task_spec, UserTask):
                show_form(task)
                print("complete task")
            else:
                print("Complete Task ",task.task_spec.name)
            workflow.complete_task_from_id(task.id)
            
        workflow.do_engine_steps()
        ready_tasks = workflow.get_ready_user_tasks()
printTaskTree(workflow.get_nav_list(),task.task_spec.id,task.data)
print("All tasks in the workflow are now complete.")
print("The following data was collected:")
print(workflow.last_task.data)
