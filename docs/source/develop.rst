.. _develop:

###########################
Informations for developers
###########################

The software was developed in `Python 3 <https://www.python.org/>`_
(v3.5 and above).

Requirements
============

To install the required package for the development::

    pip install -r requirements-dev.txt

That will install the following package:

Needed to use the software:

- `docopt <http://docopt.org/>`_

Needed to build the documentation:

- `sphinx <http://www.sphinx-doc.org/en/stable/#>`_
- sphinx-bootstrap-theme
- numpydoc
- pyqt5

Advised for development:

* to check that that the code source followed `PEP8
  <https://www.python.org/dev/peps/pep-0008/>`_.

- `pylint <https://www.pylint.org/>`_
- flake8

pylint does offer more advise to improve the code and give a note at
the code which reflected some good coding practice.  It is advised to
be as close to 10 as possible.

For the unit test the following packages are needed:

- `pytest <https://docs.pytest.org/en/latest/>`_
- `testfixture <http://testfixtures.readthedocs.io/en/latest/>`_

To run all the tests present in the ``tests`` directory::

    pytest

When modifiying the code it is important to verify that all the tests
are still working. It is also strongly advised to expand them when
adding or modifying the codes.

It is also encouraged to use:

- `pytest-cov <https://pypi.python.org/pypi/pytest-cov>`_
- `coverage <https://pypi.python.org/pypi/coverage>`_

It is also advised to use `tox
<https://tox.readthedocs.io/en/latest/>`_ to automate testing using a
virtual environment.

To use it::

    tox








