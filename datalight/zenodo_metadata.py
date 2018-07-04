#!/usr/bin/env python

"""This module is implementing high level function to upload
and download Lightform data.

:Authors: Nicolas Gruel <nicolas.gruel@manchester.ac.uk>

:Copyright: IT Services, The University of Manchester

"""

# pylint: disable=locally-disabled, invalid-name

import yaml
import jsonschema

try:
    from .__init__ import __version__
    from .conf import logger
except ImportError:
    from __init__ import __version__
    from conf import logger


class ZenodoMetadataException(Exception):
    """Class for exception
        """
    pass


class ZenodoMetadata(object):
    """Class to manage the Metadata needed for Zenodo.

    Attributes
    ----------

    """

    def __init__(self, metadata=None, schema='metadata-1.0.0.yaml'):
        # Read the metadata zenodo file to verify
        if type(metadata) is dict:
            logger.info('Metadata provided through dictionary object')
            self._metadata = metadata
        else:
            self.setMetadata(metadata)

        # Read the Zenodo yaml schema
        if type(schema) is dict:
            logger.info('Schema provided through dictionary object')
            self._schema = schema
        else:
            self.setSchema(schema)

    def setSchema(self, schema):

        if type(schema) is str:
            logger.info('Schema file use: {}'.format(schema))
            _schema = self._read_schema(schema)
        else:
            message = 'Something is wrong with the schema: {}.'.format(schema)
            logger.error(message)
            raise ZenodoMetadataException(message)

    def setMetadata(self, metadata):
        if type(metadata) is str:
            logger.info('Metadata provided by file: {}'.format(metadata))
            self._metadata = self._read_metadata(metadata)
        elif metadata is None:
            logger.warn('Metadata are empty')
            self._metadata = metadata

    @staticmethod
    def _read_schema(fschema):
        """Method to read the schema.

        Parameter
        ---------
        schema: str
            Name of the file which contain the definition of the schema

        Return
        ------
        _schema: dict
            dictionary which contains the schema used to validate the metadata.

        """

        logger.info('Read schema from: {}'.format(fschema))
        try:
            with open(fschema) as f:
                _schema = yaml.load(f)
        except FileNotFoundError as err:
            message = 'Schema file not founded.'.format(fschema)
            logger.error(message)
            raise ZenodoMetadataException(message)
        return _schema

    @staticmethod
    def _read_metadata(fmetadata):
        """Method to read Zenodo metadata file

        """
        logger.info('Read metadata from: {}'.format(fmetadata))
        try:
            with open(fmetadata) as f:
                _metadata = yaml.load(f)
        except FileNotFoundError as err:
            message = 'Metadata file not founded.'.format(fmetadata)
            logger.error(message)
            raise ZenodoMetadataException(message)
        return _metadata

    def _check_minimal(self):
        """Method to check that the minimal set of Metadata needed for Zenodo
        is present
        """

        minimal_keys = ('title', 'upload_type', 'description', 'creators',
                        'access_right')

        for key in minimal_keys:
            if key not in self._metadata['metadata']:
                error = 'Missing metadata information: {}'.format(key)
                logger.error(error)
                raise ZenodoMetadataException(error)

        return True

    def _verify_metadata(self):
        """Method which is verifying that the metadata does have the correct type
        and if the dependencies are respected.

        The dependencies have to be check because the value of a
        metadata can implied the presence of another one. For example,
        if *upload_type* (which is a necessary metadata) has the value
        *publication* that implied the presence of the metadata
        *publication_type*.
        """
        self._check_minimal()
        try:
            jsonschema.validate(self._metadata, self._schema)
        except jsonschema.exceptions.ValidationError as err:
            error = 'ValidationError: {}'.format(err.message)
            logger.error(error)
            raise ZenodoMetadataException(error)

    # def modify_metadata(self, metadata):
    #     """Method to modify the metadata after having upload a file.
    #
    #     Metadata dictionary should contains at least the following keys:
    #     title: str
    #     upload_type: str ['publication', 'poster', 'presentation', 'dataset',
    #                       'image', video', 'software', 'lesson', 'other']
    #     'description': str
    #     'creators': list of dictionaries which contains name and affiliation
    #     e.g.:
    #     metadata = { 'metadata': { 'title': 'My first upload',
    #                                'upload_type': 'poster',
    #                                'description': 'This is my first upload',
    #                                'creators': [{'name': 'Doe, John',
    #                                              'affiliation': 'Zenodo'}]
    #                }
    #
    #     Parameters
    #     ----------
    #     metadata: dict,
    #         dictionary which will contains the zenodo metadata associated
    #         to the file(s) uploaded using the deposition id.
    #
    #     Return
    #     ------
    #     boolean
    #         return True if everything went well, false in other hand.
    #     """
    #
    #     if metadata is not dict:
    #         logger.error('Metadata should be given in a dictionary form')
    #     pass
