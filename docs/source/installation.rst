.. highlight:: shell

.. _installation:

============
Installation
============


Stable release
--------------

To install **datalight** as user, run this command in your terminal:

.. code-block:: console

    $ pip install -U datalight --user

This is the preferred method to install **datalight**, as it will
always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_
can guide you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


.. warning::

   This method IS NOT AVAILABLE for alpha and beta version! Use the
   installation from source.

From sources
------------

The sources for datalight can be downloaded from
the `Github repository <https://github.com/gruel/datalight>`_.

the easiest way to install from the source is done by executing
the following command::

    pip3 install -U https://github.com/gruel/datalight/archive/master.zip


You can either clone the public repository:

.. code-block:: console

    $ git clone https://github.com/gruel/datalight

Or download the `tarball`_:

.. code-block:: console

    $ curl -OL https://github.com/gruel/datalight/tarball/master
    $ tar xvf master -C datalight --strip-components=1

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ cd datalight-master
    $ python setup.py install --user

The installer should take care of the missing dependencies, if any.

.. note::

    on MacOS X, the downloaded the file could be uncompress automatically.
    In this case go to the directory were the code is and write::

        pip3 install . --user

.. warning::

    The option ``--user`` will install **datalight** in the user directory
    without the need to be administrator or root on the system.

    Thhat prevent breaking any system-wide packages. It can happen that
    you'll need to manually add the user base's binary directory
    to your ``PATH``.

    On Linux and macOS you can find the user base binary directory by running
    ``python -m site --user-base`` and adding ``bin`` to the end. For example,
    this will typically print ``~/.local`` (with ``~`` expanded to the
    absolute path to your home directory) so you'll need to add
    ``~/.local/bin`` to your ``PATH``. You can set your ``PATH`` permanently by
    modifying ``~/.profile``.

    .. code-block:: console

        echo 'PATH="${PATH}:${HOME}/Library/Python/3.7/bin"' >> ~/.bash_profile
        echo 'export PATH' >> ~/.bash_profile

    On Windows you can find the user base binary directory by running
    ``py -m site --user-site`` and replacing ``site-packages`` with
    ``Scripts``. For example, this could return
    ``C:\Users\Username\AppData\Roaming\Python37\site-packages`` so you would
    need to set your ``PATH`` to include
    ``C:\Users\Username\AppData\Roaming\Python37\Scripts``. You can set your
    user ``PATH`` permanently in the **Control Panel**. You may need to log
    out for the ``PATH`` changes to take effect.

Data files
----------

At the installation, there are data file which are copied in the
directory of the software. For now, it concern the validation of the
metadata needed to upload on the data repository. There are two files:
*schemas/zenodo/metadata-1.0.0.yml* which contains the *YAML* schema
used to validated the metadata for Zenodo and
*schemas/zenodo/opendefinition-licenses.json* which contains the list
of acceptable open source licenses for Zenodo.



.. If there are missing dependencies mention at the installation:

.. .. code-block:: console

       $ python XXX
