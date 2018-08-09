#!/usr/bin/env python

"""This module is implementing high level function to upload
and download data on Zenodo.

:Authors: Nicolas Gruel <nicolas.gruel@manchester.ac.uk>

:Copyright: IT Services, The University of Manchester

"""
import os

# pylint: disable=locally-disabled, invalid-name
try:
    from .conf import logger
except ImportError:
    from conf import logger

import requests
import json


class ZenodoException(Exception):
    """Class for exception
        """
    pass


class Zenodo(object):
    """Class to upload and download files on Zenodo

    Attributes
    ----------
    token: str, optional
        Token that need to be provided to Zenodo to be able to upload.
        The attribute is optional.
    sandbox_token: str
        Token similar to the one above but to upload on the sandbox zone.
        Files uploaded
    """

    # TODO verify that there are no json file where this information
    # can be downloaded.

    def __init__(self, token, sandbox=False):

        self.token = token

        if sandbox:
            self.api_baseurl = 'https://sandbox.zenodo.org/api/'
        else:
            self.api_baseurl = 'https://zenodo.org/api/'

        self.depositions_url = self.api_baseurl + 'deposit/depositions'
        self.deposition_id = None

        self.status_code = None

    def _verify_token(self):
        """ Function to test if token could be valid

        Exception
        ---------
        ZenodoException
            if token not define (token = None).

        """
        if self.token is None:
            message = 'No Zenodo token provided'
            logger.error(message)
            raise ZenodoException(message)

    @staticmethod
    def _check_status_code(status_code):
        """Method to test that the request went as expected.

        Parameters
        ----------
        status_code: int
            status code return by the request (requests.status_code)

        Exceptions
        ----------
        ZenodoException:
            Raise exception if the request ended with a problem

        .. note:
            If the error is a Server conncetion problem,
            the exception is not raised (problem with the test in other hand)
        """
        # Test that everything went as expected
        if status_code < 400:
            logger.debug('Request succeed '
                         'with status code: {}'.format(status_code))
            return status_code

        if status_code >= 500:
            message = 'Server connection failed ' \
                      'with error: {}'.format(status_code)
            logger.error(message)
            raise ZenodoException(message)

        if status_code >= 400:
            message = 'Request failed ' \
                      'with error: {}'.format(status_code)
            logger.error(message)
            raise ZenodoException(message)

    def connection(self):
        """Method to test that connection with zenodo website is working.

        Exception
        ---------
        ZenodoException
            raise if token not define (token = None) or if connection
            return status >= 400
        """
        # Test if Token defined and access zenodo to test the token if exist
        self._verify_token()

        request = requests.get(self.depositions_url,
                               params={'access_token': self.token})
        self.status_code = request.status_code
        logger.debug('Status code: {}'.format(self.status_code))

        # Raise exception if Error from Zenodo (status >= 400)
        if self.status_code >= 400:
            message = 'Access token not accepted by Zenodo. ' \
                      'Error: {}'.format(self.status_code)
            logger.error(message)
            self.token = None
            raise ZenodoException(message)

    def get_deposition_id(self):
        """Method to obtain the deposition id need to upload documents to Zenodo

        Attributes
        ----------
        deposition_id: int
            Deposition id gave by Zenodo deposition api to be used to upload
            files and metadata.

        Exception
        ---------
        ZenodoException
            raise if token not define (token = None) or if connection
            return status >= 400
        """
        headers = {'Content-Type': 'application/json'}

        # Test if Token defined and access zenodo to test the token if exist
        self._verify_token()

        request = requests.post(self.depositions_url,
                                params={'access_token': self.token},
                                json={},
                                headers=headers)
        self.status_code = request.status_code
        logger.debug('Status code: {}'.format(self.status_code))
        logger.debug('deposition url: {}'.format(self.depositions_url))

        # Test that the request succeed
        if self.status_code >= 400:
            message = ('Deposition id not obtain, '
                       'error: {}'.format(self.status_code))
            logger.error(message)
            raise ZenodoException(message)
        else:
            self.deposition_id = request.json()['id']
            logger.info('Deposition id: {}'.format(self.deposition_id))
            logger.info('Deposition url: {}'.format(self.deposition_id))

    def delete(self, id=None):
        """Method to delete deposition.

        note: it worked only if it is not publish.

        Exception
        ---------
        ZenodoException
            raise if token not define (token = None) or if connection
            return status >= 400
        """
        # Test if token was defined
        self._verify_token()

        # Use provided if if not None. If not provided use self.deposition_id

        if id is not None:
            self.deposition_id = id

        # Create the request url
        request_url = (self.depositions_url + '/{}'.format(self.deposition_id))

        logger.info('Delete url: {}'.format(request_url))
        try:
            request = requests.delete(request_url,
                                      params={'access_token': self.token})
            self.status_code = request.status_code
            logger.debug('Status code: {}'.format(self.status_code))
            if self.status_code >= 400:
                raise ZenodoException
        except ZenodoException:
            message = 'Request_url does not exist or bad token. ' \
                      'Error: {}'.format(self.status_code)
            logger.error(message)
            raise ZenodoException(message)

#        self._check_status_code(self.status_code)

    def upload_files(self, filenames, path=None, id=None):
        """Method to upload a file to Zenodo

        Parameters
        ----------
        filenames: str
            Name of the file(s) to upload
        path: str, optional
            Path of where the file(s) is.
        id: int
            deposition id of the record where the file(s) will be updated

        Exception
        ---------
        ZenodoException
            raise if token not define (token = None) or if connection
            return status >= 400
        """

        # Test if token was defined
        self._verify_token()

        # If the deposition_id was not run before to obtain the id to uploads
        # TODO: Perhaps is it better to raise an exception
        # if type(self.deposition_id) is not int:
        #     self.get_deposition_id()

        if type(id) is int:
            self.deposition_id = id

        # Create the url to upload with the deposition_id
        url = self.depositions_url + '/{}/files'.format(self.deposition_id)
        logger.info('url: {}'.format(url))

        # if filenames is only a file convert it to list
        if type(filenames) is str:
            filenames = [filenames]

        logger.info('Deposition id: {}'.format(self.deposition_id))

        status_code = []
        for filename in filenames:
            if path is not None:
                filename = os.path.join(path, filename)

            # Create the zenodo data dictionary which contain
            # the name of the file
            data = {'filename': filename}
            logger.info('filename: {}'.format(filename))

            # Open the file to upload in binary mode.
            files = {'file': open(filename, 'rb')}

            # upload the file

            request = requests.post(url,
                                    params={'access_token': self.token},
                                    data=data,
                                    files=files)
            status_code.append(request.status_code)
            self._check_status_code(request.status_code)

        self.status_code = max(status_code)
        self._check_status_code(self.status_code)

    def upload_metadata(self, metadata, id=None):
        """Upload metadata to Zenodo repository.

        After creating the request and upload the file(s) we need to update
        the metadata needed by Zenodo related to the record.

        Parameters
        ----------
        metadata: dict
            dictionary which contains zenodo metadata

        id: int
            deposition id of the record where the metadata will be updated

        """
        self._verify_token()

        # Todo replace by test of zenodometadata
        if type(metadata) is not dict or 'metadata' not in metadata:
            raise ZenodoException('Metadata should be '
                                  'dictionary with one key: "metadata" ')

        if type(id) is int:
            self.deposition_id = id

        # Create the url to upload with the deposition_id
        url = self.depositions_url + '/{}'.format(self.deposition_id)
        logger.info('url: {}'.format(url))

        headers = {"Content-Type": "application/json"}
        request = requests.put(url,
                               params={'access_token': self.token},
                               data=json.dumps(metadata),
                               headers=headers)

        self.status_code = request.status_code
        self._check_status_code(self.status_code)

    def publish(self):
        """Method which will publish the deposition linked with the id.

        .. warning:

            After publishing it is not possible to delete anything.

        Exception
        ---------
        ZenodoException
            raise if token not define (token = None) or if connection
            return status >= 400
        """
        # Test if token was defined
        self._verify_token()

        publish_url = self.depositions_url + \
                      '/{}/actions/publish'.format(self.deposition_id)
        request = requests.post(publish_url,
                                params={'access_token': self.token})

        self.status_code = request.status_code

        # Test that everything went as expected
        if self.status_code == 202:
            logger.info('Deposition id: {}'.format(self.deposition_id))
            logger.debug('Status code: {}'.format(self.status_code))
            return

        self._check_status_code(self.status_code)

    def download_files(self):
        """Method to download file present in a specific record

        """
        raise "Not implemented"

    def metadata_verify(self):
        """If implemented will be wrapper around the ZenodoMetadata class
        """
        raise "Not implemented"