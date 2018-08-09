# Process to create the zenodo json schema

## Motivation

During the development of a software for a research project, a need for 
a tool which validate the metadata that will be send when doing created 
(or updated) a record.
The users could obtain information on the validity of their metadata related 
to Zenodo. 
In addition to the Zenodo validation, it is possible to create using 
the same method a tool which will validate specific metadata asked by a project. 


## Choice of json schema

The main reasons to choose json schema instead of XML/XLST to validate 
the metadata is that Zenodo is using json as tool to communicate. 
Unfortunately, json, if useful as communication tool, is not really human
readable and it was decided to go through in intermediate step by writing 
the metadata in YAML format and we did the same for the json schema.

The programming language that it is used in our development, python, allowed 
a seamless conversion from one format to the other.
YAML is similar to python in term of forcing the user to format the code. 
Another main disadvantage of JSON is the lack of comments which is present
in the YAML format. 

So technically we are using in reality a YAML schema which is converted to 

## Construction of the schema

The file should start with::

    %YAML 1.1

which state the version of YAML used.

YAML files can *optionally* begin with `---` and end with `...` 
That indicates the start and end of a document.

After that, three lines should be present, they are not *required* but 
it is considered good practice to include them:

```yaml
$schema: "http://stsci.edu/schemas/yaml-schema/draft-01"
id: "https://zenodo.org/schemas/zenodo/metadata-1.0.0"
tag: "tag:zenodo.org:zenodo/metadata-1.0.0"
```

The main part of the yaml schema is done inside the keyword **properties**.
This 

After that you can add any keywords you want like but we are going to use 
the same default keys used in the 
[YAML definition schema](https://asdf-standard.readthedocs.io/en/latest/schemas/stsci.edu/yaml-schema/draft-01.html):

- title
- description
- example

The most important keywords which should be present in any schema definition (to be meaningful) is:

- properties

this keywords is a list of all the different metadata which are defining 
the schema.

Each keyword is define with a type and this type is used to validate
keyword. The type are the one existing in json. 

This table list the json file and their equivalence in python:

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

here some example:

```yaml
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
```

It is possible to create complex schema using the specific keywords:

- anyOf
- allOf
- oneOf

It is also possible to force the presence of some metadata keywords by using 
the keyword *required* which will take a list (an array) containing the name 
of the keyword that **must** be present.

## Zenodo minimal set of metadata

Zenodo metadata which should **always** be include in any metadata are:

- title
- description
- upload_type
- creators
- access_right (default: open)
- license: (default: cc-by-0])

some additional values can be needed depending on the values of 
the *upload_type* and *access_right*.

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

[Zenodo API](http://developers.zenodo.org/#representation) documentation 
present all the different metadata keywords accepted by it. 
In any doubt this is the reference pages. 

Until Zenodo is providing their own schema there are no
possibility to be sure that the schema is up-to-date. Datalight developer will 
try to keep up-to-date and be sure that any change in the Zenodo API will be 
reflected in the yaml schema.

##  Important limitation of the json schema

There are a major limitation in json schema which does not allows 
the use of the *additionalProperties: false* keyword with an expected
behaviour, i.e. that only the properties (keywords) listed in the schema
are the one allowed by the schema.
See: https://spacetelescope.github.io/understanding-json-schema/reference/combining.html#combining
for more information.

This limitation implied that we need to verify the presence of extra keyword 
outside the json schema. This verification is crucial since Zenodo upload will
failed if the metadata are not correct.