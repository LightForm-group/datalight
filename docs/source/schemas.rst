Use of a schema to validate metadata
###########################################

Motivation
-------------

When a record is uploaded to Zenodo, some metadata is required. When uploading via
the API, the metadata is provided in JSON format.

A schema is a way of validating structured data to ensure that it includes
required fields. Although Zenodo has a schema to describe the metadata it stores
about a **deposited** record, it does not have a schema to validate the metadata
required when uploading data.

Since Datalight will involve creating a separate metadata template for each record type
that will be uploaded, it is desirable that we have a schema to validate these templates.

A schema has therefore been created as part of this project by analysing the Zenodo
API documentation. Since the schema is based on the API it may need to be updated if
the API is updated. However, it seems that the API is relatively stable so this
shouldn't be much of a problem.

Choice of json/YAML schema
----------------------------

Since JSON is not easily human readable, it was decided to write the Zenodo upload
metadata schema in YAML. YAML is similar to JSON but is more easily readable and flexible,
allowing things like comments. Python allows seamless conversion between JSON and YAML.

This means that technically we are using a YAML schema which is converted to JSON
at run time.

Construction of the schema
----------------------------

The file starts with::

    %YAML 1.1

which states the version of YAML used.

YAML files can *optionally* begin with `---` and end with `...` 
That indicates the start and end of a document.

After that, three lines should be present, they are not *required* but 
it is considered good practice to include them::


    $schema: "http://stsci.edu/schemas/yaml-schema/draft-01"
    id: "https://zenodo.org/schemas/zenodo/metadata-1.0.0"
    tag: "tag:zenodo.org:zenodo/metadata-1.0.0"


Since the schema itself is written in JSON, it can be validated against a schema which
describes schemas. In this case we use the `YAML definition schema
<https://asdf-standard.readthedocs.io/en/latest/schemas/stsci.edu/yaml-schema/draft-01.html)>`_

The YAML definition schema requires the fields:

- title - The title of the schema
- description - A description of the purpose of the schema.
- example - An example of the usage of the schema

The main data of the schema is then provided by the **properties** keyword. This has sub
keywords describing each valid field.

Each keyword is defined with a type and this type is used to validate the
keyword. The valid types and their equivalents in python are::

| JSON          | Python    |
| ------------- | --------- |
| object        | dict      |
| array         | list      |
| string        | unicode   |
| number (int)  | int, long |
| number (real) | float     |
| true          | True      |
| false         | False     |
| null          | None      |

here some example::


    properties:
        a_string:
            type: string
     
    an_array:
        type: array
            items:
                type: string
      
    a_dictionary:
        type: object
            properties:
                key1:
                    type: string
                key2:
                    type: number


It is possible to create complex schemas using the keywords:

- anyOf
- allOf
- oneOf

It is also possible to force the presence of some metadata keywords by using 
the keyword *required* which will take a list (an array) containing the name 
of the keyword that **must** be present.

Zenodo minimal set of metadata
----------------------------------

Zenodo metadata which should **always** be include in any metadata are:

- title
- description
- upload_type
- creators
- access_right (default: open)
- license: (default: cc-by-0])

Some additional values may be needed depending on the values of
the *upload_type* and *access_right*.

- If *upload_type* is *publication*, the *publication_type* keyword is required.
- If *upload_type* is *image*, the *image_type* keyword is required.
- If *access_right* is not present or is *open* (default value),
  the *license* keyword will be set to *cc-by-4.0* if *license* is not explicitly set.
- If *access_right* is *embargoed* this requires the *license*
  (or *license* will be set to *cc-by-4.0*) and *embargo_date* keywords
- If *access_right* is *restricted*, the *access_conditions* keyword is required.

The `Zenodo API <http://developers.zenodo.org/#representation>`_ documentation
presents all of the accepted metadata keywords.


Important limitation of the JSON schema
-----------------------------------------

There is a major limitation in the JSON schema which does not allow
the use of the *additionalProperties: false* keyword with an expected
behaviour, i.e. that only the properties (keywords) listed in the schema
are the one allowed by the schema.
See: https://spacetelescope.github.io/understanding-json-schema/reference/combining.html#combining
for more information.

This limitation implied that we need to verify the presence of extra keyword 
outside the JSON schema. This verification is crucial since Zenodo upload will
failed if the metadata are not correct.