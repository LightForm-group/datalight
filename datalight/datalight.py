"""Main module for datalight."""

import os
import sys
import configparser

from conf import logger
from common import DatalightException, zip_data, get_files_path
from zenodo import Zenodo as DataRepo


def main(directory_name, metadata, zip_name="data.zip", publish=False, sandbox=True):
    """Run datalight scripts to upload file to data repository"""

    try:
        files = get_files_path(directory_name)
    except DatalightException:
        logger.error('Problem with the files to upload.')
        sys.exit()

    if not os.path.exists(metadata):
        logger.error('Metadata file: {} does not exist.'.format(metadata))
        sys.exit(1)

    zip_data(files, zip_name)
    # Change the name of the files to upload for the zip file created
    files, directory = [zip_name], '.'

    token = get_authentication_token(sandbox)

    data_repo = DataRepo(token=token, sandbox=sandbox)
    data_repo.get_deposition_id()
    data_repo.upload_files(files, path=directory)
    data_repo.set_metadata(metadata)
    data_repo.upload_metadata()
    if publish:
        data_repo.publish()


def get_authentication_token(sandbox):
    current_directory = os.path.dirname(os.path.realpath(__file__))

    token_file = os.path.join(current_directory, "..", "datalight.config")
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


if __name__ == '__main__':
    main("C:/Users/Peter/Desktop/test/", "../tests/metadata/minimum_valid.yml")
