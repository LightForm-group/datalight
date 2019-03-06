"""This module is common core functions for datalight."""

import os
import sys
import zipfile
import pathlib


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

    # If directory_name is a file, return a list with file_name
    if os.path.isfile(directory_name):
        file_paths = [pathlib.Path(directory_name)]
    else:
        file_paths = pathlib.Path(directory_name).glob('**/*')

    absolute_paths = []

    for path in file_paths:
        absolute_paths.append(path.resolve())

    if len(absolute_paths) == 0:
        raise FileNotFoundError('Directory: {} does not exist.'.format(directory_name))

    return sorted(absolute_paths)


def zip_data(files, zip_name):
    """Method to zip files which will be uploaded to the data repository.

    :param files: (list of string) The paths of the files written to the zip archive.
    :param zip_name: (str) Name of the zip file to create.
    """

    zip_name = os.path.abspath(zip_name)

    try:
        with zipfile.ZipFile(zip_name, 'x') as output_zip:
            for file in files:
                output_zip.write(file)
    except FileExistsError:
        print("Error: Zip file \"{}\" already exists. Cannot overwrite.".format(zip_name))
        sys.exit()
