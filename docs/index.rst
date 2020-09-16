.. SpiffWorkflow-BPMN Documentation documentation master file, created by
   sphinx-quickstart on Fri Sep 11 12:40:08 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Business Process Model and Notation Documentation's
============================================================

 toctree::
   :maxdepth: 2
   :caption: Contents:


Indices and tables
==================

How to Create Your Own BPMN:
============================

Making your first BPMN can be overwhelming, here we can will go over an example step by step and create a simple flow together with as many attributes as possible. In our example and through the documentation we will continue to use Camunda Modeler as our application for modeling BPMN. (link on how to install Camunda Modeler)

The first step in anything in life is getting started, with BPMN you represent the start of a flow with a single thin border circle, also known as a start event. In some cases there are symbols inside the start event called triggers. These triggers identify the “meaning” of the processes start.
Let’s look at an example: A family is trying to buy enough food for a week at a cabin.
The start of this decision flow would look like this:



All though this is th last step to putting our flow together, we are going to quickly go over the end event. The end event is shown with a single thick border around a circle. Much like the start event an end event can also have triggers signals to indicate how or when the event ended.
For our example the end will be reached when…
The symbol to represent that will look like this:



﻿This is a very straight forward next step but to make sure that we are all on the same page, we are going to quickly go over the Sequence flow, drawn in the diagram as a solid line connector. It represents the sequential  execution of process steps:
When the node at the tail of a sequence flow completes, the node  at the arrowhead is enabled to start.
For our example the sequence flow will be used many times the first being attached to the start event:


Now we need to tell the flow what it needs to do, this is down by drawing a rounded rectangular shape. These are called activities which represent an action.
In our example the first few actions that needs to be performed is gathering data on the family.
After putting everything together a few task our flow now looks like this:





Each of these activities will have a task assigned to them very shortly.
First we need to counite the flow, the first thing to consider is that there is a possibility that the family is not going on a trip where they need to bring their own food. In that case the flow will change. Like such:








From the above flow you can see that a new symbol has been introduced. ﻿The diamond shape is called a gateway, It represents a branch point in our flow.  There a few other gateways that BPMN utilizes but the one used in our example is called an exclusive data-based  gateway (also called an XOR gateway). When we use this gateway we are saying that you must take one path or the other based on some data condition.
In our example are the question would be are they going on a trip which requires them to bring their own food? If it’s a yes then they go to the next step, if it’s a no then the flow has ended.





We are foing to take a step back and assign some of these activites with one of the following tasks:
A user task , with the head-and-shoulders icon, means a task performed by a  person.
A script task, is The task defines a script that the engine can interpret. When the task begin, the engine will execute the script. The Task will be completed when the script is completed.
A service task, with the gears icon, means an automated activity. Automated  means when the sequence flow arrives, the task starts automatically, with zero  human intervention. If a person has to just click a button and the rest is automatic,  that is a User task, not a Service task.
Decision task/ Business process task , with the table icon, means that a DMN decision is going to be executed. ﻿A decision transforms the data represented by its inputs into an output value, according to some specified decision logic. The most common  form of decision logic is a decision table.


So let’s add them to our example:







Do you like spam? ---end
User task - about trip (form) (include spam)
Make a form



Family member
Age
How much spam?
1
>6
1 can
2
6-15
2 cans
3
16-35


4




5







Notes for Step one Code:  (step on branch)

In line 21 we have a specialized parse that parsers the Camunda file
In line 22 we add the file in, that we just parsed.
In line 23 we are getting a specification, it is loaded all the file and has complied it down and knows what it got

Image here

In line 25 we are calling BPMNworkflow(spec), which is creating an instances of that workflow. Meaning that is a running working workflow, this allows for it to know states such as where you are and current tasks
In line 27 you are running .do_engine_steps()
Allows you to do things that are not automatic. For example if you have script task that need to run at the start event it will go through and do all the automatic task that are already there.
Line 28 on the other hands calls for all task, and gets it ready to run all tasks.
Need to mention parrel tasks.

Image here
In lines 29 - 35 our code is running through the workflow and seeing there is a task that have a Usertask then it will show form and print out the data from that task. (look at example bellow to see what printed questions look like and what the data at the end looks like.
It also says that if its just a task then it will just print out Complete task.





Notes on Multi- instance (step two example): start a branch once you have code that makes this work!!

Multi-instance activities are represented by three parallel lines at the bottom-center of the activity and task symbol. It’s purpose is to show that the activity occurs for a collection of objects or items.  The number of times that the activity completes is defined by the number of items that exist in the collection. This is different than other looping mechanisms that must check a condition every time the loop completes in order to determine if it should continue looping.

Three vertical lines indicate that the multi-instance activity is non-sequential.  This means that the activity can be completed for each item in the collection in no particular order.

Three horizontal lines indicate that the multi-instance activity is sequential.  This means that the activity must complete for each item in the order that they are received within the collection.




















Goals of a Good BPMN:

Correctness. Now we understand this means not only semantic correctness – the  shapes and symbols are used correctly – but structural correctness as well, so that the  instance of each activity corresponds 1:1 with the process instance.
Clarity. The process logic should be clear from the diagrams alone, without prior  knowledge of how the process works or even of the terminology employed.
Completeness. It should be possible to tell from a single glance how the process  starts, it’s possible end states, what the instance represents, and all interactions with  external entities. The Method actually begins with this.
 Consistency. Given the same set of process information, ideally all modelers should  create (more or less) the same process model. If all members of your project team  follow the Method, understanding each other’s diagrams becomes a breeze. Over ten years of teaching Method and Style, the Method has evolved to become more  mechanical, more standardized in the order of its steps, and this has helped with  consistency.




























The Basics (important vocab, symbols, very much made for referencing and not memorizing):

Symbol/Image:
Definitions:
Start event -- Thin Circle
﻿The thin circle at the start of the process is called a start event. It indicates where the process  starts. The icon inside represents the trigger.
End event --Thick circle
﻿The thick circle at the end is called an end event, signifying the process is complete.
Activities
﻿Rounded rectangles are activities. An activity represents an action, a specific unit of work  performed.
Sequence flows


﻿The solid arrows are called sequence flows. When the element at the tail end is complete, the  flow moves immediately to the element at the head.
Exclusive data-based gateway (more commonly called an XOR gateway)



﻿The diamond shape is called a gateway. It represents a branch point in the flow.  BPMN provides a number of different gateway types, but this one – the exclusive data-based  gateway (more commonly called an XOR gateway), a diamond with no symbol inside – means  take one path or the other based on some data condition. ﻿An X inside the diamond also means the same thing. The spec says just choose one convention –  nothing inside or X inside – and stick with it.


Subprocess



﻿A subprocess is an  activity containing subparts that can be expressed as a process flow. In contrast, a task is an  activity with no defined subparts. A collapsed subprocess is rendered as a single activity with a  [+] marker. The subprocess details are normally drawn in a separate hyperlinked diagram.
Parallel gateway (also called an AND-gateway)



﻿This uses a gateway with a + symbol inside, in fact two of  them. This is a parallel gateway, also called an AND-gateway. A parallel gateway with one  sequence flow in and two or more out is called a parallel split or AND-split. It means  unconditionally split the flow into parallel, i.e., concurrent, segments.

