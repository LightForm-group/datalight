"""Main module for datalight."""

import os

import datalight.common as common
from datalight.zenodo import Zenodo as DataRepo


def main(directory_name, metadata_path, zip_name="data.zip", publish=False, sandbox=True):
    """Run datalight scripts to upload file to data repository"""

    token = common.get_authentication_token(sandbox)
    if token is None:
        common.logger.error("Unable to load API token from datalight.config.")
        raise FileNotFoundError("Unable to load API token from datalight.config.")

    try:
        files = common.get_files_path(directory_name)
    except common.DatalightException:
        common.logger.error('Problem with the files to upload.')
        raise common.DatalightException

    if not os.path.exists(metadata_path):
        common.logger.error('Metadata file: {} does not exist.'.format(metadata_path))
        raise FileNotFoundError

    common.zip_data(files, zip_name)
    # Change the name of the files to upload for the zip file created
    files, directory = [zip_name], '.'

    data_repo = DataRepo(token=token, metadata_path=metadata_path, sandbox=sandbox)
    data_repo.deposit_record(files, directory, publish)


if __name__ == '__main__':
    main("C:/Users/Peter/Desktop/test/", "../tests/metadata/minimum_valid.yml")
