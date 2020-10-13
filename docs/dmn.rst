DMN and Decision Tables
=======================

What is DMN
-----------

Decision Model and Notation (DMN) is a standard for business decision modeling. DMN allows modelers to separate decision logic from process logic and maintain it in a table format. DMN is linked into BPMN with a *decision task*.


BPMN Model With DMN
--------------------------------

With DMN, business analysts can model the rules that lead to a decision in an easy to read table. Those tables can be executed directly by SpiffWorkflow.

This minimizes the risk of misunderstandings between business analysts and developers, and allows rapid changes in production.

BPMN includes a decision task that refers to the decision table. The outcome of the decision lookup allows the next gateway or activity to route the flow.

Let's first look at the BPMN image below we are building on the basic example. Here we have an activity with the
business tasks that reads Make a decision this is where the table is rooted and called on the BPMN side.

.. image:: images/decision_table.png


Decision Table
----------------------

Here is a simple table example based on our TripInfo data.

.. image:: images/dmn.png

Users were asked to choose between cabin, hotel, and camping for the location of their trip. Based on this information, we want to send them a message about spam.

If they go camping or stay in a cabin, they should bring spam. If they stay in a hotel, they can buy it near the hotel. DMN tables allow annotations that help explain entries in the table.


Changes to ExampleCode.py
-------------------------

Up to this point, all of our BPMN models run using the code in ExampleCode.py. (We do need to updata the file and process names.)

For DMN, we need to modify our code so that we can import a DMN table.

This code is in Example-dmn.py.

Below are the code changes that happened to make this happen

We import a second parser.

.. code:: python

   from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser

and create a class based on the new parser.

.. code:: python

    class MyCustomParser(BpmnDmnParser):
     """
     A BPMN and DMN parser that can also parse Camunda forms.
     """
     OVERRIDE_PARSER_CLASSES = BpmnDmnParser.OVERRIDE_PARSER_CLASSES
     OVERRIDE_PARSER_CLASSES.update(CamundaParser.OVERRIDE_PARSER_CLASSES)

This new class can parse both BPMN and DMN.

To use the new class, we change

.. code:: python

   parser = CamundaParser()
   parser.add_bpmn_file('BasicExample.bpmn')
   spec = parser.get_spec('BasicExample')

to

.. code:: python

    parser = MyCustomParser()
    parser.add_bpmn_file('decision_table.bpmn')
    parser.add_dmn_file('spam_decision.dmn')
    spec = parser.get_spec('step1')

Note that we add both a bpmn file and a dmn file to the parser.

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

