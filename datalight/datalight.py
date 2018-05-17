# -*- coding: utf-8 -*-
"""
Main module for datalight

:Authors: Nicolas Gruel <nicolas.gruel@manchester.ac.uk>

:Copyright: IT Services, The University of Mancheste
"""

import os
import sys
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

        Usage: datalight [-h | --help] <files>... --metadata=<metadata> [options]

        Options:

        --metadata=<metadata>     File which contains the metadata information
        --repository=<repository> Name of a data repository [default: zenodo].
        --sandbox=<sandbox>]
        -h, --help                Print this help
        --version                 Print version of the software

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

    if repository is None:
        repository = 'zenodo'

    sandbox = arguments['--sandbox']

    # Read metadata from file
    if metadata is not None:
        with open(metadata, encoding="utf-8") as f:
            try:
                from ruamel.yaml import YAML
                metadata = {'metadata': YAML(typ="safe", pure=True).load(f)}
            except ImportError:
                import yaml
                metadata = {'metadata': yaml.load(f)}

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
                token = zenoconfig['sandbox.zenodo.org']['lightForm']
            else:
                token = zenoconfig['zenodo.org']['lightForm']
        except KeyError:
            token = input('Provide Zenodo token: ')

            # Save the token to the ~/.zenodo
            config = configparser.ConfigParser()
            if sandbox:
                config['sanbox.zenodo.org'] = {'lightForm': token}
            else:
                config['zenodo.org'] = {'lightForm': token}

            with open(tokenfile, 'a', encoding="utf-8") as configfile:
                config.write(configfile)

    try:
        if len(fname) == 1 and os.path.isdir(fname[0]):
            directory = fname[0].strip(os.pathsep)
            files = os.listdir(directory)
        else:
            files, directory = fname, ''
    except TypeError:
        files, directory = fname, ''
    except FileNotFoundError:
        error = 'Error: path {} for text files ' \
                'not found'.format(directory)
        logger.error(error)
        sys.exit()

    datarepo = DataRepo(token=token, sandbox=sandbox)
    datarepo.get_deposition_id()
    datarepo.upload_files(files, path=directory)
    if type(metadata) is dict:
        datarepo.upload_metadata(metadata=metadata)
    logger.info("Finished " + logger.name)


if __name__ == '__main__':
    main()
