"""This module is implements high level functions to upload and download data to Zenodo."""

import json
import pathlib
from typing import List, Union

import requests

import datalight.zenodo_metadata as zenodo_metadata
from datalight import common
from datalight.common import logger


class ZenodoException(Exception):
    """General exception raised when there is some failure to interface with Zenodo."""


def upload_record(file_paths: List[pathlib.Path], metadata: dict, publish=False,
                  sandbox=True, credentials_location="../datalight.config"):
    """Run datalight scripts to upload file to data repository
    :param file_paths: One or more paths of files to upload.
    :param metadata: A dictionary of metadata describing the record.
    :param publish: Whether to publish this record on Zenodo after uploading.
    :param sandbox: Whether to put the record on Zenodo sandbox or the real Zenodo.
    :param credentials_location: Location of the file containing zenodo API tokens.
    """

    credentials_location = pathlib.Path(credentials_location).resolve()
    token = common.get_authentication_token(credentials_location, sandbox)

    data_repo = Zenodo(token, metadata, sandbox)
    data_repo.deposit_record(file_paths, publish)


class Zenodo:
    """Class to upload files to Zenodo
    The :func:`~datalight.Zenodo.deposit_record` method handles all of the steps required to upload a file.
    """

    def __init__(self, token: str, metadata: Union[str, dict], sandbox: bool = False):
        """
        :param token: API token for connection to Zenodo.
        :param metadata: Either a path to a metadata file or a dictionary of metadata.
        :param sandbox: If True, upload to the Zenodo sandbox. If false, upload to Zenodo."""
        self.raw_metadata = None
        self.metadata_path = None

        if isinstance(metadata, dict):
            self.raw_metadata = metadata
        else:
            self.metadata_path = metadata

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

    def deposit_record(self, files: List[pathlib.Path], publish: bool):
        """Method which calls the parts of the upload process."""

        self.checked_metadata = self._get_metadata()
        self._get_deposition_id()
        self._upload_files(files)
        self._upload_metadata()
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

    def _upload_files(self, filenames: List[pathlib.Path]):
        """Method to upload a file to Zenodo
        :param filenames: Paths of one or more files to upload.
        """

        # Create the url to upload with the deposition_id
        url = self.depositions_url + '/{}/files'.format(self.deposition_id)
        logger.info('url: {}'.format(url))

        for filename in filenames:
            # Create the zenodo data dictionary which contains the name of the file
            data = {'filename': filename}
            logger.info('filename: {}'.format(filename))

            # Open the file to upload in binary mode.
            files = {'file': open(filename, 'rb')}

            # upload the file
            request = requests.post(url, params={'access_token': self.token}, data=data, files=files)
            self._check_status_code(request.status_code)

    def _get_metadata(self):
        """Method to get and validate metadata."""
        schema = zenodo_metadata.read_schema_from_file()
        if self.raw_metadata is None:
            # If metadata was provided as a path then read it from a file.
            self.raw_metadata = zenodo_metadata.read_metadata_from_file(self.metadata_path)
        else:
            # If metadata comes from the UI, need to parcel the creator data up.
            creators = {}
            if "name" in self.raw_metadata:
                creators["name"] = self.raw_metadata.pop("name")
            if "affiliation" in self.raw_metadata:
                creators["affiliation"] = self.raw_metadata.pop("affiliation")
            if "orcid" in self.raw_metadata:
                creators["orcid"] = self.raw_metadata.pop("orcid")
            # A list of a dictionary makes a JSON array type.
            self.raw_metadata["creators"] = [creators]
        validated_metadata = zenodo_metadata.validate_metadata(self.raw_metadata, schema)
        return {'metadata': validated_metadata}

    def _upload_metadata(self):
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
                      ' due to insufficient privileges.'.format(status_code)
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
