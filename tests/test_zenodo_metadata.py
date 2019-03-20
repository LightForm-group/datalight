"""Tests for zenodo_metadata.py"""

import pathlib
import pytest
import yaml

from datalight.zenodo import ZenodoMetadata
from datalight.zenodo_metadata import ZenodoMetadataException

# Path where the tests are located
test_directory = pathlib.Path(__file__).parent

# Path where schema and sample metadata files are located
schema_path = test_directory.parent / pathlib.Path(
    "datalight/schemas/zenodo/zenodo_upload_metadata_schema.json5")
metadata_path = test_directory / pathlib.Path('metadata/minimum_valid.yml')

with open(schema_path) as f:
    schema_dictionary = yaml.load(f)

with open(metadata_path) as f:
    metadata_dictionary = yaml.load(f)


# Test setting up a Metadata object with both a path to a schema file or the schema
# directly as a dictionary.
@pytest.fixture(params=[schema_path, schema_dictionary])
def zeno_meta(request):
    """Set up a Metadata instance to pass to later tests"""
    return ZenodoMetadata(metadata_path=metadata_dictionary, schema=request.param)


def test_init_schema_yaml():
    """Verify that schema can be read from a dictionary"""
    ZenodoMetadata(metadata_path=metadata_dictionary, schema=schema_dictionary)


def test_init_schema_file():
    """Verify that schema can be read from a file"""
    ZenodoMetadata(metadata_path=metadata_dictionary, schema=schema_path)


def test_init_schema_not_present():
    """Verify that method raises an error if schema file not present"""
    with pytest.raises(ZenodoMetadataException):
        ZenodoMetadata(metadata_path=metadata_dictionary, schema='not_present')


def test_init_schema_not_correct_type():
    """test to verify that method raise an error if schema file not present"""
    with pytest.raises(ZenodoMetadataException):
        ZenodoMetadata(metadata_path=metadata_dictionary, schema=1)


def test_init_schema_is_none():
    """test to verify that method raise an error if schema file not present"""
    with pytest.raises(ZenodoMetadataException):
        ZenodoMetadata(metadata_path=metadata_dictionary, schema=None)


def test_set_schema_wrong_schema(zeno_meta):
    with pytest.raises(ZenodoMetadataException):
        zeno_meta.set_schema(schema=None)


def test_set_schema_modifying_schema_from_file(zeno_meta):
    zeno_meta.set_schema(schema=schema_path)


def test_set_schema_modifying_schema_from_dictionary(zeno_meta):
    zeno_meta.set_schema(schema=schema_dictionary)


def test_set_schema_modifying_schema_failed(zeno_meta):
    with pytest.raises(ZenodoMetadataException):
        zeno_meta.set_schema(schema=1)


def test_set_metadata_modifying_metadata_none(zeno_meta):
    zeno_meta.set_metadata(metadata_path=metadata_dictionary)


def test_set_metadata_modifying_from_dictionary(zeno_meta):
    zeno_meta.set_metadata({})


def test_set_metadata_modifying_from_file(zeno_meta):
    zeno_meta.set_metadata(metadata_path / metadata_path)


def test_set_metadata_is_none(zeno_meta):
    with pytest.raises(ZenodoMetadataException):
        zeno_meta.set_metadata(None)


def test__read_metadata_from_file(zeno_meta):
    assert metadata_dictionary == zeno_meta._read_metadata(metadata_path / metadata_path)


def test__read_metadata_from_bad_file(zeno_meta):
    with pytest.raises(ZenodoMetadataException):
        zeno_meta._read_metadata('no file')


def test__check_minimal_ok(zeno_meta):
    assert zeno_meta._check_minimal()


def test__check_minimal_missing_title(zeno_meta):
    tmp = metadata_dictionary.copy()
    del tmp['title']
    zeno_meta._metadata = tmp
    with pytest.raises(ZenodoMetadataException):
        zeno_meta._check_minimal()


def test__remove_extra_properties(zeno_meta):
    tmp = metadata_dictionary.copy()
    tmp['addkey'] = '122'
    zeno_meta._metadata = tmp
    zeno_meta._remove_extra_properties()
    assert 'addkey' not in zeno_meta._metadata


def test_verify_metadata_ok(zeno_meta):
    zeno_meta.validate()


@pytest.fixture(params=['open', 'embargoed'])
def zeno_access(request):
    _metadata = metadata_dictionary.copy()
    _metadata.update({'access_right': request.param})
    zeno_access = ZenodoMetadata(metadata_path=_metadata, schema=schema_path)
    return zeno_access


def test__check_license_availability_ccby4(zeno_access):
    zeno_access.set_metadata({'license': 'cc-by-4.0'})
    assert zeno_access._check_license_availability()


def test__check_license_availability_failed(zeno_access):
    zeno_access.set_metadata({'license': 'not a valid license'})
    with pytest.raises(ZenodoMetadataException):
        zeno_access._check_license_availability()


def test__check_license_availability_no_access_right():
    tmp = metadata_dictionary.copy()
    tmp.update({'license': 'cc-by-4.0'})
    zeno = ZenodoMetadata(metadata_path=tmp, schema=schema_path)
    assert zeno._check_license_availability()


def test__check_license_availability_default(zeno_access):
    zeno_access._check_minimal()
    assert zeno_access._check_license_availability()


def test__check_license_availability_access_right_not_in_open_embargoed():
    _metadata = metadata_dictionary.copy()
    _metadata.update({'access_right': 'closed'})
    zeno = ZenodoMetadata(metadata_path=_metadata, schema=schema_path)
    assert zeno._check_license_availability()


def test__check_license_availability_licenses_files_provided(zeno_access):
    zeno_access.set_metadata({'license': 'cc-by-4.0'})
    open_licence_path = metadata_path.parent / pathlib.Path('opendefinition-licenses.json')
    assert zeno_access._check_license_availability(open_licence_path)


# use it with internet connection or find a way to mimic it...
def test__check_license_availability_from_opendefinition(zeno_access):
    zeno_access.set_metadata({'license': 'cc-by-4.0'})
    assert zeno_access._check_license_availability(opendefinition=True)
