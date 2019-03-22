.. _howto:

######
How-To
######

Usage
=====
Before using datlight to upload data,  it is necessary to add some metadata
which will be used by the data repository to create the data record.

Zenodo Metadata
---------------

Zenodo requires a specific set of metadata which should be included 
with **every** data record.

Zenodo metadata which should **always** be include in any metadata
are:

- title
- description
- upload_type
- creators
- access_right
- license

some additional values may be needed depending on the values of the
*upload_type* and *access_right*.

If:

- *upload_type* is *publication* the *publication_type* keyword is required.
- *upload_type* is *image* the *image_type* keyword is required.
- *access_right* is *embargoed* the *embargo_date* keyword is required.
- *access_right* is *restricted* the *access_conditions* keyword is required.

The `Zenodo API <http://developers.zenodo.org/#representation>`_
documentation gives all of the accepted metadata keywords.

These metadata muse be provided in a file with the
`YAML format <http://yaml.org/>`_ which is described below.

`YAML Format. <http://yaml.org>`_
---------------------------------


Basics
^^^^^^

YAML files can *optionally* begin with `---` and end with `...` That
indicates the start and end of a document.

Comments
^^^^^^^^

It is possible to add comments in a yaml file. The character used to
declare that everything after that character is considered as comment
is **#** (similar to python):

.. code-block:: yaml
    
  # This is a comment in yaml
  title: a title # <- The line read up to this character.

Key-value pairs
^^^^^^^^^^^^^^^

YAML stores information using key value pairs.The key describes what the data
is and the value is the data. To describe the title of a record, a key value
pair might look like::

.. code-block:: yaml

  title : A title for our data

A string can be written over multiple lines in three different ways:

.. code-block:: yaml

  title : "A title for our data
          which extend on multiple lines using quote"


.. code-block:: yaml

  title : |
          A title for our data
          which extend on multiple lines "Literal Block Scalar" |
          will include the newlines and any trailing spaces.

.. code-block:: yaml

  title : >
          A title for our data
          which extend on multiple lines "Literal Block Scalar" > 
          will fold newlines to spaces; it’s used to make what would
          otherwise be a very long line easier to read and edit. 

In either case the indentation will be ignored.

Values may be more complex than just a text. YAML allows lists or 
combinations of lists and key-pair values. YAML will consider
lines prefixed with more spaces than the parent key as being are contained
inside tje parent key, All child keys must be prefixed with the same 
amount of spaces to belong to the same level.

Below are some examples of this.

A list in YAML where the key has the name *alist* and the value is a
list of three elements:

.. code-block:: yaml

  alist:
    - first element
    - second element.
    - third element

For datalight we can use it to list, for example, the *creators* of
the data:

.. code-block:: yaml

  creators:
    - name: Jane Doe
    - name: Alan Smith
    
The value associated witgh a key can be a list the list may also contain
more key-value pairs. In this example there are multiple creators each of whom has
an affiliation:

.. code-block:: yaml

  creators:
    - name: Jane Doe
      affiliation: University of Neverland

    - name: Alan Smith
      affiliation: University of Shire

This is the description of the YAML format needed to create a metadata
file to upload on our favorite data repository.

In the following section, we are going to see different examples of
valid metadata for the Zenodo repository.

Zenodo metadata examples
------------------------

Minimal
^^^^^^^

.. code-block:: yaml

  title: A small title describing our data
  
  description: "Description of the dataset that 
                is going to be upload"
                
  upload_type: dataset
  
  creators:
    - name: Jane Doe
      affiliation: University of Neverland

    - name: Alan Smith
      affiliation: University of Shire
      
  access_right: open
  
  license: CC-BY-4.0


This metadata will be sufficient to upload successfully a dataset on
Zenodo.


A more complete set of metadata
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

  title: "A very long 
         title"
  
  description: "Description of the data"
  
  creators:
      - name: John Doe
        affiliation: The University of Neverland
  
      - name: Jane Doe
        affiliation: The University of Shire
        orcid: 0000-0000-0000-0007
  
  upload_type: dataset
  
  access_right: restricted
  
  access_conditions: "Only available through contact to myproject project"
  
  communities:
      - identifier: mycommunity
  
  thesis_supervisors:
      - name: Jane Doe
        affiliation: The University of Shire
        orcid: 0000-0000-0000-0007
  
  contributors:
      - name: Alan Smith
        affiliation: The University of Mars
        orcid: 0000-0000-0000-0005
        type: ContactPerson
  
  license: CC-BY-4.0
  
  keywords:
      - MyProject
      - another_keyword
  
  notes: "If grant number is not reconize by OpenAir this is where you
         indicate the information related to the grant (as mention in
         the Zenodo documentation)."
  
  # If project known in the OpenAir
  #grants:
  #    id:
  
  language: eng
  
  subjects:
      - term: Fantasy and SF
        identifier: http://id.loc.gov/authorities/subjects/sh000000
        scheme: "url"


An example of a metadata file where the record is emboargoed until a certain date:

.. code-block:: yaml

  title: "A very long 
         title"
  
  description: "Description of the data"
  
  creators:
      - name: John Doe
        affiliation: The University of Neverland
  
      - name: Jane Doe
        affiliation: The University of Shire
        orcid: 0000-0000-0000-0007
  
  upload_type: dataset
  
  access_right: embargoed
  
  embargo_date: 2022-12-31
  
  communities:
      - identifier: mycommunity
  
  thesis_supervisors:
      - name: Jane Doe
        affiliation: The University of Shire
        orcid: 0000-0000-0000-0007
  
  contributors:
      - name: Alan Smith
        affiliation: The University of Mars
        orcid: 0000-0000-0000-0005
        type: ContactPerson
  
  license: CC-BY-4.0
  
  keywords:
      - MyProject
      - another_keyword
  
  notes: "If grant number is not reconize by OpenAir this is where you
         indicate the information related to the grant (as mention in
         the Zenodo documentation)."
  
  # If project known in the OpenAir
  #grants:
  #    id:
  
  language: eng
  
  subjects:
      - term: Fantasy and SF
        identifier: http://id.loc.gov/authorities/subjects/sh000000
        scheme: "url"



Datalight usage
===============

When you have a file or directory containing your data and a proper
metadata file associated, you can upload your data to Zenodo data
repository.


.. code-block:: bash

  $ python main.py file_name <name of the file which contains zenodo metadata>
  $ python main.py directory <name of the file which contains zenodo metadata>
  

The second argument should point to the file which contains
the Zenodo metadata as described above.

Publishing the data at the upload time
--------------------------------------

By default the data will be upload on the data repository but 
they will not be published. You can ask datalight to do it using 
the argument publish=True::

  $ python main.py file_to_upload.txt metadata.yaml publish=True
  
In this example file_to_upload.txt will be uploaded with the 
information found in the metadata.yaml and the record will be
published on the Zenodo.

.. warning::

    data which have been published **cannot** be removed. 
    They will be present forever on the data repository.
    
The finalisation of the data and the publication can also be done 
through the web interface on `Zenodo <https://zenodo.org>`_. When you 
upload a file with datalight using your token it associates it with your
account and so you can see it by logging in to Zenodo with your username 
and password.

Testing the upload
------------------

If you prefer to test the upload of your data, Zenodo provides 
a sandbox website. Tis is just like the real website except data is 
regularly deleted. As such you can use it for testing purposes. To upload data
to the sandbox you need to use the sandbox=True argument::

  $ python main.py file_to_upload.txt -m metadata.yaml sandbox=True
  
will upload (but not publish) the data on the `sandbox website <https://sandbox.zenodo.org>`_.

.. warning::

    1. To be able to use the sandbox you need to create an account and get a 
    token from: https://sandbox.zenodo.org. This is described in the .. _prerequisites: section
    of the documenation. 
    
    2. Zenodo sandbox is sometimes unreliable and the tests can fail with an error 500.
       That does not necessarily mean that the upload didn't work but that datalight did not
       get a valid resposne from the website.




