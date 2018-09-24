#!/usr/bin/env python

"""This module is implementing high level function to upload
and download Lightform data.


.. note::
    There are no verification of the validity of the schema used to validate
    the metadata which will be uploaded to Zenodo.
    This part should be done somewhere else. In a perfect world, the schema
    should be provided by Zenodo but it is not (yet) the case.


:Authors: Nicolas Gruel <nicolas.gruel@manchester.ac.uk>

:Copyright: IT Services, The University of Manchester

"""

# pylint: disable=locally-disabled, invalid-name

try:
    from .conf import logger
except ImportError:
    from conf import logger

import os
import json
import urllib
import yaml
import jsonschema


_dir = os.path.dirname(os.path.realpath(__file__))


class ZenodoMetadataException(Exception):
    """Class for exception
    """
    pass


ZENODO_VALID_PROPERTIES = ['publication_date', 'title', 'creators',
                           'description', 'doi', 'preserved_doi',
                           'keywords', 'notes', 'related_identifiers',
                           'relation', 'contributors', 'references',
                           'communities', 'grants', 'journal_title',
                           'journal_volume', 'journal_issue', 'journal_pages',
                           'conference_title', 'conference_acronym',
                           'conference_dates', 'conference_place',
                           'conference_url', 'conference_session',
                           'conference_session_part', 'imprint_publisher',
                           'imprint_isbn', 'partof_title', 'partof_pages',
                           'thesis_supervisors', 'thesis_university',
                           'subjects', 'version', 'language',
                           'name', 'affiliation', 'orcid', 'gnd',
                           'upload_type', 'publication_type', 'image_type',
                           'access_right', 'license', 'embargo_date',
                           'access_conditions'
                           ]


# Define the path where the schema file for zenodo is written
# at installation time
SCHEMAFILE=os.path.join(_dir, 'schemas', 'zenodo', 'metadata-1.0.0.yml')


class ZenodoMetadata(object):
    """Class to manage the Metadata needed for Zenodo.

    Attributes
    ----------

    """

    def __init__(self, metadata, schema=SCHEMAFILE):
        # Read the metadata zenodo file to verify
        self._metadata = None
        self.set_metadata(metadata)

        # Read the Zenodo yaml schema
        self._schema = None
        self.set_schema(schema)

    def set_schema(self, schema):

        if type(schema) is str:
            logger.info('Schema file use: {}'.format(schema))
            self._schema = self._read_schema(schema)
        elif type(schema) is dict:
            logger.info('Schema provided through dictionary object')
            if self._schema is None:
                self._schema = schema
            else:
                self._schema.update(schema)
        else:
            message = 'Something is wrong with the schema: {}.'.format(schema)
            logger.error(message)
            raise ZenodoMetadataException(message)

    def set_metadata(self, metadata):
        """Method to set metadata from a file or a dictionary.

        Parameter
        ---------
        metadata: str, dict
            - if it is a string it is the name of file which contains
              zenodo metadata (yaml format). It will read the metadata
              and set the attribute _metadata to it
            - if dictionary, it set the attribute _metadata to it

        Attribute
        ---------
        _metadata: dict
            dictionary which contains Zenodo metadata
        """
        if type(metadata) is str:
            logger.info('Metadata provided by file: {}'.format(metadata))
            self._metadata = self._read_metadata(metadata)
        elif type(metadata) is dict:
            logger.info('Metadata provided by dictionary.')
            if self._metadata is None:
                self._metadata = metadata
            else:
                self._metadata.update(metadata)
        elif metadata is None:
            logger.warn('Metadata are empty')
            self._metadata = metadata
        self._check_minimal()

    def get_metadata(self):
        """Method which will return Zenodo metadata

        This method will return a dictionary which contains Zenodo metadata.

        Return
        ------
        metadata: dict
            Dictionary which contains Zenodo metadata.
        """
        self.validate()
        return self._metadata

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

        # change communities identifier in lower case (only format accepted by zenodo)
        if 'communities' in _metadata:
            for _com in _metadata['communities']:
                _com['identifier'] = _com['identifier'].lower()

        return _metadata

    def _check_minimal(self):
        """Method to check that the minimal set of Metadata needed for Zenodo
        is present
        """

        if self._metadata is None:
            message = 'Metadata not provided'
            logger.error(message)
            raise ZenodoMetadataException(message)

        minimal_keys = ('title', 'upload_type', 'description', 'creators')

        for key in minimal_keys:
            if key not in self._metadata.keys():
                error = 'Missing metadata information: {}'.format(key)
                logger.error(error)
                raise ZenodoMetadataException(error)

        if 'access_right' not in self._metadata:
            self._metadata['access_right'] = 'open'
            logger.warning('Add metadata: "access_right" set to default value '
                           '"open"')

        if 'license' not in self._metadata:
            self._metadata['license'] = 'cc-by-4.0'
            logger.warning('Add metadata: "license" set to default value '
                           '"cc-by-4.0"')

        # Default value.(Should be done in schema)
        #TODO

        return True

    def validate(self):
        """Method which is verifying that the metadata does have the correct type
        and if the dependencies are respected.

        The dependencies have to be check because the value of a
        metadata can implied the presence of another one. For example,
        if *upload_type* (which is a necessary metadata) has the value
        *publication* that implied the presence of the metadata
        *publication_type*.
        """

        # Check if the minimal set of information are provided
        self._check_minimal()

        # Check validity of the license (if open or embargoed)
        self._check_license_availability()

        try:
            jsonschema.validate(self._metadata, self._schema)
        except jsonschema.exceptions.ValidationError as err:
            error = 'ValidationError: {}'.format(err.message)
            logger.error(error)
            raise ZenodoMetadataException(error)

        logger.info('Metadata should be ok to use for upload')

    def _check_license_availability(self, flicenses=None, opendefinition=False):
        """Method to verify the license

        Zenodo metadata des have an non-optional keyword *access_right*,
        that if it is set to open or embargoed an optional keyword
        **can** be added: license.
        The license in this case has to be considered as open by Zenodo and
        be part of the list provided by the
        `Open Definition License Service<https://licenses.opendefinition.org/>`_

        The method will look directly on internet where the service is providing
        a json file which contains all the acceptable license:

        https://licenses.opendefinition.org/licenses/groups/all.json

        This file is also provided by the software to be able to verify
        the validity of the license.

        .. important::
            The file provided by the software **could** be out-dated.
            Since the upload of the data on Zenodo will do the verification
            it is not a major problem but the user as to be careful.

        Parameter
        ---------

        update: boolean
            if True will update the license file
            TODO: NOT IMPLEMENTED YET

        Exception
        ---------
        raise exception if license does not exist in the list accepted by Zenodo
        as open.


        TODO: modify method to use file on disk before and if license not there,
        TODO: look at the file on internet and retest it.
        """

        # if access right is not 'open' or 'embargoed' there are no need to
        # test if the license is open compliant with Zenodo

        if not (self._metadata['access_right'] in ['open', 'embargoed']):
            logger.info('No need to check license for Zenodo upload.')
            return True

        # Get on the opendefinition website the file with the licenses
        # informations
        if opendefinition:
            licenses = self._get_opendefinition_file()

        # Get the licenses information from an input file or
        # from the default file
        else:

            if flicenses is None:
                flicenses = os.path.join(_dir, 'schemas', 'zenodo',
                                    'opendefinition-licenses.json')

            try:
                with open(flicenses) as f:
                    licenses = json.load(f)
                    logger.info(
                        'Use file: {} to validate license'.format(flicenses))
            except FileNotFoundError:
                licenses = self._get_opendefinition_file()

        if ('license' in self._metadata and
                self._metadata['access_right'] in ['open', 'embargoed']):
            self._metadata['license'] = self._metadata['license'].upper()
            mlicense = self._metadata['license'].upper()
            logger.info('License present in metadata file: '
                        '"{}"'.format(mlicense))
            logger.info('access_right: '
                        '"{}"'.format(self._metadata['access_right']))

            _tmp = ''
            for lic in licenses.keys():
                if lic.startswith(mlicense):
                    logger.info('license: "{}" validated.'.format(lic))
                    return True

            message = 'license: "{}" is not listed as ' \
                      'open by Zenodo'.format(self._metadata['license'])
            logger.error(message)
            raise ZenodoMetadataException(message)

    @staticmethod
    def _get_opendefinition_file():
        """Method which download the definition file for open source licenses
        accepted by Zenodo.

        Return
        ------
        licenses: dict
            a dictionnary which contains the informations the differents
            licenses.
        """
        url = 'https://licenses.opendefinition.org/licenses/groups/all.json'
        try:
            with urllib.request.urlopen(url) as f:
                licenses = json.load(f)
                logger.info(
                    'open licenses file use for validation: {}'.format(url))
        except urllib.error.URLError:
            message = 'Not possible to access to the list ' \
                      '(internet connection problem?): {}'.format(url)
            logger.error(message)
            raise ZenodoMetadataException(message)
        return licenses

    def _remove_extra_properties(self):
        """Method to remove properties which are not allowed by zenodo

        Jsonschema has a major limitation (it which does not allowed to use
        is in discussion to modify it in future iteration of the format).
        It does not allowed the usage of::

            additionalProperties: False

        when associated to combining schema.

        We are touching the problem describe as a
        `shortcoming <https://spacetelescope.github.io/understanding-json-schema/reference/combining.html#combining>`_
        that implied that we need to deal outside the json schema
        for verify that only Zenodo metadata are provided at the upload time.
        """

        keytoremove = []
        for key in self._metadata.keys():
            if key not in ZENODO_VALID_PROPERTIES:
                logger.warning('Zenodo metadata with '
                               'key invalid: {}'.format(key))
                keytoremove.append(key)

        for key in keytoremove:
            logger.warning('Invalid key: {} removed.'.format(key))
            del self._metadata[key]


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



# license available for access_right: open from
# https://licenses.opendefinition.org
#
# A machine readable format is available at:
#
# https://licenses.opendefinition.org/licenses/groups/all.json
# format :
# {
#   "id": "ODC-BY-1.0",
#   "domain_content": false,
#   "domain_data": true,
#   "domain_software": false,
#   "od_conformance": "approved",
#   "osd_conformance": "not reviewed",
#   "status": "active",
#   "title": "Open Data Commons Attribution License 1.0",
#   "url": "https://opendatacommons.org/licenses/by"
# }
# How to read it:
# licenses = urllib.request.urlopen('https://licenses.opendefinition.org/licenses/groups/all.json')
# import json
# licenses = json.load(licenses)
#
