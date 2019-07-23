"""This module is common core functions for datalight."""

import pathlib
import configparser
from typing import Union

import logging.config


def set_up_logger():
    """ Dictionary with the configuration for the logging."""
    log_config = {
        'version': 1,
        'formatters': {
            'default': {
                'format': '%(levelname)s - %(asctime)s - %(name)s - %(funcName)s - %(message)s'
            },
        },
        # Handlers send log records to particular destinations.
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'default',
            }
        },
    }

    # Read logging configuration and create logger
    logging.config.dictConfig(log_config)


set_up_logger()
logger = logging.getLogger('datalight')


class DatalightException(Exception):
    """Class for exception"""


def get_authentication_token(credentials_location: pathlib.Path, sandbox: bool) -> Union[str, None]:
    """A method to read the Zenodo authentication token from a local file. This file is not
    committed to git and so will not appear online.
    :param credentials_location: The location of the credentials file.
    :param sandbox: Whether to get the Zenodo sandbox token or a real Zenodo token.
    """

    if not credentials_location.exists():
        raise FileNotFoundError(
            "Unable to load API token from datalight.config. {} was not found.".format(credentials_location))

    zeno_config = configparser.ConfigParser()
    zeno_config.read(credentials_location)
    try:
        if sandbox:
            token = zeno_config['sandbox.zenodo.org']['token']
        else:
            token = zeno_config['zenodo.org']['token']
        return token
    except KeyError:
        raise KeyError("Key not found in datalight.config.")

