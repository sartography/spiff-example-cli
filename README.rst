spiff-example-cli
=================

This is the documentation and example repository for the SpiffWorkflow BPMN workflow engine.
Below is a brief outline on how to get started using this documentation - which in itself is designed as a tool for
getting started with Spiffworkflow.

Clone this repository
---------------------

.. code:: bash

   git clone https://github.com/sartography/spiff-example-cli.git

Using pip
---------

Set up virtual environment
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: bash

    cd spiff-example-cli
    python3 -m venv venv
    source ./venv/bin/activate

Install Requirements
^^^^^^^^^^^^^^^^^^^^

.. code:: bash

    pip3 install -r requirements.txt

Using pipenv
------------

Install Requirements
^^^^^^^^^^^^^^^^^^^^

.. code:: bash

    pipenv sync


Using the Application
---------------------

This application is intended to accompany the documentation for `SpiffWorkflow
<https://spiffworkflow.readthedocs.io/en/latest/index.html>`_.
Further discussion of the models and application can be found there.

Models
^^^^^^

Example BPMN and DMN files can be found in the :code:`bpmn` directory of this repository.

Running a Workflow
^^^^^^^^^^^^^^^^^^

To execute the complete workflow:

.. code:: bash

   ./src/run.py -p order_product \
       -d bpmn/product_prices.dmn bpmn/shipping_costs.dmn \
       -b bpmn/multiinstance.bpmn bpmn/call_activity_multi.bpmn

To restore a saved workflow:

.. code:: bash

   ./src/run.py -r <saved_workflow_file>

To see all program options:

.. code:: bash

   ./src/run.py --help

On Windows, you may need to prepend the python executable to those commands.
If using :code:`pip`, use :code:`python -m src.run [args]`.
If using :code:`pipenv` use :code:`pipenv run python -m src.run [args]`.

Run in docker
^^^^^^^^^^^^^

.. code:: bash

   ./bin/run_in_docker

It will use the pip installation method. If you want pipenv, replace the `Dockerfile`
with the one named `Dockerfile_pipenv`.

License
-------
GNU LESSER GENERAL PUBLIC LICENSE
