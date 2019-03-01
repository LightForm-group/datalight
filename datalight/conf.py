"""Module to contains the configuration of the zenoligth software

:Authors: Nicolas Gruel <nicolas.gruel@manchester.ac.uk>

:Copyright: IT Services, The University of Manchester
"""

import logging.config

# Pure python dictionary with the configuration for the logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(levelname)s - %(asctime)s - %(name)s - %(funcName)s - %(message)s'
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'filename': 'datalight.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'ERROR',
            'formatter': 'default',
        }
    },
    'root': {
        'handlers': ['file', 'console'],
        #'level': 'DEBUG',
    },
}


# Read logging configuration and create logger
logging.config.dictConfig(LOGGING)
logger = logging.getLogger('datalight')
