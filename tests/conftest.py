"""
Module to
"""


import os
import sys

# sys.path.insert(0, os.path.abspath('..'))
file_path = os.path.realpath(__file__)

# go up one level to access the schema definition
path = os.path.dirname(file_path) + os.sep + '..'
sys.path.append(path)

schemafile = os.path.join(path, 'datalight',
                          'schemas', 'zenodo', 'record-1.0.0.yml')

import datalight

# Module
from datalight.zenodo import Zenodo, ZenodoException

from datalight.zenodo_metadata import ZenodoMetadata, ZenodoMetadataException

from datalight.common import DatalightException, get_files_path, zipdata
