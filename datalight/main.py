# -*- coding: utf-8 -*-
"""Main module to upload lightform data files to data repository.

:Authors: Nicolas Gruel <nicolas.gruel@manchester.ac.uk>

:Copyright: IT Services, The University of Manchester
"""
import sys
import os

try:
    from docopt import docopt
except ImportError:
    print("Install docopt package: pip install docopt --user")
    sys.exit()

try:
    from .__init__ import __version__
    from .datalight import logger, Process, DatalightException
except ImportError:
    from __init__ import __version__
    from datalight import logger, Process, DatalightException


