"""This module is implements high level functions to upload and download data to Zenodo."""

import os
import json
import requests

import datalight.zenodo_metadata as zenodo_metadata
from datalight import common
from datalight.common import logger


class ZenodoException(Exception):
    """General exception raised when there is some failure to interface with Zenodo."""


def upload_record(directory_name, metadata, zip_name="data.zip", publish=False, sandbox=True):
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

    #if not os.path.exists(metadata_path):
    #    common.logger.error('Metadata file: {} does not exist.'.format(metadata_path))
    #    raise FileNotFoundError

    common.zip_data(files, zip_name)
    # Change the name of the files to upload for the zip file created
    files, directory = [zip_name], '.'

    data_repo = Zenodo(token=token, metadata_path=metadata, sandbox=sandbox)
    data_repo.deposit_record(files, directory, publish)


class Zenodo:
    """Class to upload and download files on Zenodo
    The deposit record method should be called and this does all
    of the steps required to uplad a file.

    :var token: (str) API token for connection to Zenodo.
    :var sandbox: (bool) If True, upload to the Zenodo sandbox. If false, upload to Zenodo.
    """

    def __init__(self, token, metadata_path, sandbox=False):

        self.metadata_path = metadata_path

        if sandbox:
            self.api_base_url = 'https://sandbox.zenodo.org/api/'
        else:
            self.api_base_url = 'https://zenodo.org/api/'

        self.depositions_url = self.api_base_url + 'deposit/depositions'
        self.deposition_id = None
        self.checked_metadata = None
        self.status_code = None

        self.token = token
        self._try_connection()

    def deposit_record(self, files, directory, publish):
        """The main method which calls the many parts of the upload process."""

        self.checked_metadata = self.get_metadata()
        self._get_deposition_id()
        self._upload_files(files, path=directory)
        self.upload_metadata()
        if publish:
            self.publish()

    def _try_connection(self):
        """Method to test that the API token and connection with Zenodo website is working."""
        request = requests.get(self.depositions_url, params={'access_token': self.token})
        self._check_status_code(request.status_code)

    def _get_deposition_id(self):
        """Get the deposition id needed to upload a new record to Zenodo"""
        headers = {'Content-Type': 'application/json'}

        logger.debug('deposition url: {}'.format(self.depositions_url))
        request = requests.post(self.depositions_url, params={'access_token': self.token},
                                json={}, headers=headers)

        self._check_status_code(request.status_code)

        self.deposition_id = request.json()['id']
        logger.info('Deposition id: {}'.format(self.deposition_id))

    def _upload_files(self, filenames, path):
        """Method to upload a file to Zenodo

        :param filenames: (str or list) Name of the file(s) to upload
        :param path: (str) Path of where the file(s) is.
        """

        # Create the url to upload with the deposition_id
        url = self.depositions_url + '/{}/files'.format(self.deposition_id)
        logger.info('url: {}'.format(url))

        # if filenames is only a file convert it to list
        if isinstance(filenames, str):
            filenames = [filenames]

        for filename in filenames:
            if path is not None:
                filename = os.path.join(path, filename)

            # Create the zenodo data dictionary which contains the name of the file
            data = {'filename': filename}
            logger.info('filename: {}'.format(filename))

            # Open the file to upload in binary mode.
            files = {'file': open(filename, 'rb')}

            # upload the file
            request = requests.post(url, params={'access_token': self.token}, data=data,
                                    files=files)
            self._check_status_code(request.status_code)

    def get_metadata(self):
        """Method to get and validate metadata."""
        schema = zenodo_metadata.read_schema_from_file()
        metadata = zenodo_metadata.read_metadata_from_file(self.metadata_path)
        validated_metadata = zenodo_metadata.validate_metadata(metadata, schema)
        return {'metadata': validated_metadata}

    def upload_metadata(self):
        """Upload metadata to Zenodo repository.

        After creating the request and uploading the file(s) we need to update
        the metadata needed by Zenodo related to the record.
        """

        # Create the url to upload with the deposition_id
        url = self.depositions_url + '/{}'.format(self.deposition_id)
        logger.info('url: {}'.format(url))

        headers = {"Content-Type": "application/json"}
        request = requests.put(url, params={'access_token': self.token},
                               data=json.dumps(self.checked_metadata), headers=headers)

        self._check_status_code(request.status_code)

    def publish(self):
        """Method which will publish the deposition linked with the id.

        .. warning: After publishing a record it is not possible to delete it.

        :exception ZenodoException: Raise if connection return status >= 400
        """

        publish_url = (self.depositions_url + '/{}/actions/publish'.format(self.deposition_id))
        request = requests.post(publish_url, params={'access_token': self.token})

        self._check_status_code(request.status_code)

    def delete(self, _id=None):
        """Method to delete an unpublished deposition.
        If id not provided, use self.deposition_id, else use provided id

        :param _id: (int) Deposition id of the record to delete.
        Can be done only if the record was not published.

        :exception ZenodoException: If connection return status >= 400
        """

        if _id is not None:
            self.deposition_id = _id

        # Create the request url
        request_url = (self.depositions_url + '/{}'.format(self.deposition_id))

        logger.info('Delete url: {}'.format(request_url))
        request = requests.delete(request_url, params={'access_token': self.token})
        self._check_status_code(request.status_code)

    def _check_status_code(self, status_code):
        """Check the status code returned from an interaction with the Zenodo API.

        :param status_code: Status code to check.
        :return status_code: If status code represents success.
        :raises ZenodoException: If status code represents a failure.
        """
        self.status_code = status_code

        if status_code in [200, 201, 202, 204]:
            logger.debug('Request succeed with status code: {}'.format(status_code))
            return status_code

        if status_code == 400:
            message = 'Request failed with error: {}. This is ' \
                      'likely due to a malformed request.'.format(status_code)
            logger.error(message)
            raise ZenodoException(message)

        if status_code == 401:
            message = 'Request failed with error: {}. This is ' \
                      'due to a bad access token.'.format(status_code)
            logger.error(message)
            raise ZenodoException(message)

        if status_code == 403:
            message = 'Request failed with error: {}. This is' \
                      ' due to insufficent privilege.'.format(status_code)
            logger.error(message)
            raise ZenodoException(message)

        if status_code == 500:
            message = 'Zenodo server error {}. It is likely to be ' \
                      'their problem not ours.'.format(status_code)
            logger.error(message)
            raise ZenodoException(message)

        else:
            message = 'Unclassified error: {}.'.format(status_code)
            logger.error(message)
            raise ZenodoException(message)
