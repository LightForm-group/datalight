#!/usr/bin/env python

"""This module is implementing high level function to upload
and download Lightform data.

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


class ZenodoException(Exception):
    """Class for exception
        """
    pass


class ZenodoMetadata(object):

    # _upload_type = ('publication',
    #                 'poster',
    #                 'presentation',
    #                 'dataset',
    #                 'image',
    #                 'video',
    #                 'software',
    #                 'lesson',
    #                 'other')
    #
    # _publication_type = ('book',
    #                      'section',
    #                      'conferencepaper',
    #                      'article',
    #                      'patent',
    #                      'preprint',
    #                      'report',
    #                      'softwaredocumentation',
    #                      'thesis',
    #                      'technicalnote',
    #                      'workingpaper',
    #                      'other')
    #
    # _image_type = ('figure',
    #                'plot',
    #                'drawing',
    #                'diagram',
    #                'photo',
    #                'other')
    #
    # _access_right = ('open',
    #                  'embargoed',
    #                  'restricted',
    #                  'closed')
    #
    # # dependency contains the
    # _metadata_requirement = { 'upload_type': {'required': True,
    #                                           'default': None,
    #                                           'child': ('publication',
    #                                                     'image')},
    #                           'image_type': }

    def __init__(self):
        pass

    def verify_minimal_metadata(self):
        # TODO
        pass

    @staticmethod
    def __verify_upload_type(self, upload_type):
        """

        :param self:
        :param upload_type:
        :return:
        """

        # if upload_type is not in _publication_type:
        #     message = 'Upload type not available'
        #     logger.error(message)
        #     raise ZenodoException(message)
        pass

    def modify_metadata(self, metadata):
        """Method to modify the metadata after having upload a file.

        Metadata dictionary should contains at least the following keys:
        title: str
        upload_type: str ['publication', 'poster', 'presentation', 'dataset',
                          'image', video', 'software', 'lesson', 'other']
        'description': str
        'creators': list of dictionaries which contains name and affiliation
        e.g.:
        {
            'title': 'My first upload',
            'upload_type': 'poster',
            'description': 'This is my first upload',
            'creators': [{'name': 'Doe, John',
                          'affiliation': 'Zenodo'}]
        }



        Parameters
        ----------
        metadata: dict,
            dictionary which will contains the zenodo metadata associated
            to the file(s) uploaded using the deposition id.

        Return
        ------
        boolean
            return True if everything went well, false in other hand.
        """

        if metadata is not dict:
            logger.error('Metadata should be given in a dictionary form')




        pass


class Zenodo(object):
    """Class to upload and download files on Zenodo

    Attributes
    ----------
    access_token: str, optional
        Token that need to be provided to Zenodo to be able to upload.
        The attribute is optional.
    sandbox_token: str
        Token similar to the one above but to upload on the sandbox zone.
        Files uploaded
    """

    # TODO verify that there are no json file where this information
    # can be downloaded.

    def __init__(self, token, sandbox=False):

        self._token = token
        self.sandbox = sandbox

        if sandbox:
            self.api_baseurl = 'https://sandbox.zenodo.org/api/'
        else:
            self.api_baseurl = 'https://zenodo.org/api/'

        self.depositions_url = self.api_baseurl + 'deposit/depositions'
        self.deposition_id = None

        self.status_code = None

    def __test_token(self):
        """ Function to test if token could be valid

        Exception
        ---------
        ZenodoException
            if token not define (token = None).

        """
        if self._token is None:
            message = 'No Zenodo token provided'
            logger.error(message)
            raise ZenodoException(message)

    def connection(self):
        """Method to test that connection with zenodo website is working.

        Exception
        ---------
        ZenodoException
            if token not define (token = None) or
            if connection return status >= 400
        """
        # Test if Token defined and access zenodo to test the token if exist
        self.__test_token()

        request = requests.get(self.depositions_url,
                               params={'access_token': self._token})
        self.status_code = request.status_code
        logger.debug('Status code: {}'.format(self.status_code))

        # Raise exception if Error from Zenodo (status >= 400)
        if self.status_code >= 400:
            message = 'Access token not accepted by Zenodo. ' \
                      'Error: {}'.format(self.status_code)
            logger.error(message)
            self._token = None
            raise ZenodoException(message)

    def get_deposition_id(self):
        """Method to obtain the deposition id need to upload documents to Zenodo

        Attributes
        ----------
        request:

        deposition_id: int
            Deposition id gave by Zenodo deposition api to be used to upload
            files and metadata.

        Exception
        ---------
        ZenodoException
            if token not define (token = None) or
            if connection return status >= 400
        """
        headers = {'Content-Type': 'application/json'}

        # Test if Token defined and access zenodo to test the token if exist
        self.__test_token()

        request = requests.post(self.depositions_url,
                                params={'access_token': self._token},
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
            if token not define (token = None) or
            if connection return status >= 400
        """
        # Test if token was defined
        self.__test_token()

        # Use provided if if not None. If not provided use self.deposition_id

        if id is not None:
            self.deposition_id = id

        # Create the request url
        request_url = (self.depositions_url + '/{}'.format(self.deposition_id))

        if self.depositions_url is not None:
            logger.info('Delete url: {}'.format(request_url))
            request = requests.delete(request_url,
                                      params={'access_token': self._token})
            self.status_code = request.status_code
            logger.debug('Status code: {}'.format(self.status_code))
        else:
            message = 'Request_url does not exist or bad token. ' \
                      'Error: {}'.format(self.status_code)
            logger.error(message)
            raise ZenodoException(message)

        if self.status_code >= 400:
            message = "Delete failed with error: {}".format(self.status_code)
            logger.error(message)
            raise ZenodoException(message)

    def upload_file(self, filename, path=None):
        """Method to upload a file to Zenodo

        Parameters
        ----------
        filename: str
            Name of the file to upload
        path: str, optional
            Path of where the file is. If given the file that will be upload

        Exception
        ---------
        ZenodoException
            if token not define (token = None) or
            if connection return status >= 400
        """

        # Test if token was defined
        self.__test_token()

        # If the deposition_id was not run before to obtain the id to uploads
        if type(self.deposition_id) is not int:
            self.get_deposition_id()

        if path is not None:
            filename = os.path.join(path, filename)

        # Create the data dictionary which contain the name of the file
        data = {'filename': filename}
        logger.info('filename: {}'.format(filename))

        # Open the file to upload in binary mode.
        files = {'file': open(filename, 'rb')}

        # Create the url to upload with the deposition_id
        url = self.depositions_url + '/{}/files'.format(self.deposition_id)
        logger.info('url: {}'.format(url))

        # upload the file

        request = requests.post(url,
                                params={'access_token': self._token},
                                data=data,
                                files=files)
        self.status_code = request.status_code

        # Test that everything went as expected
        if self.status_code < 400:
            logger.info('Deposition id: {}'.format(self.deposition_id))
            logger.debug('Status code: {}'.format(self.status_code))
            return

        if self.status_code >= 500:
            message = 'Server connection failed ' \
                      'with error: {}'.format(self.status_code)
            logger.error(message)
            #raise ZenodoException(message) # Break the test....
            return

        if self.status_code >= 400:
            message = 'upload file failed ' \
                      'with error: {}'.format(self.request.status_code)
            logger.error(message)
            raise ZenodoException(message)

    def publish(self):
        """Method which will publish the deposition linked with the id.

        BE CAREFUL: after publishing it is not possible to delete anything.

        Exception
        ---------
        ZenodoException
            if token not define (token = None) or
            if connection return status >= 400
        """
        # Test if token was defined
        self.__test_token()

        publish_url = self.depositions_url + \
                      '/{}/actions/publish'.format(self.deposition_id)
        request = requests.post(publish_url,
                                params={'access_token': self._token})

        self.status_code = request.status_code

        # Test that everything went as expected
        if self.status_code == 202:
            logger.info('Deposition id: {}'.format(self.deposition_id))
            logger.debug('Status code: {}'.format(self.status_code))
            return

        if self.status_code >= 500:
            message = 'Server connection failed ' \
                      'with error: {}'.format(self.request.status_code)
            logger.error(message)
            #raise ZenodoException(message) # Break the test....
            return

        if self.status_code >= 400:
            message = 'Publish file failed ' \
                      'with error: {}'.format(self.request.status_code)
            logger.error(message)
            raise ZenodoException(message)

    def download_file(self):
        """

        """
        raise "Not implemented"

    def metadata_verify(self):
        """


        """
        raise "Not implemented"