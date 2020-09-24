Concepts, Example Code,and Diagrams
===================================

Example Code
------------

This is the example code for running the workflow::

    from SpiffWorkflow.specs import *
    from SpiffWorkflow import Workflow

    spec = WorkflowSpec()
    # (Add tasks to the spec here.)

    wf = Workflow(spec)
    wf.complete_task_from_id(...)

All below examples will use the same code


Exclusive Gateway Example:
--------------------------
An exclusive gateway is used to express that exactly one alternative can be selected. In an exclusive gateway, the
token runs along the sequence flow whose condition is met first. The response you get depends on which one path that
you chose to take. For example looking at the BPMN and output you can see that the path that is taken depends on the
response to the “Do you like spam?” question in the user task previous. If you answered no you will be asked for ONLY
bad spam brands, if you answered yes you will be asked ONLY good spam brands.

.. image:: images/exgateway.png

.. image:: images/exgateway-output.png



Parallel Gateway Example:
-------------------------
A parallel or AND gateway creates parallel paths without checking any conditions. This means that each outgoing sequence
flow becomes active upon the execution of a parallel gateway, which is commonly known as a “process fork”. Let's look
at the example below, unlike in the previous example of exclusive gateways, you will be promoted to answer questions
in regards to both good AND bad brands.

.. image:: images/plgateway.png

.. image:: images/plgateway-output.png
