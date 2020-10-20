"""This module processes and validates metadata."""
import json
import urllib
import pathlib
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


def read_schema_from_file() -> dict:
    """Method to read the schema. Reads schema from self.schema_path
    Stores schema dictionary in self.schema"""
    logger.info(f'Reading schema from: {SCHEMA_FILE}')
    try:
        with open(SCHEMA_FILE) as input_file:
            return json.load(input_file)
    except FileNotFoundError:
        raise ZenodoMetadataException(f'Schema file: {SCHEMA_FILE} not found.')


def validate_metadata(metadata: dict, schema: dict) -> dict:
    """Method which verifies that the metadata have the correct type and that
     dependencies are respected."""

    # Validate metadata before license to be sure that the "license" and "access_right"
    # keys are present.
    try:
        jsonschema.validate(metadata, schema)
    except jsonschema.exceptions.ValidationError as err:
        raise ZenodoMetadataException(f'ValidationError: {err.message}')

    # Check validity of the license (if open or embargoed)
    license_checker = _LicenseStatus(metadata["license"], metadata["access_right"])
    license_checker.validate_license()
    if license_checker.license_valid is False:
        logger.error("Invalid licence type. access_right is 'open' or 'embargoed' and {}"
                     "is not a valid Open License.".format(license_checker.license))
        raise ZenodoMetadataException

    logger.info('Metadata have been validated successfully.')
    metadata = remove_extra_properties(metadata)
    return metadata


def remove_extra_properties(metadata: dict) -> dict:
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
    for key in metadata.keys():
        if key not in ZENODO_VALID_PROPERTIES:
            logger.warning(f'Zenodo metadata with key invalid: {key}. Key removed.')
            keys_to_remove.append(key)

    for key in keys_to_remove:
        del metadata[key]

    return metadata


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
                logger.info(f'open licenses file use for validation: {url}')
                return licenses
        except urllib.error.URLError:
            logger.warning(f'Not possible to access open license list from: {url}')
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
                logger.info(f'Using file: {license_path} to validate license')
                return open_licenses
        except FileNotFoundError:
            error = f"Could not get open license definitions from local file {license_path}."
            logger.error(error)
            raise ZenodoMetadataException(error)

    def validate_license(self):
        """Method to verify the status of the metadata license."""

        if not (self.access_right in ['open', 'embargoed']):
            logger.info('No need to check license for Zenodo upload.')
            self.license_valid = True
        else:
            metadata_license = self.license.upper()

            logger.info(f'Specified license type is: {self.license}')
            logger.info(f'access_right: "{self.access_right}"')

            for lic in self.open_licenses.keys():
                if lic.startswith(metadata_license):
                    logger.info(f'license: "{lic}" validated.')
                    self.license_valid = True
                    break
