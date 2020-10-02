Concepts, Example Code,and Diagrams
===================================


Basic Example:
--------------
In this example you are doing one of the most simple versions of a BPMN workflow. We have a start event, an activity
with a UserTask, and an end event. When the user task activity box is clicked there are forms that you can fill to ask
questions. In this flow the user is answering two questions : Where are they going and do they like spam. Below you will
find what the user is being prompted to answer and how the data is being stored in the data dictionary (covered later).

.. image:: images/basic_example.png
   :scale: 25%
   :align: center

.. image:: images/basic_example_output.png

When making the BPMN and assigning the activity with a UserTask you then have the option to fill out a form which
will (using the source code listed below), prompt and ask the sure to complete the questions and collect the data.

The form in the image
below is the same form that is used to create the example above.  In this form you are first asked to enter a form key
which identifies the name of the form. Then you can add form fields. So here we have added location, below we have added
the different components that need to be in this form field, first with the id-the name of the variable, then the type
in this case and enum. Next we need to have a label, this is the Information that will be displayed to the user.
Followed by values, it is recommended that you add a default value just in case the user does not input a variable
that is recognized. And with all that you have the basics that you need to get the form up and working.

.. image:: images/basic_example_form.png

Example Code
------------
To enable the workflow we made above, we can interact with it using the code found in the
`ExampleCode.py <ExampleCode.py>`_ file.

This is the example code for running the workflow. The first thing that you will need to do is make sure that the
following files are imported

.. code:: python
   :name: ExampleCode.py
   :number-lines: 1

    from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
    from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser
    from SpiffWorkflow.camunda.specs.UserTask import EnumFormField, UserTask


In the code below we have first specialized parse that parsers the Camunda file
we then add the file (bpmn) in, that we just parsed. Lastly for this chunck we are getting a specification, it is loading
all the files from the and has complied it down

.. code:: python
   :name: ExampleCode.py
   :number-lines: 23

    x = CamundaParser()
    x.add_bpmn_file('Basicexample.bpmn')
    spec = x.get_spec('Basicexample')

On this line below we are calling BPMNworkflow(spec), this is creating instances of that workflow. Meaning that it is a running
working workflow, this allows for the state to be known, such as where you are and what current tasks needs to be completed.

.. code:: python
   :name: ExampleCode.py
   :number-lines: 27

    workflow = BpmnWorkflow(spec)

On the line bellow you are running .do_engine_steps(): This allows you to do things that are automatic. For example if
you have script task that need to run at the start event it will go through and do all the automatic task that are
already there. The code after that on other hands calls for all task, and gets it ready to run all tasks. Including
getting parallele tasks ready to run

.. code:: python
   :name: ExampleCode.py
   :number-lines: 29

    workflow.do_engine_steps()
    ready_tasks = workflow.get_ready_user_tasks()

In these last few lines our code is running through the workflow and seeing where there are task that have a UserTask
then it will show form and print out the data from that task. (look at example below to see what printed questions
look like and what the data at the end looks like.)

.. code:: python
   :name: ExampleCode.py
   :number-lines: 29

    while len(ready_tasks) > 0:
        for task in ready_tasks:
            if isinstance(task.task_spec, UserTask):
               show_form(task)
               print(task.data)
            else:
                print("Complete Task ", task.task_spec.name)
            workflow.complete_task_from_id(task.id)

All below examples will use the same code

There is also a function at the top of the Example Code file that allows for the form to ask the user the quations
that are filled out in the form section, ask for input and update the information as the workflow is working through
the process.

.. code:: python
   :name: ExampleCode.py
   :number-lines: 6

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
            task.update_data_var(field.id,answer)

Exclusive Gateway Example
--------------------------
An exclusive gateway is used to express that exactly one alternative can be selected. In an exclusive gateway, the
token runs along the sequence flow whose condition is met first. The response you get depends on which one path that
you chose to take. For example looking at the BPMN and output you can see that the path that is taken depends on the
response to the “Do you like spam?” question in the user task previous. If you answered no you will be asked for ONLY
bad spam brands, if you answered yes you will be asked ONLY good spam brands.

.. image:: images/exgateway.png
   :scale: 25%
   :align: center

.. image:: images/exgateway-output.png


Parallel Gateway Example
-------------------------
A parallel or AND gateway creates parallel paths without checking any conditions. This means that each outgoing sequence
flow becomes active upon the execution of a parallel gateway, which is commonly known as a “process fork”. Let's look
at the example below, unlike in the previous example of exclusive gateways, you will be promoted to answer questions
in regards to both good AND bad brands.

.. image:: images/plgateway.png
   :scale: 25%
   :align: center

.. image:: images/plgateway-output.png

Script Example
-----------------
.. sidebar:: Setting up a script task

  To create a script task in Camunda modeler, you drag over a task from the object bar and then right click on the
  task, use the wrench and select a script task from the options.  Once you have a script task selected, use the
  'inline script' option in the options bar on the right and put in the code that you want to run. When using scripts,
  you can interact with all of the data that has been put into the task.data object during the workflow.

  .. image:: images/script_task.png
     :align: center


A Script Task is executed by a business process engine. In our example it's the .do_engine_steps(). The modeler (for us
it will be Camunda) or implementer defines a script in a language that the engine can interpret, we will be using
python.
When the Task is ready to start, the engine will execute the script. When the script is completed, the Task will also be
completed. These are easy to use when a task can easily be performed automatically.


.. image:: images/Scriptsexample.png
   :scale: 25%
   :align: center

.. image:: images/Scriptsexample-output.png


Multi-Instance Example
-------------------------
Multi-instance activities are represented by three horizontal or vertical lines at the bottom-center of the activity
and task symbol. It’s purpose is to show that the activity occurs for a collection of objects or items.  The number of
times that the activity completes is defined by the number of items that exist in the collection. This is different from
other looping mechanisms that must check a condition every time the loop completes in order to determine if it should
continue looping. Three vertical lines indicate that the multi-instance activity is non-sequential.  This means that the
activity can be completed for each item in the collection in no particular order. Three horizontal lines indicate that
the multi-instance activity is sequential. This means that the activity must complete for each item in the order that
they are received within the collection.

Let's look at the example below, the first activity is a UserTask which allows us to ask how many people are going on
this trip. We are then going to use that number to go through the multi-instance. The first is non-sequential, which
means that you can add the names in any order. Then in the next activity the multi-instance in sequential and will go
through the names in the order they were received. This can more easily be seen through the output image.

.. image:: images/multi_instance_array.png
.. image:: images/multi_instance_array-output.png


MultiInstance Notes
-------------------

A subset of MultiInstance and Looping Tasks are supported. Notably,
the completion condition is not currently supported.

The following definitions should prove helpful

**loopCardinality** - This variable can be a text representation of a
number - for example '2' or it can be the name of a variable in
task.data that resolves to a text representation of a number.
It can also be a collection such as a list or a dictionary. In the
case that it is a list, the loop cardinality is equal to the length of
the list and in the case of a dictionary, it is equal to the list of
the keys of the dictionary.

If loopCardinality is left blank and the Collection is defined, or if
loopCardinality and Collection are the same collection, then the
MultiInstance will loop over the collection and update each element of
that collection with the new information. In this case, it is assumed
that the incoming collection is a dictionary, currently behavior for
working with a list in this manner is not defined and will raise an error.

**Collection** This is the name of the collection that is created from
the data generated when the task is run. Examples of this would be
form data that is generated from a UserTask or data that is generated
from a script that is run. Currently the collection is built up to be
a dictionary with a numeric key that corresponds to the place in the
loopCardinality. For example, if we set the loopCardinality to be a
list such as ['a','b','c] the resulting collection would be {1:'result
from a',2:'result from b',3:'result from c'} - and this would be true
even if it is a parallel MultiInstance where it was filled out in a
different order.

**Element Variable** This is the variable name for the current
iteration of the MultiInstance. In the case of the loopCardinality
being just a number, this would be 1,2,3, . . .  If the
loopCardinality variable is mapped to a collection it would be either
the list value from that position, or it would be the value from the
dictionary where the keys are in sorted order.  It is the content of the
element variable that should be updated in the task.data. This content
will then be added to the collection each time the task is completed.

Example:
  In a sequential MultiInstance, loop cardinality is ['a','b','c'] and elementVariable is 'myvar'
  then in the case of a sequential multiinstance the first call would
  have 'myvar':'a' in the first run of the task and 'myvar':'b' in the
  second.

Example:
  In a Parallel MultiInstance, Loop cardinality is a variable that contains
  {'a':'A','b':'B','c':'C'} and elementVariable is 'myvar' - when the multiinstance is ready, there
  will be 3 tasks. If we choose the second task, the task.data will
  contain 'myvar':'B'.

Updating Data
-------------

While there may be some MultiInstances that will not result in any
data, most of the time there will be some kind of data generated that
will be collected from the MultiInstance. A good example of this is a
UserTask that has an associated form or a script that will do a lookup
on a variable.

Each time the MultiInstance task generates data, the method
task.update_data(data) should be called where data is the data
generated. The 'data' variable that is passed in is assumed to be a
dictionary that contains the element variable. Calling task.update_data(...)
will ensure that the MultiInstance gets the correct data to include in the
collection. The task.data is also updated with the dictionary passed to
this method.

Example:
  In a Parallel MultiInstance, Loop cardinality is a variable that contains
  {'a':'A','b':'B','c':'C'} and elementVariable is 'myvar'.
  If we choose the second task, the task.data will contain 'myvar':{'b':'B'}.
  If we wish to update the data, we would call task.update_data('myvar':{'b':'B2'})
  When the task is completed, the task.data will now contain:
  {'a':'A','b':'B2','c':'C'}

Looping Tasks
-------------

A looping task sets the cardinality to 25 which is assumed to be a
sane maximum value. The looping task will add to the collection each
time it is processed assuming data is updated as outlined in the
previous paragraph.

To halt the looping the task.terminate_loop()

Each time task.complete() is called (or
workflow.complete_task_by_id(task.id) ), the task will again present
as READY until either the cardinality is exausted, or
task.terminate_loop() is called.


Shared code
-----------

Up to this point, all of these examples can run using the exact same code, only changing the name of the BPMN and the
id of the workflow (in Camunda modeler, you click on the background and change the ID field in the 'general' tab -
this is slightly different when working with multi-lane workflows which are covered later).

For the following example, we will need to change the code a bit so that we can import a DMN table, outlined below.

Please see the Example-dmn.py code for an example.

Below are the code changes that happened to make this happen

add

.. code:: python
   :number-lines: 2

   from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser

and

.. code:: python
   :number-lines: 6

    class MyCustomParser(BpmnDmnParser):
     """
     A BPMN and DMN parser that can also parse Camunda forms.
     """
     OVERRIDE_PARSER_CLASSES = BpmnDmnParser.OVERRIDE_PARSER_CLASSES
     OVERRIDE_PARSER_CLASSES.update(CamundaParser.OVERRIDE_PARSER_CLASSES)

change

.. code:: python
   :number-lines: 23

   x = CamundaParser()
   x.add_bpmn_file('Basicexample.bpmn')
   spec = x.get_spec('Basicexample')

to

.. code:: python
   :number-lines: 31

    x = MyCustomParser()
    x.add_bpmn_file('decision_table.bpmn')
    x.add_dmn_file('spam_decision.dmn')
    spec = x.get_spec('step1')

Basically, we needed a class that would handle both the Camunda parser AND a dmn parser in the same workflow so we
made the custom class above

.. sidebar:: TODO

   This should really change - it seems really confusing to a person new to this as to why I should have to create a
   custom class to do this.

Once we have the additional capabilities we will be able to process a workflow with a DMN table

Dmn and Decision Table Example:
--------------------------------
In DMN, decisions can be modeled and executed using the same language. Business analysts can model the rules that lead
to a decision in an easy to read table, and those tables can be executed directly by SpiffWorkflow
This minimizes the risk of misunderstandings between business analysts and developers, and it even allows rapid changes
in production. Yes we can do a lot of the things we do with DMN using BPMN gateways but it creates complicated and very
disorganized BPMN allowing for mistakes and confusions. BPMN includes a business rule task, which is the decision table.
That task refers to a decision that needs to be made, and the outcome of the decision that is made based on the table
allows for the next gateway or activity to route the flow.

Let's first look at the BPMN image below we are building on the basic example. Here we have an activity with the
business tasks that reads Make a decision this is where the table is rooted and called on the BPMN side.

.. image:: images/decision_table.png


.. sidebar:: TODO

   SpiffWorkflow still doesn't honor the hit policy, and it currently requires you to jump through some hoops if you
   want to use the FEEL expression language rather than python ( you can't just change the expression language)

Now let's look at the DMN table:

    * The column second from the left refers to possible input data. In this example,
      there is only one input column. The cell with the text “Location” defines what the input is. In DMN, this is the
      label for an input expression. The cells below called input entries refer to the possible conditions regarding the
      input. Those conditions are in quotation marks (like “cabin”), which is because we are technically comparing
      String values.
    * For each possible input entry, we define the according output entry in the cell next to it. That’s how we express
      that based on the location, how you must bring your Spam. Again, we have to use quotation marks because
      technically we are assigning String values.
    * Last but not least, you can annotate your rules in the column on the right. Those annotations are only there
      for you to explain and are not seen by anyone else, and will be ignored by a decision engine.

In the DMN table for each input and output, we can define an expression to evaluate. For example, the expression for
"Location" is location that we created in the TripInfo user task, and stores the output in the variable
'spampurchase'. These are defined as part of the DMN table. You can have multiple inputs and outputs, for example you
might want to add another input varible that determines if we are hungry or not, and if we aren't hungry we have the
output show that we don't need to get any Spam.


.. image:: images/dmn.png

Lastly you can see an example of what is happening in the output image below.

.. image:: images/dmn-output.png


