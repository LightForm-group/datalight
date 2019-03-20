"""This module does something with metadata."""

import json
import urllib
import yaml
import jsonschema
import pathlib

from datalight.common import logger


class ZenodoMetadataException(Exception):
    """Class for exception"""
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

# Define the path to the Zenodo upload metadata schema
SCHEMAS_DIR = pathlib.Path(__file__).parent / pathlib.Path('schemas')
SCHEMA_FILE = SCHEMAS_DIR / pathlib.Path('zenodo/zenodo_upload_metadata_schema.json5')


class ZenodoMetadata(object):
    """Class to manage the Metadata needed for a Zenodo upload."""

    def __init__(self, metadata_path, schema_path=SCHEMA_FILE):
        """Read the metadata and then the metadata schema.
        :param metadata_path: (path) the path to the file containing metadata.
        :param schema_path: (path) the path to the file containing the metadata schema.

        :attribute _metadata: (dict) the metadata
        :attribute _schema: (MetadataSchema object) the metadata schema
        """

        self._metadata = None
        self.set_metadata(metadata_path)

        self._schema = _MetadataSchema(schema_path)

    def set_metadata(self, metadata_path):
        """Method to set metadata from a file.

        :param metadata_path: (path) A path to a file which contains zenodo metadata (yaml format).
        """
        if isinstance(metadata_path, str) or issubclass(type(metadata_path), pathlib.Path):
            logger.info('Metadata provided by file: {}'.format(metadata_path))
            self._metadata = self._read_metadata(metadata_path)
            self._check_minimal()
        else:
            raise TypeError("Metadata of wrong type. Needs to be a path.")

    @staticmethod
    def _read_metadata(metadata_path):
        """Method to read Zenodo metadata file
        :param metadata_path: (path) Path to metadata file.
        """
        logger.info('Read metadata from: {}'.format(metadata_path))
        try:
            with open(metadata_path) as f:
                metadata = yaml.load(f)
        except FileNotFoundError:
            message = 'Metadata file {} not found.'.format(metadata_path)
            logger.error(message)
            raise ZenodoMetadataException(message)

        return metadata

    def get_metadata(self):
        """Method which validates and returns a dictionary of metadata.

        :returns metadata: (dict) Metadata for a deposition.
        """
        self.validate()
        return self._metadata

    def _check_minimal(self):
        """Method to check that the minimal set of Metadata needed for Zenodo
        is present
        """

        if self._metadata is None:
            message = 'Metadata not provided'
            logger.error(message)
            raise ZenodoMetadataException(message)

        minimal_keys = ('title', 'upload_type', 'description',
                        'creators', 'access_right', 'license')

        for key in minimal_keys:
            if key not in self._metadata.keys():
                error = 'Missing metadata information: {}'.format(key)
                logger.error(error)
                raise ZenodoMetadataException(error)

        return True

    def validate(self):
        """Method which verifies that the metadata have the correct type and that
         dependencies are respected."""

        # Check if the minimal set of information are provided
        self._check_minimal()

        # Check validity of the license (if open or embargoed)
        license_checker = _LicenseStatus
        if _LicenseStatus.license_valid is False:
            logger.error("Invalid licence type. access_right is 'open' or 'embargoed' and {}"
                         "is not a valid Open License.".format(license_checker.license))

        try:
            jsonschema.validate(self._metadata, self._schema)
        except jsonschema.exceptions.ValidationError as err:
            error = 'ValidationError: {}'.format(err.message)
            logger.error(error)
            raise ZenodoMetadataException(error)

        logger.info('Metadata should be ok to use for upload')

    def _remove_extra_properties(self):
        """Method to remove properties which are not allowed by zenodo

        Jsonschema has a major limitation, it does not allow the usage of::

            additionalProperties: False

        when associated to combining schema.

        We are touching the problem describe as a
        `shortcoming <https://spacetelescope.github.io/understanding-json-schema/reference/combining.html#combining>`_
        that implied that we need to deal outside the json schema
        for verify that only Zenodo metadata are provided at the upload time.
        """

        key_to_remove = []
        for key in self._metadata.keys():
            if key not in ZENODO_VALID_PROPERTIES:
                logger.warning('Zenodo metadata with key invalid: {}'.format(key))
                key_to_remove.append(key)

        for key in key_to_remove:
            logger.warning('Invalid key: {} removed.'.format(key))
            del self._metadata[key]


class _MetadataSchema:
    """An object representing the metadata schema for an upload"""

    def __init__(self, schema_path):
        self._schema = None
        self.set_schema(schema_path)

    def set_schema(self, schema):
        """Validate the path of the schema."""
        if isinstance(schema, str) or issubclass(type(schema), pathlib.Path):
            logger.info('Schema file use: {}'.format(schema))
            self._schema = self._read_schema(schema)
        else:
            message = 'Something is wrong with the schema: {}.'.format(schema)
            logger.error(message)
            raise ZenodoMetadataException(message)

    @staticmethod
    def _read_schema(schema_path):
        """Method to read the schema.

        :param schema_path: (path) Name of the file which contains the definition of the schema
        :returns _schema: (dict) The schema used to validate the metadata.
        """

        logger.info('Read schema from: {}'.format(schema_path))
        try:
            with open(schema_path) as f:
                _schema = json.load(f)
        except FileNotFoundError:
            message = 'Schema file not found.'.format(schema_path)
            logger.error(message)
            raise ZenodoMetadataException(message)
        return _schema


class _LicenseStatus:
    """An object representing the license status of a metadata file.

    If access_right is not open or embargoed then any license is valid.
    If access_right is open or embargoed then the license must be an Open one
    as defined by the
    `Open Definition License Service<https://licenses.opendefinition.org/>`_
    """

    license = ""
    access_right = ""
    open_licenses = {}
    license_valid = False

    def __init__(self, metadata_license, access_right):
        """ Initialise license_status object.

        :param metadata_license: (string) The license from the metadata provided for upload.
        :param access_right: (string) The access_right from the metadata provided for upload.
        """
        self.license = metadata_license
        self.access_right = access_right
        if self.access_right in ["open", "embargoed"]:
            self.open_licenses = self._get_open_licenses()
        self._verify_license()

    def _get_open_licenses(self):
        # Try to retrieve the latest open licenses from the internet.
        open_licenses = self._get_internet_open_licenses()

        # If the open licenses cannot be downloaded, read them from a local file instead.
        if open_licenses is None:
            open_licenses = self._get_local_open_licenses()
        return open_licenses

    @staticmethod
    def _get_internet_open_licenses():
        """Download the definition file for open source licenses accepted by Zenodo.

        :returns licenses: (dict) Information about the different license types.
        if licenses cannot be accessed, returns none.
        """
        url = 'https://licenses.opendefinition.org/licenses/groups/all.json'
        try:
            with urllib.request.urlopen(url) as f:
                licenses = json.load(f)
                logger.info('open licenses file use for validation: {}'.format(url))
                return licenses
        except urllib.error.URLError:
            logger.warning('Not possible to access open license list from: {}'.format(url))
            return None

    @staticmethod
    def _get_local_open_licenses():
        """Get open license definitions from a local file.

        :returns open_licenses: (dict) details of open licenses.
        """
        license_path = SCHEMAS_DIR / pathlib.Path('zenodo/opendefinition-licenses.json')
        try:
            with open(license_path) as f:
                open_licenses = json.load(f)
                logger.info('Using file: {} to validate license'.format(license_path))
                return open_licenses
        except FileNotFoundError:
            error = "Could not get open license definitions a local file {}.".format(license_path)
            logger.error(error)
            raise ZenodoMetadataException(error)

    def _verify_license(self):
        """Method to verify the status of the metadata license."""

        if not (self.access_right in ['open', 'embargoed']):
            logger.info('No need to check license for Zenodo upload.')
            self.license_valid = True
        else:
            self.license = self.license.upper()

            logger.info('Specified license type is: {}'.format(self.license))
            logger.info('access_right: "{}"'.format(self.access_right))

            for lic in self.open_licenses.keys():
                if lic.startswith(self.license):
                    logger.info('license: "{}" validated.'.format(lic))
                    self.license_valid = True
