"""This module is implements high level functions to upload and download data to Zenodo."""

import json
import pathlib
from typing import List, Union, Tuple
import tempfile

import requests
import yaml

import datalight.zenodo_metadata as zenodo_metadata
from datalight import common
from datalight.common import logger, UploadStatus

STATUS_SUCCESS = [200, 201, 202, 204]


class ZenodoException(Exception):
    """General exception raised when there is some failure to interface with Zenodo."""


def load_yaml(metadata_path: str) -> dict:
    """Method to read metadata from a file.
    :param metadata_path: A path to a file which contains zenodo metadata (yaml format).
    """
    logger.info(f'Metadata read from file: {metadata_path}')
    try:
        with open(metadata_path) as input_file:
            return yaml.load(input_file, Loader=yaml.FullLoader)
    except FileNotFoundError:
        raise FileNotFoundError(f'Metadata file {metadata_path} not found.')


def upload_record(file_paths: List[str], repository_metadata: Union[dict, str],
                  config_path: Union[pathlib.Path, str], experimental_metadata: dict,
                  publish: bool, sandbox: bool) -> UploadStatus:
    """Run datalight scripts to upload file to data repository
    :param file_paths: One or more paths of files to upload.
    :param repository_metadata: Either a path to load metadata from or a dictionary of metadata
      describing the record.
    :param config_path: Path to the file containing zenodo API tokens.
    :param experimental_metadata: A dictionary of experimental metadata - if not None, this will
      be written to a text file and added to the upload.
    :param publish: Whether to publish this record on Zenodo after uploading.
    :param sandbox: Whether to put the record on Zenodo sandbox or the real Zenodo.
    :returns: None if upload successful else returns a string describing the error.
    """
    if isinstance(repository_metadata, str):
        repository_metadata = load_yaml(repository_metadata)

    if experimental_metadata:
        experimental_metadata = ExperimentalMetadata(experimental_metadata)
        file_paths.append(experimental_metadata.metadata_path)

    credentials_location = pathlib.Path(config_path).resolve()
    token = common.get_authentication_token(credentials_location, sandbox)

    depositions_url = get_deposition_url(sandbox)

    upload_status = deposit_record(file_paths, repository_metadata, depositions_url,
                                   token, publish)

    return upload_status


def get_deposition_url(sandbox: bool):
    """Get the Zenodo API URL for requesting an upload. The URL depends on whether the sandbox
    or live version of Zenodo is being used."""
    if sandbox:
        api_base_url = 'https://sandbox.zenodo.org/api/'
    else:
        api_base_url = 'https://zenodo.org/api/'
    depositions_url = f'{api_base_url}deposit/depositions'
    return depositions_url


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


def deposit_record(files: List[str], raw_metadata: dict, deposition_url: str, token: str,
                   publish: bool) -> UploadStatus:
    """Method which calls the parts of the upload process.
    :returns: An UploadStatus object indicating whether there was an error or if the upload
        was successful."""
    status, checked_metadata = validate_metadata(raw_metadata)
    if status.code not in STATUS_SUCCESS:
        return status

    status = try_connection(deposition_url, token)
    if status.code not in STATUS_SUCCESS:
        return status

    status, deposition_id = _get_deposition_id(deposition_url, token)
    if status.code not in STATUS_SUCCESS:
        return status

    status = _upload_files(deposition_url, deposition_id, token, files)
    if status.code not in STATUS_SUCCESS:
        delete_record(deposition_url, deposition_id, token)
        return status

    status = _upload_metadata(deposition_url, deposition_id, token, checked_metadata)
    if status.code not in STATUS_SUCCESS:
        delete_record(deposition_url, deposition_id, token)
        return status

    if publish:
        status = publish_record(deposition_url, deposition_id, token)
    if status.code not in STATUS_SUCCESS:
        delete_record(deposition_url, deposition_id, token)
        return status
    else:
        return UploadStatus(200, "Upload Completed successfully")


def try_connection(deposition_url: str, token: str) -> UploadStatus:
    """Method to test that the API token and connection with Zenodo website is working."""
    request = requests.get(deposition_url, params={'access_token': token})
    return _check_request_response(request)


def _get_deposition_id(deposition_url: str, token: str) -> Tuple[UploadStatus, int]:
    """Get the deposition id needed to upload a new record to Zenodo"""
    deposition_id = ""
    headers = {'Content-Type': 'application/json'}

    logger.debug(f'deposition url: {deposition_url}')
    request = requests.post(deposition_url, params={'access_token': token},
                            json={}, headers=headers)

    upload_status = _check_request_response(request)
    if upload_status.code in STATUS_SUCCESS:
        deposition_id = request.json()['id']
        logger.info(f'Deposition id: {deposition_id}')
    return upload_status, deposition_id


def _upload_files(deposition_url: str, deposition_id: int, token: str,
                  filenames: List[str]) -> UploadStatus:
    """Method to upload a file to Zenodo
    :param filenames: Paths of one or more files to upload.
    """
    # Create the url to upload with the deposition_id
    url = f'{deposition_url}/{deposition_id}/files'
    logger.info(f'url: {url}')

    for filename in filenames:
        # Create the zenodo data dictionary which contains the name of the file
        data = {'filename': filename}
        logger.info(f'filename: {filename}')

        # Open the file to upload in binary mode.
        files = {'file': open(filename, 'rb')}

        # upload the file
        request = requests.post(url, params={'access_token': token}, data=data,
                                files=files)
        status = _check_request_response(request)
        if status.code not in STATUS_SUCCESS:
            return status
    return UploadStatus(200, "All files uploaded successfully.")


def _upload_metadata(deposition_url: str, deposition_id: int, token: str,
                     metadata: dict) -> UploadStatus:
    """Upload metadata to Zenodo repository.

    After creating the request and uploading the file(s) we need to update
    the metadata needed by Zenodo related to the record.
    """

    # Create the url to upload with the deposition_id
    url = f'{deposition_url}/{deposition_id}'
    logger.info(f'url: {url}')

    headers = {"Content-Type": "application/json"}
    request = requests.put(url, params={'access_token': token},
                           data=json.dumps(metadata), headers=headers)

    return _check_request_response(request)


def publish_record(deposition_url: str, deposition_id: int, token: str) -> UploadStatus:
    """Method which will publish the deposition linked with the id.

    .. warning: After publishing a record it is not possible to delete it.

    :exception ZenodoException: Raise if connection return status >= 400
    """

    publish_url = f'{deposition_url}/{deposition_id}/actions/publish'
    request = requests.post(publish_url, params={'access_token': token})

    return _check_request_response(request)


def delete_record(deposition_url: str, deposition_id: int, token: str) -> UploadStatus:
    """Method to delete an unpublished deposition.
    If id not provided, use deposition_id, else use provided id

    :param deposition_url: URL to make the Zenodo API request.
    :param deposition_id: Deposition id of the record to delete. Record can only be deleted
      if it was not published.
    :param token: API token for connecting to Zenodo.
    """

    # Create the request url
    request_url = f'{deposition_url}/{deposition_id}'

    logger.info('Delete url: {}'.format(request_url))
    request = requests.delete(request_url, params={'access_token': token})
    return _check_request_response(request)


def _check_request_response(response: requests.models.Response) -> Union[UploadStatus, None]:
    """Check the status code returned from an interaction with the Zenodo API.

    :param response: A response to an HTTP request.
    :return status_code: If status code represents success.
    :raises ZenodoException: If status code represents a failure.
    """

    if response.status_code in STATUS_SUCCESS:
        message = f'Request succeeded with status code: {response.status_code}'
        return UploadStatus(response.status_code, message)

    content = json.loads(response.text)

    if response.status_code == 400:
        message = f'Request failed with error: {response.status_code}. ' \
                  f'The details are: {content}.'

    elif response.status_code == 401:
        message = f'Request failed with error: {response.status_code}. This is ' \
                  'due to a bad access token.'

    elif response.status_code == 403:
        message = f'Request failed with error: {response.status_code}. This is' \
                  ' due to insufficient privileges.'

    elif response.status_code == 500:
        message = f'Zenodo server error {response.status_code}. It is likely to be their ' \
                  f'problem not ours. Details: {content}'

    else:
        message = f'Unclassified error: {response.status_code}. Details: {content}'

    logger.error(message)
    code = content["status"]
    message = content["message"]
    if "errors" in content:
        error_field = content["errors"][0]["field"]
        error_content = content["errors"][0]["message"]
        return UploadStatus(code, message, error_field, error_content)
    return UploadStatus(code, message)


def validate_metadata(raw_metadata: dict) -> Tuple[UploadStatus, dict]:
    """Compare the metadata to the schema and remove anything not allowed by Zenodo."""
    schema = zenodo_metadata.read_schema_from_file()
    try:
        validated_metadata = zenodo_metadata.validate_metadata(raw_metadata, schema)
    except zenodo_metadata.ZenodoMetadataException as e:
        upload_status = UploadStatus(401, str(e))
        checked_metadata = {}
    else:
        upload_status = UploadStatus(200, "Metadata successfully validated.")
        checked_metadata = {'metadata': validated_metadata}
    return upload_status, checked_metadata
