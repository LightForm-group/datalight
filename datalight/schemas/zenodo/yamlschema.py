import sys
import yaml
import jsonschema

with open('record-1.0.0.yml') as f:
    schema = yaml.load(f)

#with open('lightform.yml') as f:
#with open('minimum.yaml') as f:
with open(sys.argv[1]) as f:
    test = yaml.load(f)

try:
    jsonschema.validate(test, schema)
    print('validated')
except jsonschema.exceptions.ValidationError as err:
    print('ValidationError:', err.message)

