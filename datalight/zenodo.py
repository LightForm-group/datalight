"""This module is implements high level functions to upload and download data to Zenodo."""

import json
import pathlib
from typing import List, Union
from os import PathLike
import tempfile

import requests

import datalight.zenodo_metadata as zenodo_metadata
from datalight import common
from datalight.common import logger


class ZenodoException(Exception):
    """General exception raised when there is some failure to interface with Zenodo."""


def upload_record(file_paths: List[pathlib.Path], repository_metadata: dict,
                  experimental_metadata: dict, config_path: Union[pathlib.Path, str],
                  publish: bool = False, sandbox: bool = True):
    """Run datalight scripts to upload file to data repository
    :param experimental_metadata: The experimental metadata.
    :param file_paths: One or more paths of files to upload.
    :param repository_metadata: A dictionary of metadata describing the record.
    :param publish: Whether to publish this record on Zenodo after uploading.
    :param sandbox: Whether to put the record on Zenodo sandbox or the real Zenodo.
    :param config_path: Path to the file containing zenodo API tokens.
    """

    experimental_metadata = ExperimentalMetadata(experimental_metadata)
    file_paths.append(experimental_metadata.metadata_path)

    credentials_location = pathlib.Path(config_path).resolve()
    token = common.get_authentication_token(credentials_location, sandbox)

    data_repo = Zenodo(token, repository_metadata, sandbox)
    data_repo.deposit_record(file_paths, publish)


class ExperimentalMetadata:
    def __init__(self, metadata: dict):
        self.metadata = metadata
        self.temp_directory = tempfile.TemporaryDirectory()
        self.metadata_path = pathlib.Path(self.temp_directory.name) / pathlib.Path("metadata.txt")
        self.generate_metadata_summary()

    def generate_metadata_summary(self):
        """
        A method to take all of the metadata and write it to a text file which will be uploaded
        along with the data.
        """
        with open(self.metadata_path, 'w') as metadata_file:
            for value in self.metadata.values():
                metadata_file.write(f"{value}\n")
                metadata_file.write("\n\nMetadata auto recorded by Datalight "
                                    "(https://github.com/LightForm-group/datalight)")

    def remove_temp_folder(self):
        del self.temp_directory


class Zenodo:
    """Class to upload files to Zenodo
    The :func:`~datalight.Zenodo.deposit_record` method handles all of the steps required to upload
     a file.
    """

    def __init__(self, token: str, metadata: Union[PathLike, dict], sandbox: bool = False):
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

        self.depositions_url = f'{self.api_base_url}deposit/depositions'
        self.deposition_id = None
        self.checked_metadata = None
        self.status_code = None

        self.token = token
        self._try_connection()

    def deposit_record(self, files: List[pathlib.Path], publish: bool):
        """Method which calls the parts of the upload process."""
        self._get_metadata()
        self.checked_metadata = self.validate_metadata()
        self._get_deposition_id()
        self._upload_files(files)
        self._upload_metadata()
        if publish:
            self.publish()

    def _try_connection(self):
        """Method to test that the API token and connection with Zenodo website is working."""
        request = requests.get(self.depositions_url, params={'access_token': self.token})
        self._check_request_response(request)

    def _get_deposition_id(self):
        """Get the deposition id needed to upload a new record to Zenodo"""
        headers = {'Content-Type': 'application/json'}

        logger.debug(f'deposition url: {self.depositions_url}')
        request = requests.post(self.depositions_url, params={'access_token': self.token},
                                json={}, headers=headers)

        self._check_request_response(request)

        self.deposition_id = request.json()['id']
        logger.info(f'Deposition id: {self.deposition_id}')

    def _upload_files(self, filenames: List[pathlib.Path]):
        """Method to upload a file to Zenodo
        :param filenames: Paths of one or more files to upload.
        """
        # Create the url to upload with the deposition_id
        url = f'{self.depositions_url}/{self.deposition_id}/files'
        logger.info(f'url: {url}')

        for filename in filenames:
            # Create the zenodo data dictionary which contains the name of the file
            data = {'filename': filename}
            logger.info(f'filename: {filename}')

            # Open the file to upload in binary mode.
            files = {'file': open(filename, 'rb')}

            # upload the file
            request = requests.post(url, params={'access_token': self.token}, data=data,
                                    files=files)
            self._check_request_response(request)

    def _get_metadata(self):
        """Method to get and validate metadata."""
        if self.raw_metadata is None:
            # If metadata was provided as a path then read it from a file.
            self.raw_metadata = zenodo_metadata.read_metadata_from_file(self.metadata_path)
        else:
            # If metadata comes from the UI, need to get some data into the right format.
            # A list of dictionaries makes a JSON array type.
            creators = []
            if "author_details" in self.raw_metadata:
                creator = {}
                for author in self.raw_metadata["author_details"]:
                    creator["name"] = author[0]
                    creator["affiliation"] = author[1]
                    creator["orcid"] = author[2]
                creators.append(creator)
            self.raw_metadata["creators"] = creators

            # Communities must also be a JSON array
            if "communities" in self.raw_metadata:
                communities = [{"identifier": (self.raw_metadata["communities"]).lower()}]
                self.raw_metadata["communities"] = communities

    def _upload_metadata(self):
        """Upload metadata to Zenodo repository.

        After creating the request and uploading the file(s) we need to update
        the metadata needed by Zenodo related to the record.
        """

        # Create the url to upload with the deposition_id
        url = f'{self.depositions_url}/{self.deposition_id}'
        logger.info(f'url: {url}')

        headers = {"Content-Type": "application/json"}
        request = requests.put(url, params={'access_token': self.token},
                               data=json.dumps(self.checked_metadata), headers=headers)

        self._check_request_response(request)

    def publish(self):
        """Method which will publish the deposition linked with the id.

        .. warning: After publishing a record it is not possible to delete it.

        :exception ZenodoException: Raise if connection return status >= 400
        """

        publish_url = f'{self.depositions_url}/{self.deposition_id}/actions/publish'
        request = requests.post(publish_url, params={'access_token': self.token})

        self._check_request_response(request)

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
        request_url = f'{self.depositions_url}/{self.deposition_id}'

        logger.info('Delete url: {}'.format(request_url))
        request = requests.delete(request_url, params={'access_token': self.token})
        self._check_request_response(request)

    def _check_request_response(self, response: requests.models.Response) -> int:
        """Check the status code returned from an interaction with the Zenodo API.

        :param response: A response to an HTTP request.
        :return status_code: If status code represents success.
        :raises ZenodoException: If status code represents a failure.
        """
        self.status_code = response.status_code

        if response.status_code in [200, 201, 202, 204]:
            logger.debug(f'Request succeed with status code: {response.status_code}')
            return response.status_code

        if response.status_code == 400:
            message = f'Request failed with error: {response.status_code}. ' \
                      f'The details are: {response.content}.'
            logger.error(message)
            raise ZenodoException(message)

        if response.status_code == 401:
            message = f'Request failed with error: {response.status_code}. This is ' \
                      'due to a bad access token.'
            logger.error(message)
            raise ZenodoException(message)

        if response.status_code == 403:
            message = f'Request failed with error: {response.status_code}. This is' \
                      ' due to insufficient privileges.'
            logger.error(message)
            raise ZenodoException(message)

        if response.status_code == 500:
            message = f'Zenodo server error {response.status_code}. It is likely to be their ' \
                      f'problem not ours. Details: {response.content}'
            logger.error(message)
            raise ZenodoException(message)

        else:
            message = 'Unclassified error: {response.status_code}. Details: {response.content}'
            logger.error(message)
            raise ZenodoException(message)

    def validate_metadata(self):
        """Compare the metadata to the schema and remove anything not allowed by Zenodo."""
        schema = zenodo_metadata.read_schema_from_file()
        validated_metadata = zenodo_metadata.validate_metadata(self.raw_metadata, schema)
        return {'metadata': validated_metadata}
