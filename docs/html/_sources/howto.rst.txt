.. _howto:

######
How-To
######

Usage
=====

Before to use the software it is needed to create the file which will
be use to fill the necessary metadata needed by the data repository to
create the data record.

Zenodo Metadata
---------------

Zenodo data repository is asking for a very specific informations
which should be included in **every** data record.

Zenodo metadata which should **always** be include in any metadata
are:

- title
- description
- upload_type
- creators
- [access_right] (optional, default: open)
- [license] (optional, default: cc-by-0])

some additional values can be needed depending on the values of the
*upload_type* and *access_right*.

If:

- *upload_type* is equal to *publication* implied the presence of
  *publication_type* metadata keyword.
- *upload_type* is equal to *image* implied the presence of the keyword
  *image_type*
- *access_right* is not present or equal to *open* (default value),
  it implied the presence of *license* keyword if not *license* will be:
  *cc-by-4.0*
- *access_right* is equal to *embargoed* implied the presence of *license*
  (or *license* will be set to *cc-by-4.0*) and *embargo_date* keywords
- *access_right* is equal to *restricted* implied the presence
  of *access_conditions* keyword

`Zenodo API <http://developers.zenodo.org/#representation>`_
documentation present all the different metadata keywords accepted by
it. In any doubt this is **the** reference page.

Until Zenodo is providing their own schema there are no possibility to
be sure that the schema is up-to-date. Datalight developer will try to
keep up-to-date and be sure that any change in the Zenodo API will be
reflected in the yaml schema.

The associated informations to the records has to be provided in a
text file following the `YAML format <http://yaml.org/>`_.

We decided to use YAML format because it is easier for humans to read
and write than other metadata formats like XML or JSON.

This format is describe in the following paragraph.

`YAML Format. <http://yaml.org>`_
---------------------------------


Basics
^^^^^^

.. warning::

  Using a WYSIWYG (Microsoft Word) to create or edit a YAML file is
  not advised.

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

YAML keep informations using a key which is associated to a value (it
is a called hashtable or in python dictionary):

.. code-block:: yaml

  title : A title for our data

A string can be extended on multiple lines by three differents way:

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

Value can be more complex than just a string but list or combinaison
of list and key-pair values. YAML will consider that lines prefixed
with more spaces than the parent key are contained inside it;
Moreover, all lines must be prefixed with the same amount of spaces to
belong to the same map

We are going to see some examples to understand what it means in the
context of datalight metadata.

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
    
The value associated to a key can be a list but also another hashtable
to add more informations. Here an example where we are providing the
name for every creators but also the affiliation:

.. code-block:: yaml

  creators:
    - name: Jane Doe
      affiliation: University of Neverland

    - name: Alan Smith
      affiliation: University of Shire

Every element of the list will have two informations (name and
affiliation).

This is the description of the YAML format needed to create a metadata
file to upload on our favorite data repository.

In the following section, we are going to see different examples of
valide metadata for Zenodo repository.

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


This metadata will be sufficient to upload successfully a dataset on
Zenodo.

Zenodo will add the following one which will have their default value:

.. code-block:: yaml

  access_right: open
  license: CC-BY-4.0

A more complete (realistic) one
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
  
  access_conditions: "Only available through contact to myroject project"
  
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


or one where data are emboargoed until a certain date:

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

When you have a file(s)/directory containing your data and a proper
metadata file associated, you can upload your data to Zenodo data
repository.


.. code-block:: bash

  $ datalight file1 -m <name of the file which contains zenodo metadata>
  $ datafile file1 file2 -m <name of the file which contains zenodo metadata>
  $ datafile directory -m <name of the file which contains zenodo metadata>
  

The **--metadata** argument should point to the file which contains
the Zenodo metadata as describe above.

.. warning::

    **-m <metadata_file>**  or **--metadata=<metadata_file>** argument 
    is **not optional**. It has to be provided.

You can add as many argument as you want and they should be the name
of file or the name of a directory which contains the data you want to
upload to the data repository.

Example::

  $ datalight metadata.yaml -m metadata.yaml
  
Where *metadata.yaml* will contains the following values:

.. code-block:: yaml

  title: A small title describing our data
  
  description: "Description of the dataset that 
                is going to be upload"
  
  upload_type: dataset
  
  creators:

    - name: Alan Smith
      affiliation: University of Shire
  
In this example, the file containing the metadata will be upload as a
data file and store on Zenodo.

Publishing the data at the upload time
--------------------------------------

By default the data will be upload on the data repository but 
they will not be published. You can ask datalight to do it using the option
**-p** or **--publish**::

  $ datalight metadata.yaml -m metadata.yaml -p
  
or::

  $ datalight metadata.yaml -m metadata.yaml --publish
  
The file metadata.yaml will be upload with the information found 
in the file containing the metadata (here the same file) 
and will be publish on the data repository.

.. warning::

    data which have been publish **cannot** be removed. 
    They will be present forever on the data repository.
    
The finalisation of the data and the publication can always be done through the web interface provided by Zenodo: `Zenodo webinterface <https://zenodo.org>`_

Testing the upload
------------------

If you prefer to test the upload of your data, Zenodo is providing 
a sandbox and you can use it for the tests by using the option **--sandbox**::

  $ datalight metadata.yaml -m metadata.yaml --publish --sandbox
  
will publish the data on the `sandbox website <https://sandbox.zenodo.org>`_.

.. warning::

    1. To be able to use the sandbox you need to create the token from: https://sandbox.zenodo.org.
    
    2. The token should be copied in the file **.zenodo** with 
    the keyword *[sandbox.zenodo.org]* e.g.::
    
    
      [sandbox.zenodo.org]
      lightForm = <zenodo sandbox token>

      [zenodo.org]
      lightform = <zenodo token>

    3. Zenodo sandbox is not really reliable and the tests can failed with an error 500.
       That does not necessariliy means than the upload didn't work but 
       that at least one step where missing. 
       That can create a record on the sandbox that you will have to clean manually.




