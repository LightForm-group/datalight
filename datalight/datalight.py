# -*- coding: utf-8 -*-
"""
Main module for datalight

:Authors: Nicolas Gruel <nicolas.gruel@manchester.ac.uk>

:Copyright: IT Services, The University of Mancheste
"""

import sys
import os
import configparser

# To get the home directory
from pathlib import Path
home = str(Path.home())

try:
    from docopt import docopt
except ImportError:
    print("Install docopt package: pip install docopt --user")
    sys.exit()

try:
    from .__init__ import __version__
    from .conf import logger
except ImportError:
    from __init__ import __version__
    from conf import logger


def main(args=None):
    """Run datalight scripts to upload file on data repository

    Command line::

        Usage:
            datalight <files> [--metadata=<metadata>] [--repository=<repository>] [--sandbox=<sandbox>]
            datalight -h | --help
            datalight --version

        Options:
            -h --help                   Show this screen.
            --version                   Show version.

        Examples:
            datalight file1 file2
            datalight directory --metadata=metadata.yml --repository=zenodo

    Raises
    ------
    SystemExit
        if the file or the folder to treat is not available.
    """

    arguments = docopt(main.__doc__, argv=args,
                       version=__version__)

    # Convert docopt results in the proper variable (change type when needed)

    fname = arguments['<files>']
    metadata = arguments['--metadata']
    repository = arguments['--repository']
    sandbox = arguments['--sandbox']

    if repository == 'zenodo':
        try:
            from .zenodo import Zenodo as DataRepo
            from .zenodo import ZenodoException as DataRepoException
        except ImportError:
            from zenodo import Zenodo as DataRepo
            from zenodo import ZenodoException as DataRepoException

        # Read zenodo token file from home repository
        tokenfile = os.path.join(home,'.zenodo')
        zenoconfig = configparser.ConfigParser()
        zenoconfig.read(tokenfile)

        try:
            if sandbox:
                token = zenoconfig['sandbox.zenodo.org']['lightForm']
            else:
                token = zenoconfig['zenodo.org']['lightForm']
        except KeyError:
            token = input('Provide Zenodo token: ')
            # todo implement save token

    try:
        if os.path.isdir(fname):
            directory = fname.strip(os.pathsep)
            files = os.listdir(directory)
        else:
            files, directory = [fname], ''
    except FileNotFoundError:
        error = 'Error: path {} for text files ' \
                'not found'.format(directory)
        logger.error(error)
        sys.exit()

    datarepo = DataRepo(token=token, sandbox=sandbox)
    datarepo.get_deposition_id()
    datarepo.upload_files(files, path=directory)
    #datarepo.upload_metadata(metadata=metadata)
    logger.info("Finished " + logger.name)


if __name__ == '__main__':
    main()
