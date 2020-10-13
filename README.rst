SpiffExample
==============
This is the documentation and example repository for the SpiffWorkflow BPMN workflow engine. While the knipknap version of this is the master, there are many (many) changes that are only in the sartography repository.

Below is a brief outline on how to get started using this documentation - which in itself is designed as a tool for getting started with Spiffworkflow.

How to use and extend
-----------------------

To interact with and extend this documentation you need:

.. sidebar:: Note

   As of writing, this documentation has not been tried on Windows

1) this repository
2) a supported version of Python 3 (as of the writing, that means >= 3.5) - Python 2 is not supported
3) a virtual environment set up

Set up repository
------------------

Just use git clone to clone this repository

.. code:: bash

   git clone https://github.com/sartography/SpiffExample.git

Set up virtual environment
--------------------------

Python now includes virtualenv in the standard library.

.. code:: bash

    cd SpiffExample
    python3 -m venv venv

This will setup a Python3 virtual environment.

Please note, you will need to edit a line in SpiffExample/docs/Makefile to match your version of Python. Look for the line below and change it to match your version of Python

.. code::

   apidoc:
	   sphinx-apidoc -d5 -Mefo . ../venv/lib/python3.7/site-packages/SpiffWorkflow

Enable the virualenv we just created.

.. code:: bash

    my-prompt$ source ./venv/bin/activate
    (venv) my-prompt$


Install Requirements
--------------------

Now that we have the Python virutal environment set up, let's get our requirements installed.

.. code:: bash

    pip3 install -r requirements.txt

This should get us all of the tools we will need to run the examples - Any of the .py files should be able to be run
in the SpiffExample main directory

.. code:: bash

    (venv) my-prompt$ python ExampleCode.py
    Where are you going? (Options: cabin, hotel, camping)? hotel
    ['location']
    Do you like spam? yes
    ['spam']
    {'location': 'hotel', 'spam': 'yes'}
    {'location': 'hotel', 'spam': 'yes'}


Build the Documentation
-----------------------

Next let's make sure we can build the documentation

.. code:: bash

   cd docs
   make apidoc
   . . .  a bunch of output . . .
   make html
   . . . a bunch more output . . .

Assuming everything went well, you can now open the following file in your browser:

.. code::

    <yourdirectory>/SpiffExample/docs/_build/html/index.html

and be able to view all of the documentation with your browser.

Extending the documentation
---------------------------

Extending the documentation is really just a matter of editing and adding .rst files in the RestructuredText format and adding the associated images to the docs/images folder

.. sidebar:: Note

   At the time of writing, the version of SpiffWorkflow is tied to a specific branch - This should change once the branch has been merged into master. At that time the requirements.txt file should be changed in this repository so it is important to pull this from github every so often.


For updating the actual SpiffWorkflow API documentation, all you should have to do is re-install the SpiffWorkflow through spiff using pip

.. code:: bash

    pip3 install --upgrade -r requirements.txt

and then re-running the make commands above - this will re-generate all of the api documents. The API documentation is taken from the comments within the SpiffWorkflow source code.
