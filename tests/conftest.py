"""
Module to
"""


import os
import sys
import pytest

# sys.path.insert(0, os.path.abspath('..'))
file_path = os.path.realpath(__file__)
path = os.path.dirname(file_path) + os.sep + '..'
sys.path.append(path)

import datalight

# Module
from datalight.zenodo import Zenodo, ZenodoException

