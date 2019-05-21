"""This module processes and validates metadata."""

import json
import urllib
import pathlib
import yaml
import jsonschema

from datalight.common import logger


class ZenodoMetadataException(Exception):
    """Class for exception"""


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


class ZenodoMetadata:
    """Class to manage the Metadata needed for a Zenodo upload.

    general schema for usage is:
    set_schema()
    set_metadata()
    validate_metadata()
    """

    def __init__(self):
        """Initialise a Metadata object.

        :attribute _metadata: (dict) the metadata
        :attribute _schema: (MetadataSchema object) the metadata schema
        """

        self.metadata = None
        self.schema = None
        self.schema_path = SCHEMA_FILE
        self.metadata_validated = False

    def set_schema(self):
        """Method to read the schema. Reads schema from self.schema_path
        Stores schema dictionary in self.schema"""
        logger.info('Reading schema from: {}'.format(self.schema_path))
        try:
            with open(self.schema_path) as input_file:
                schema = json.load(input_file)
                self.schema = schema
        except FileNotFoundError:
            message = 'Schema file: {} not found.'.format(self.schema_path)
            logger.error(message)
            raise ZenodoMetadataException(message)

    def set_metadata(self, metadata_path):
        """Method to set metadata from a file.

        :param metadata_path: (path) A path to a file which contains zenodo metadata (yaml format).
        """
        if isinstance(metadata_path, str) or issubclass(type(metadata_path), pathlib.Path):
            logger.info('Metadata provided by file: {}'.format(metadata_path))
            self.metadata = self._read_metadata(metadata_path)
        elif isinstance(metadata_path, dict):
            self.metadata = metadata_path
            self.metadata["creators"] = {"author_name": self.metadata.pop("author_name"),
                                         "affiliation": self.metadata.pop("affiliation"),
                                         "orcid": self.metadata.pop("orcid")}
        else:
            raise TypeError("Metadata path of wrong type. Needs to be a path.")

    @staticmethod
    def _read_metadata(metadata_path):
        """Method to read Zenodo metadata file
        :param metadata_path: (path) Path to metadata file.
        """
        logger.info('Read metadata from: {}'.format(metadata_path))
        try:
            with open(metadata_path) as input_file:
                metadata = yaml.load(input_file, Loader=yaml.FullLoader)
        except FileNotFoundError:
            message = 'Metadata file {} not found.'.format(metadata_path)
            logger.error(message)
            raise ZenodoMetadataException(message)

        return metadata

    def validate_metadata(self):
        """Method which verifies that the metadata have the correct type and that
         dependencies are respected."""

        if self.metadata is None:
            print("Metadata not set. Use set_metadata method.")
            raise ZenodoMetadataException
        if self.schema is None:
            print("Schema not set. Use set_schema method.")
            raise ZenodoMetadataException

        # Validate metadata before license to be sure that the "license" and "access_right"
        # keys are present.
        try:
            jsonschema.validate(self.metadata, self.schema)
        except jsonschema.exceptions.ValidationError as err:
            error = 'ValidationError: {}'.format(err.message)
            logger.error(error)
            raise ZenodoMetadataException(error)

        # Check validity of the license (if open or embargoed)
        license_checker = _LicenseStatus(self.metadata["license"], self.metadata["access_right"])
        license_checker.validate_license()
        if license_checker.license_valid is False:
            logger.error("Invalid licence type. access_right is 'open' or 'embargoed' and {}"
                         "is not a valid Open License.".format(license_checker.license))
            raise ZenodoMetadataException

        self._remove_extra_properties()
        self.metadata_validated = True

        logger.info('Metadata have been validated successfully.')

    def _remove_extra_properties(self):
        """Method to remove properties which are not allowed by zenodo.

        Json-schema has a major limitation, it does not allow the usage of::

            additionalProperties: False

        when using the "allOf" keyword.

        This problem is described as a shortcoming
        `<https://json-schema.org/understanding-json-schema/reference/combining.html>`_
        which implies that we need to deal with this outside the json schema to
        verify that only Zenodo metadata are provided. This is likely to be resolved in
        json-schema draft-8 some time in 2019.
        """

        keys_to_remove = []
        for key in self.metadata.keys():
            if key not in ZENODO_VALID_PROPERTIES:
                logger.warning('Zenodo metadata with key invalid: {}. Key removed.'.format(key))
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.metadata[key]


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
            with urllib.request.urlopen(url) as input_file:
                licenses = json.load(input_file)
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
            with open(license_path) as input_file:
                open_licenses = json.load(input_file)
                logger.info('Using file: {} to validate license'.format(license_path))
                return open_licenses
        except FileNotFoundError:
            error = "Could not get open license definitions from local file {}.".format(
                license_path)
            logger.error(error)
            raise ZenodoMetadataException(error)

    def validate_license(self):
        """Method to verify the status of the metadata license."""

        if not (self.access_right in ['open', 'embargoed']):
            logger.info('No need to check license for Zenodo upload.')
            self.license_valid = True
        else:
            metadata_license = self.license.upper()

            logger.info('Specified license type is: {}'.format(self.license))
            logger.info('access_right: "{}"'.format(self.access_right))

            for lic in self.open_licenses.keys():
                if lic.startswith(metadata_license):
                    logger.info('license: "{}" validated.'.format(lic))
                    self.license_valid = True
                    break
