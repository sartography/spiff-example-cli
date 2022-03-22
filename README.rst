SpiffExample
==============

.. sidebar:: Note

   As of writing, this documentation has not been tried on Windows

This is the documentation and example repository for the SpiffWorkflow BPMN workflow engine.
Below is a brief outline on how to get started using this documentation - which in itself is designed as a tool for
getting started with Spiffworkflow.

Clone this repository
------------------

.. code:: bash

   git clone https://github.com/sartography/SpiffExample.git

Set up virtual environment
--------------------------

.. code:: bash

    cd SpiffExample
    python3 -m venv venv
    source ./venv/bin/activate

Install Requirements
--------------------

.. code:: bash

    pip3 install -r requirements.txt


Using the Application
---------------------

This application is intended to accompany the documentation for `SpiffWorkflow
<https://spiffworkflow.readthedocs.io/en/latest/index.html>`_.  Further discussion of
the models and application can be found there.

Models
^^^^^^

Example BPMN and DMN files can be found in the :code:`bpmn` directory of this repository.

Running a Workflow
^^^^^^^^^^^^^^^^^^

To execute the complete workflow:

.. code:: bash

   ./run.py -p order_product \
       -d bpmn/product_prices.dmn bpmn/shipping_costs.dmn \
       -b bpmn/multiinstance.bpmn bpmn/call_activity_multi.bpmn

To restore a saved workflow:

.. code:: bash

   ./run.py -r <saved_workflow_file>

To see all program options:

.. code:: bash

   ./run.py --help

