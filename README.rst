spiff-example-cli
==============

.. sidebar:: Note

   As of writing, this documentation has not been tried on Windows

This is the documentation and example repository for the SpiffWorkflow BPMN workflow engine.
Below is a brief outline on how to get started using this documentation - which in itself is designed as a tool for
getting started with Spiffworkflow.

Clone this repository
------------------

.. code:: bash

   git clone https://github.com/sartography/spiff-example-cli.git

Set up virtual environment
--------------------------

.. code:: bash

    cd spiff-example-cli
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

Example BPMN and DMN files can be found in the `bpmn` directory of this repository.
There are several versions of a product ordering process of variying complexity located in the
`bpmn/tutorial` directory of the repo which contain most of the elements that SpiffWorkflow supports.  These
diagrams can be viewed in any BPMN editor, but many of them have custom extensions created with
`bpmn-js-spiffworflow <https://github.com/sartography/bpmn-js-spiffworkflow>`_.

Loading Workflows
^^^^^^^^^^^^^^^^^

To add a workflow via the command line and store serialized specs in JSON files:

.. code-block:: console

   ./runner.py -e spiff_example.spiff.file add \
      -p order_product \
      -b bpmn/tutorial/{top_level,call_activity}.bpmn \
      -d bpmn/tutorial/{product_prices,shipping_costs}.dmn

Running Workflows
^^^^^^^^^^^^^^^^^

To run the curses application using serialized JSON files:

.. code-block:: console

   ./runner.py -e spiff_example.spiff.file

Select the 'Start Workflow' screen and start the process.

## License
GNU LESSER GENERAL PUBLIC LICENSE
