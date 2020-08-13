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

#import logging
#debug = True
#logger = logging.getLogger('spiffLogger')
#logger.setLevel(logging.DEBUG)
#ch = logging.StreamHandler()
#formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s')
#ch.setFormatter(formatter)
#logger.addHandler(ch)
#

def updateDotDict(dict,id,value):
    x = id.split('.')
    print(x)
    if len(x) == 1:
        dict[x[0]]=value
    elif dict.get(x[0]):
        dict[x[0]][x[1]] = value
    else:
        dict[x[0]] = {x[1]:value}

def show_form(task):
    model = {}
    form = task.task_spec.form
    docs = task.task_spec.documentation
    
    #template = Template(docs)
    #print(template.render(task.data))
    for field in form.fields:
        #print("Please complete the following questions:")
        prompt = field.label
        print(task.data)
        if isinstance(field, EnumFormField):
            prompt += "? (Options: " + ', '.join([str(option.id) for option in field.options]) + ")"
        prompt += "? "
        updateDotDict(model,field.id,input(prompt))
        #model[field.id] = input(prompt)
    if task.data is None:
        task.data = {}
    task.update_data(model)
#    print(task.data)

ser = BpmnSerializer()

#f = open('RepeatForm.bpmn')
x = CamundaParser()
x.add_bpmn_file('lanes.bpmn')
spec = x.get_spec('lanes')
count = 0

def dumpStatus():
    global ser
    global count
    #print('dumping status #%d'%count)
    json = ser.serialize_workflow(workflow)
    f = open('status'+str(count)+'.json','w+')
    f.write(json)
    f.close()
    count = count + 1
    
def printTaskTree(tree,currentID,data):
    f = open('treeoutput.txt','w')
    #fix up to follow tree
    lookup = {'COMPLETED':'* ',
              'READY':'> ',
              'LIKELY':'0 ',
              'NOOP': '  '
              }
    for x in tree:
        if x['id'] == currentID:
            f.write('>>')
        else:
            f.write(lookup.get(x['state'],'O '))
        f.write("  "*x['indent'])
        f.write(x['description'])
        if x['task_id'] is not None:
            f.write(' ---> ')
            f.write(str(x['lane']))
        if x.get('is_decision') and x.get('backtracks') is not None:
            f.write('\n')
            f.write('  ' * x['indent'] + '   Returns to '+x['backtracks'][1])
        elif x.get('is_decision') and x.get('child_count',0)==0:
            f.write('\n')
            f.write('  '*x['indent']+'   Do Nothing')
        f.write('\n')
    f.write('\n\n\n-----------------\n')
    f.write(str(data))
    for lane in ['A','B']:
        f.write('\n\n'+lane+' Tasks\n')
        for x in workflow.get_ready_user_tasks(lane=lane):
            f.write('    ' + x.get_name() + '\n')
    f.close()


# def printTaskTree(tree,currentID):
#     f = open('treeoutput.txt','w')
#     #fix up to follow tree
#     for x in tree:
#         f.write(str(x))
#         f.write('\n')
#     f.close()



workflow = BpmnWorkflow(spec)
dumpStatus()
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
            printTaskTree(workflow.get_nav_list(),task.task_spec.id,task.data)
        workflow.do_engine_steps()
        ready_tasks = workflow.get_ready_user_tasks()
print("All tasks in the workflow are now complete.")
print("The following data was collected:")
print(workflow.last_task.data)
