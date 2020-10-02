How to use and Extend
===================================

Here is what you need to be able to interact and extend this documentation

.. sidebar:: Note

   As of writing, this documentation has not been tried on Windows

1) this repository
2) some python 3 variant and virtualenv - python 2 is not supported
3) a virtual environment set up

Set up repository
------------------

Just use git clone to clone this repository

.. code:: bash

   git clone https://github.com/sartography/SpiffExample.git

I'll assume you have virutalenv and python3 installed, so let's get our virualenv setup

.. code:: bash

    cd SpiffExample
    virtualenv --python=python3.7 venv

This will get a python 3.7 virtual environment setup. Please note, if you have a different version of python, you
will need to change a line in SpiffExample/docs/Makefile - look for the line below and change it to match your
version of python

.. code::

   apidoc:
	   sphinx-apidoc -d5 -Mefo . ../venv/lib/python3.7/site-packages/SpiffWorkflow

Lets' enable the virualenv that we just created.

.. code:: bash

    my-prompt$ source ./venv/bin/activate
    (venv) my-prompt$

now we know that we have the python virutal environment set up, so let's get our requirements installed

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

Extending the documentation is really just a matter of editing and adding .rst files in the RestructuredText format
and adding the associated images to the docs/images folder

.. sidebar:: Note

   At the time of writing, the version of SpiffWorkflow is tied to a specific branch - This should change once the
   branch has been merged into master. At that time the requirements.txt file should be changed in this repository
   so it is important to pull this from github every so often.


For updating the actual SpiffWorkflow API documentation, all you should have to do is re-install the SpiffWorkflow
through spiff using pip

.. code:: bash

    pip3 install --upgrade -r requirements.txt

and then re-running the make commands above - this will re-generate all of the api documents. The API documentation
is taken from the comments within the SpiffWorkflow source code.

