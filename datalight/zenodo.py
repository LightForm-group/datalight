"""This module is implements high level functions to upload and download data to Zenodo."""

import os
import requests
import json

from datalight.zenodo_metadata import ZenodoMetadata
from datalight.common import logger


class ZenodoException(Exception):
    """General exception raised when there is some failiure to interface with Zenodo."""


class Zenodo(object):
    """Class to upload and download files on Zenodo
    The deposit record method should be called and this does all of the steps required to uplad a file.

    :var token: (str) API token for connection to Zenodo.
    :var sandbox: (bool) If True, upload to the Zenodo sandbox. If false, upload to Zenodo.
    """

    def __init__(self, token, metadata=None, sandbox=False):

        if metadata is not None:
            self.metadata = metadata
        else:
            logger.warning('No metadata provided. Use the set_metadata method.')

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

    def deposit_record(self, files, directory, metadata, publish):
        """The main method which calls the many parts of the upload process."""

        self._get_deposition_id()
        self._upload_files(files, path=directory)
        self.set_metadata(metadata)
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
        if type(filenames) is str:
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
            request = requests.post(url, params={'access_token': self.token}, data=data, files=files)
            self._check_status_code(request.status_code)

    def set_metadata(self, metadata):
        """Method to validate metadata.

        :param metadata: (dict) The metadata input by the user.
        """
        self.metadata = metadata
        datalight_metadata = ZenodoMetadata(self.metadata)
        self.checked_metadata = {'metadata': datalight_metadata.get_metadata()}

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
            message = 'Request failed with error: {}. This is likely due to a malformed request.'.format(status_code)
            logger.error(message)
            raise ZenodoException(message)

        if status_code == 401:
            message = 'Request failed with error: {}. This is due to a bad access token.'.format(status_code)
            logger.error(message)
            raise ZenodoException(message)

        if status_code == 403:
            message = 'Request failed with error: {}. This is due to insufficent privilege.'.format(status_code)
            logger.error(message)
            raise ZenodoException(message)

        if status_code == 500:
            message = 'Zenodo server error {}. It is likely to be their problem not ours.'.format(status_code)
            logger.error(message)
            raise ZenodoException(message)

        else:
            message = 'Unclassified error: {}.'.format(status_code)
            logger.error(message)
            raise ZenodoException(message)
