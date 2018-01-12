######################################
Manchester Research IT Sphinx Template
######################################

Pre-requirement
===============

To use this template made for python3 you need to have the pre-require python package:

- python-sphinx


On all the major operating system where python is installed you can install the sphinx package using easy-install::

    easy-install -U sphinx

or pip::

    pip install sphinx --user

You can also install anaconda and use conda to do the installation using conda package manager::

    conda install sphinx

On linux you can use the system package to install them.


Get the template
================

Download the template::

    git clone XXXXX

Sphinx syntax
=============

`Sphinx documentation system <http://www.sphinx-doc.org>`_ is based on the `reStructuredText syntax <http://www.sphinx-doc.org/en/stable/rest.html>`_
which is very similar to Markdown.

Recently the possibility to use Markdown instead (or in complement) of reStructuredText using the Marlkdown flavor `CommonMark <http://recommonmark.readthedocs.io/en/latest/index.html>`_. 
We should notice that the Markdown syntax is more limited than the reStructuredText one.

It is possible to mix reStructuredText and Markdown files in the same Sphinx documentation.

How-To
======

To create the documentation a Makefile is provided. 
Sphinx allowed to create the documentation in multiple format 
(html, pdf, epub...). 
There are also an option in the makefile to create a documentation 
used on `pages on Github <https://pages.github.com/>`_.

To use that possibility, adapt the **GITHUBREPO** variable 
in the Makefile to poing to the Github repository of the project. 
When this is done the option *gh-pages* in the Makefile will create
a new directory on the same level than the documention directory with the suffix *-html*

.. note::
    this can be change by defining the variabe **GITHUBBUILDDIR** 
    in the Makefile file.

the option *gh-pages* will create the html documentation and upload it on the *gh-pages* on Github.::

    make gh-pages

To create an epub file::

    make epub

To create a pdf file, the best option is to use::

    make latexpdf

but that implied the installation and use of LaTeX.
