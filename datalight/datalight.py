# -*- coding: utf-8 -*-
"""
Main module for datalight

:Authors: Nicolas Gruel <nicolas.gruel@manchester.ac.uk>

:Copyright: IT Services, The University of Mancheste
"""

# pylint: disable=locally-disabled, invalid-name

try:
    from .__init__ import __version__
    from .conf import logger
except ImportError:
    from __init__ import __version__
    from conf import logger

import os
import sys
from zipfile import ZipFile
import configparser  # read the ini file containing zenodo information (token)

# To get the home directory
from pathlib import Path
home = str(Path.home())

try:
    from docopt import docopt
except ImportError:
    print("Install docopt package: pip install docopt --user")
    sys.exit()


class DatalightException(Exception):
    """Class for exception
        """
    pass


def get_files_path(fname):
    """Function to get the path(s) of the file(s)

    Parameters
    ----------
    fname: str
        Name of the file to get the path or the directory to list
    """

    # If fname is a file return a list with fname
    if os.path.isfile(fname):
        files_paths = [fname]
    else:
         # initializing empty file paths list
        file_paths = []

        # crawling through directory and subdirectories
        for root, directories, files in os.walk(fname):
            for filename in files:
                # join the two strings in order to form the full filepath.
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)

    if not len(file_paths):
        message = 'File or directory: {} to upload does not exist.'.format(fname)
        logger.error(message)
        raise DatalightException(message)

    # returning all file paths
    return file_paths


def zipdata(files, zipname='data.zip'):
    """Method to zip files which will be uploaded to the data repository.

    Parameters
    ----------
    files: list
        a list of string which contains the path of the files which will be
        part of the zip archive. Path will be conserved.
    zipname: str, optional
        Name of the zip file to create. Default: data.zip
    """
    logger.info('Zip the files to create archive: {}'.format(zipname))

    # writing files to a zipfile
    with ZipFile(zipname, 'w') as zip:
        # writing each file one by one
        for file in files:
            zip.write(file)


def unzip(self):
    pass


def main(args=None):
    """Run datalight scripts to upload file on data repository

    Command line::

        Usage: datalight [-h | --help] <files>... (-m <metadata> | --metadata=<metadata>) [options]

        Options:

        -m FILE --metadata=FILE        File which contains the metadata information
        -z zipname --zipname=FILE      Name of the zip file which will be uploaded [default: data.zip]
        --nozip                        Do not create zip file containing the data to upload
        -r NAME --repository=NAME      Name of a data repository [default: zenodo]
        -p --publish                    If present publish the data
        -s --sandbox                   If present, datalight will use the sandbox data repository
        -k --keep                      Keep zip file created
        -h --help                      Print this help
        -v --version                   Print version of the software

        Examples:
            datalight file1 file2
            datalight directory --metadata=metadata.yml --repository=zenodo
            datalight file -m metadata.yml

    Raises
    ------
    SystemExit
        if the file or the folder to treat is not available.
    KeyError
        if no key found for the data repository wanted
    ImportError
        if the not possible to import the data repository wanted
    """

    # Read the arguments and option with docopt
    arguments = docopt(main.__doc__, argv=args,
                       version=__version__)

    # Convert docopt results in the proper variable (change type when needed)

    # Lists all the files and/or directories to upload
    fnames = arguments['<files>']

    # Get list of the files path to upload
    files = []
    try:
        for fname in fnames:
            files += get_files_path(fname)
    except DatalightException:
        logger.error('Problem with the files to upload.')
        sys.exit()

    # option which will give the name of the metadata file
    metadata = arguments['--metadata']

    if not os.path.exists(metadata):
        logger.error('Metadata file: {} does not exist.'.format(metadata))
        sys.exit(1)

    # Choice of repository default Zenodo
    repository = arguments['--repository']

    if repository is None:
        repository = 'zenodo'

    # If sandbox is present the version of the repository
    # used will be the sandbox one
    sandbox = arguments['--sandbox']

    # Zip data in an archive (to keep paths)
    if not arguments['--nozip']:
        zipname = arguments['--zipname']
        zipdata(files, zipname)

        # Change the name of the files to upload for the zip file created
        files, directory = [zipname], '.'

    if repository == 'zenodo':
        try:
            from .zenodo import Zenodo as DataRepo
            from .zenodo import ZenodoException as DataRepoException
        except ImportError:
            from zenodo import Zenodo as DataRepo
            from zenodo import ZenodoException as DataRepoException

        # Read zenodo token file from home repository
        tokenfile = os.path.join(home, '.zenodo')
        zenoconfig = configparser.ConfigParser()
        zenoconfig.read(tokenfile)

        try:
            if sandbox:
                token = zenoconfig['sandbox.zenodo.org']['lightform']
            else:
                token = zenoconfig['zenodo.org']['lightform']
        except KeyError:
            token = input('Provide Zenodo token: ')

            # Save the token to the ~/.zenodo
            config = configparser.ConfigParser()
            if sandbox:
                config['sandbox.zenodo.org'] = {'lightform': token}
            else:
                config['zenodo.org'] = {'lightform': token}

            with open(tokenfile, 'a', encoding="utf-8") as configfile:
                config.write(configfile)

    datarepo = DataRepo(token=token, sandbox=sandbox)
    datarepo.get_deposition_id()
    datarepo.upload_files(files, path=directory)
    datarepo.set_metadata(metadata)
    datarepo.upload_metadata()
    if arguments['--publish']:
        datarepo.publish()

    # Remove zip file create but if asked to keep it
    if not arguments['--nozip'] \
            and not arguments['--keep'] \
            and len(files) == 1:
        logger.info('Remove created zip file: {}'.format(files[0]))
        os.remove(files[0])
    logger.info("Finished " + logger.name)


if __name__ == '__main__':
    main()
