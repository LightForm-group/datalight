"""This module is common core functions for datalight."""

import os
from zipfile import ZipFile
from conf import logger


class DatalightException(Exception):
    """Class for exception"""
    pass


def get_files_path(file_name):
    """Function to get the path(s) of the file(s) to upload to a data repository

    The function will return a list which contains the path of the files
    to upload.
    This function can be used to create an archive which contains all the files.

    Parameters
    ----------
    file_name: str
        Name of the file to get the path or the directory to list

    Return
    ------
    files_paths: list
        list of string which contains the path of the files to upload.

    Raise
    -----
    DatalightException: exception
        raise an exception if the return list is empty. It means that there
        are no file or directory with the name `file_name`.
    """

    # If file_name is a file return a list with file_name
    if os.path.isfile(file_name):
        files_paths = [file_name]
    else:
        # initializing empty file paths list
        files_paths = []

        # crawling through directory and subdirectories
        for root, directories, files in os.walk(file_name):
            for filename in files:
                # join the two strings in order to form the full filepath.
                filepath = os.path.join(root, filename)
                files_paths.append(filepath)

    if len(files_paths) == 0:
        message = 'File or directory: {} to upload does not exist.'.format(file_name)
        logger.error(message)
        raise DatalightException(message)

    # returning all file paths
    return sorted(files_paths)


def zip_data(files, zip_name='data.zip'):
    """Method to zip files which will be uploaded to the data repository.

    Parameters
    ----------
    files: list, str
        a list of string which contains the path of the files which will be
        part of the zip archive. Path will be conserved.
    zip_name: str, optional
        Name of the zip file to create. Default: data.zip
    """
    logger.info('Zip the files to create archive: {}'.format(zip_name))

    if type(files) is str:
        if os.path.isdir(files) or os.path.isfile(files):
            files = get_files_path(files)
        else:
            message = 'File/directory {} does not exist'.format(files)
            logger.error(message)
            raise DatalightException(message)

    # writing files to a zipfile
    with ZipFile(zip_name, 'w') as output_zip:
        # writing each file one by one
        try:
            for file in files:
                output_zip.write(file)
        except TypeError:
            message = 'Argument {} is not a file or a list.'.format(files)
            logger.error(message)
            raise DatalightException(message)
