How to Create Your Own BPMN:
============================

Making your first BPMN can be overwhelming, here we can go over an example step by step and create a simple flow together
with as many attributes as possible. In our example and through the documentation we will continue to use Camunda Modeler
as our application for modeling BPMN. `Camunda Modeler Download Page <https://camunda.com/download/modeler/>`_

.. sidebar:: BPMN Modelers

  There are a number of modelers in existence, but Camunda is just one of them. Camunda also offers their own platform
  run BPMN workflows. SpiffWorkflow uses Python as the main working language but Camunda uses Java. Other modelers
  may work, with SpiffWorkflow, however Camunda offers extensions that allow for forms and form questions to be asked
  of the user.

The first step in anything in life is getting started, with BPMN you represent the start of a flow with a single thin
border circle, also known as a start event. In some cases there are symbols inside the start event called triggers.
These triggers identify the “meaning” of the process's start.


.. figure:: images/simplestworkflow.png
   :scale: 25%
   :align: center

   A simple workflow.

All though this is the last step to putting our flow together, we are going to quickly go over the end event. The end
event is shown with a single thick border around a circle. Much like the start event an end event can also have triggers
signals to indicate how or when the event ended.

This is a very straight forward next step but to make sure that we are all on the same page, we are going to quickly go
over the Sequence flow, drawn in the diagram as a solid line connector. It represents the sequential  execution of
process steps:

When the node at the tail of a sequence flow completes, the node  at the arrowhead is enabled to start.

Now we need to tell the flow what it needs to do, this is down by drawing a rounded rectangular shape.
These are called activities which represent an action.

More complicated Workflows
--------------------------

.. figure:: images/plgateway.png
   :scale: 25%
   :align: center

   A workflow with a gateway


The diamond shape is called a gateway, It represents a branch point in our flow.  There are a few other gateways that
BPMN utilizes but the one used in our example is called an exclusive data-based  gateway (also called an XOR gateway).
When we use this gateway we are saying that you must take one path or the other based on some data condition.

The important point is that we can add a branch in the workflow **without** creating an explicit branch in the code.
As we build more complicated workflows with more features, we will have to add some items to our code to support
those features, but once we have them, we should be able to run any workflow without major changes to the underlying
code that is using the SpiffWorkflow library.

.. sidebar:: BPMN Resources

  This guide is a mere introduction to how to get started with BPMN allowing someone to get started with
  SpiffWorkflow and start using it to write programs that perform a workflow and let SpiffWorkflow do the heavy lifting.
  For a more serious modeling, we recommend looking for more comprehensive resources. We have used the books by Bruce
  Silver as a guide for our BPMN modeling.

  .. image:: images/bpmnbook.jpg
     :align: center


Goals of a Good BPMN:
---------------------
1. Correctness. Now we understand this means not only semantic correctness – the  shapes and symbols are used correctly
– but structural correctness as well, so that the  instance of each activity corresponds 1:1 with the process instance.

2.Clarity. The process logic should be clear from the diagrams alone, without prior  knowledge of how the process works
or even of the terminology employed.

3.Completeness. It should be possible to tell from a single glance how the process  starts, it’s possible end states,
what the instance represents, and all interactions with  external entities. The Method actually begins with this.

4. Consistency. Given the same set of process information, ideally all modelers should  create (more or less) the same
process model. If all members of your project team  follow the Method, understanding each other’s diagrams becomes a breeze.
Over ten years of teaching Method and Style, the Method has evolved to become more  mechanical, more standardized in the
order of its steps, and this has helped with  consistency.


