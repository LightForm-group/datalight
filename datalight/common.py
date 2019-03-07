"""This module is common core functions for datalight."""

import sys
import zipfile
import pathlib
import configparser


class DatalightException(Exception):
    """Class for exception"""
    pass


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
    current_directory = pathlib.Path(__file__).parent

    token_file = current_directory.parent / pathlib.Path("datalight.config")
    zeno_config = configparser.ConfigParser()
    zeno_config.read(token_file)
    try:
        if sandbox:
            token = zeno_config['sandbox.zenodo.org']['token']
        else:
            token = zeno_config['zenodo.org']['token']
    except KeyError:
        token = input('Provide Zenodo token: ')

        # Save the token to the ~/.zenodo
        config = configparser.ConfigParser()
        if sandbox:
            config['sandbox.zenodo.org'] = {'lightform': token}
        else:
            config['zenodo.org'] = {'lightform': token}

        with open(token_file, 'a', encoding="utf-8") as configfile:
            config.write(configfile)
    return token
