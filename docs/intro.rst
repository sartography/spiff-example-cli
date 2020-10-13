Overview of BPMN:
============================

To use SpiffWorkflow, you need at least a basic understanding of BPMN. This page offers a brief overview. There are many resources for additional information about BPMN.

In these examples and throughout the documentation we use the Camunda Modeler for BPMN. `Camunda Modeler Download Page <https://camunda.com/download/modeler/>`_

.. sidebar:: BPMN Modelers

  There are a number of modelers in existence. SpiffWorkflow uses Camunda because it has extensions that allow user tasks to include forms with questions. Other modelers may work with SpiffWorkflow, however some features may not be supported.


A Simple Workflow
-----------------

All BPMN models have a start event and at least one end event. The start event is represented with a single thin border circle. An end event is represented by a single thick border circle.

The following example also has one task, represented by the rectangle with curved corners.


.. figure:: images/simplestworkflow.png
   :scale: 25%
   :align: center

   A simple workflow.


The sequence flow is represented with a solid line connector. When the node at the tail of a sequence flow completes, the node  at the arrowhead is enabled to start.


More complicated Workflow
-------------------------

.. figure:: images/plgateway.png
   :scale: 25%
   :align: center

   A workflow with a gateway


In this example, the diamond shape is called a gateway. It represents a branch point in our flow.  This gateway is an exclusive data-based  gateway (also called an XOR gateway). With an exclusive gateway, you must take one path or the other based on some data condition. BPMN has other gateway types.

The important point is that we can add a branch in the workflow **without** creating an explicit branch in our Python code.


.. sidebar:: BPMN Resources

  This guide is a mere introduction to how to get started with BPMN allowing someone to get started with
  SpiffWorkflow and start using it to write programs that perform a workflow and let SpiffWorkflow do the heavy lifting.
  For a more serious modeling, we recommend looking for more comprehensive resources. We have used the books by Bruce
  Silver as a guide for our BPMN modeling.

  .. image:: images/bpmnbook.jpg
     :align: center


Goals of a Good BPMN:
---------------------
1. Correctness. This means semantic correctness – the  shapes and symbols are used correctly, as well as structural correctness, so that each activity corresponds 1:1 with a process instance.

2. Clarity. The process logic should be clear from the diagrams alone, without prior  knowledge of how the process works or even of the terminology employed.

3. Completeness. It should be possible to tell from a single glance what the instance represents, how the process  starts, where it can end, and what interactions there are with external entities.

4. Consistency. Given the same set of process information, all modelers should  create (more or less) the same process model.

