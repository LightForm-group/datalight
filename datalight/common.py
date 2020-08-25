"""This module is common core functions for datalight."""

import sys
import logging
import pathlib
import configparser
from typing import Union

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
                                f"{credentials_location} was not found.")

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


def read_yaml(folder_path: str, file_name: str) -> dict:
    """Read the UI specification from a YAML file."""
    file_path = pathlib.Path(folder_path).joinpath(file_name)

    with open(file_path, encoding='utf8') as input_file:
        ui_specification = yaml.load(input_file, Loader=yaml.FullLoader)

    return ui_specification