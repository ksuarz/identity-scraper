# identity-scraper
Grabs user identity information from websites.

## Virtual Environment
You need to install the Python dependencies in order to use the code. First,
make sure you have `python-virtualenv` installed on your computer. If you have
`python-pip`, you can do

    $ pip install virtualenv

though you may need root access for a global install.

Then, create a virtual environment with

    $ virtualenv --no-site-packages venv

This will create a place for you to install the Python dependencies. To use it,
you must activate it like so:

    $ source venv/bin/activate

Now, install the dependencies listed in `pip.req`:

    (venv)$ pip install -r pip.req

The virtual environment needs to be activated for the scraper to work. When
you're done, you can deactivate it like so:

    (venv)$ deactivate
