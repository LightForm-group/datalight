"""This module is common core functions for datalight."""

import sys
import logging
import pathlib
import configparser
from typing import Union
from os import getcwd

import yaml

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
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
        raise FileNotFoundError(f"Unable to load API token from datalight.config. "
                                f"{credentials_location} was not found.\n\n"
                                f"Current working directory is {getcwd()}.")

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


def read_yaml(file_path: Union[pathlib.Path, str]) -> dict:
    """Read a YAML file and return its contents."""
    with open(file_path, encoding='utf8') as input_file:
        return yaml.load(input_file, Loader=yaml.FullLoader)


class UploadStatus:
    """The status of the upload as it goes through the upload process."""
    def __init__(self, code: int, message: str, error_field: str = None, error_message: str = None):
        self.code = code
        self.message = message
        self.error_field = error_field
        self.error_message = error_message