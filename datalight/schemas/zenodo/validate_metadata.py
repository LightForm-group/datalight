"""This script validates a Datalight metadata template against the schema."""

import yaml
import jsonschema
import pathlib

script_path = pathlib.Path(__file__).parent.parent.parent.parent
metadata_path = script_path / pathlib.Path("tests/metadata/minimum_valid.yml")

with open('zenodo_upload_metadata_schema.json5') as f:
    schema = yaml.load(f)

with open(metadata_path) as f:
    metadata = yaml.load(f)

try:
    jsonschema.Draft4Validator(schema)
    print('Schema validated')
except jsonschema.exceptions.ValidationError as err:
    print('Schema could not be validated:', err.message)

try:
    jsonschema.validate(metadata, schema)
    print('metadata validated')
except jsonschema.exceptions.ValidationError as err:
    print('ValidationError:', err.message)

