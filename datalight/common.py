"""This module is common core functions for datalight."""

import sys
import zipfile
import pathlib
import configparser

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


def get_files_path(directory_name):
    """Recursively collect file paths within the given directory.

    The function will return a list of file paths relative to directory_name.
    :param directory_name: (str) The path to a directory
    :return files_paths: (list of string) Paths of files relative to directory_name.
    :raises FileNotFoundError: if the directory does not exist.
    """

    directory_name = pathlib.Path(directory_name)
    # If directory_name is a file, return a list with file_name
    if directory_name.is_file():
        file_paths = [directory_name]
    else:
        file_paths = directory_name.glob('**/*')

    absolute_paths = []

    for path in file_paths:
        # Glob finds directories as well as files so remove these.
        if not path.is_dir():
            absolute_paths.append(path.resolve())

    if len(absolute_paths) == 0:
        raise FileNotFoundError('Directory: {} does not exist.'.format(directory_name))

    return sorted(absolute_paths)


def zip_data(files, zip_name):
    """Method to zip files which will be uploaded to the data repository.

    :param files: (list of string) The paths of the files written to the zip archive.
    :param zip_name: (str) Name of the zip file to create.
    """

    zip_name = pathlib.Path(zip_name).resolve()

    try:
        with zipfile.ZipFile(zip_name, 'w') as output_zip:
            for file in files:
                output_zip.write(file)
    except FileExistsError:
        print("Error: Zip file \"{}\" already exists. Cannot overwrite.".format(zip_name))
        sys.exit()


def get_authentication_token(sandbox):
    """A method to read the Zenodo authentication token from a local file. This file is not
    committed to git and so will not appear online."""
    current_directory = pathlib.Path(__file__).parent

    token_file = current_directory.parent / pathlib.Path("datalight.config")
    zeno_config = configparser.ConfigParser()
    zeno_config.read(token_file)
    try:
        if sandbox:
            token = zeno_config['sandbox.zenodo.org']['token']
        else:
            token = zeno_config['zenodo.org']['token']
        return token
    except KeyError:
        return None
