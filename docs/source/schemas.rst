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


Construction of the schema
----------------------------

Schemas are written in JSON.

At the beginning of the schema, some keywords provide information about the schema.

The **$schema** keyword indicates that this is a JSON schema and not just a random bit
of JSON. The provided URL gives the schema which defines the schema (how delightfully
meta!).

The **$id** keyword declares a unique identifier for this schema. It is good to put the
url as something related to the project. Perhaps a homepage::

    {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "https://github.com/LightForm-group/datalight/tree/master/datalight/schemas/zenodo",
        "title": "Zenodo API upload metadata schema"
        "description": "When uploading to Zenodo via the API there is no schema to validate the supplied metadata.
         This is an attempt to create such a schema",


Since the schema itself is written in JSON, it can be validated against a schema which
describes schemas. In this case we use the
`JSON Schema V7 <http://json-schema.org/draft-07/schema#)>`_

The JSON Schema schema requires **title** and **description** annotation keywords. These are
purely descriptive and do not add constraints to the data.

The main data of the schema is then provided by the **properties** field. This has
sub-keywords describing each valid field.

Each keyword is defined with a type and this type is used to validate the
keyword. The valid types and their equivalents in Python are::

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

It is possible to force the presence of some metadata keywords by using
the keyword *required* which will take a list (an array) containing the name 
of the keyword that **must** be present.

Zenodo minimal set of metadata
----------------------------------

Zenodo metadata which should always be include in any metadata are:

- title
- description
- upload_type
- creators
- access_right (default: open)
- license: (default: cc-by-0])

Although **access_right** and **license** are strictly not required due to them taking
default values. They have been made mandatory in the schema to simplify the code. Since
these are important values, it is good practice to set them manually anyway.

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


Limitations of the JSON schema
-----------------------------------------

There is a major limitation in the JSON schema draft 7 which does not allow
the use of the *additionalProperties: false* keyword with the allOf command since
introspection into the allOf groups is not valid. This is explained at:
https://json-schema.org/understanding-json-schema/reference/combining.html#allof

This wil be fixed in the JSON schema draft 8 when this is released some time in 2019.
In the interim, the Python script will be required to check that there are no additional
values other than those allowed by the Zenodo API.

In addition, the **license_type** keyword has somewhat complex restrictions. If the
**access_right** keyword is "open" or "embargoed" then **license_type** must be an open
license as specified at: https://licenses.opendefinition.org/
This is also checked in the Python code and not in the schema.