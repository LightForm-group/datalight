.. highlight:: shell

.. _installation:

============
Installation
============


Stable release
--------------

To install **datalight**, run this command in your terminal:

.. code-block:: console

    $ pip install datalight

This is the preferred method to install **datalight**, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


.. note::
    This method IS NOT AVAILABLE for alpha and beta version! Use the installation from source.

From sources
------------

The sources for datalight can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone https://github.com/gruel/datalight

Or download the `tarball`_:

.. code-block:: console

    $ curl -OL https://github.com/gruel/datalight/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install --user

The option --user will install **datalight** in the user directory without the need to be administrator or root on the system.

.. _Github repo: https://github.com/gruel/datalight
.. _tarball: https://github.com/gruel/datalight/tarball/master

If there are missing dependencies mention at the installation::

.. code-block:: console

    $ python XXX
