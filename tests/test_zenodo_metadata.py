"""Tests for zenodo_metadata.py"""

import os
import pathlib
import pytest
import yaml

from datalight.zenodo import ZenodoMetadata
from datalight.zenodo_metadata import ZenodoMetadataException

# Path where the tests are
test_directory = pathlib.Path(__file__).parent

# Path where the schema files are located
test_metadata = test_directory / pathlib.Path('metadata')


schema_file = test_directory.parent / pathlib.Path("datalight/schemas/zenodo/record-1.0.0.yml")
with open(schema_file) as f:
    yaml_schema = yaml.load(f)


metadata_file = pathlib.Path('minimum_valid.yml')
with open(test_metadata / metadata_file) as f:
    metadata = yaml.load(f)


@pytest.fixture(params=[schema_file, yaml_schema])
def zeno_meta(request):
    return ZenodoMetadata(metadata=metadata, schema=request.param)


def test_init_schema_yaml():
    """test to verify that method can accept yaml file as schema"""
    ZenodoMetadata(metadata=metadata, schema=yaml_schema)


def test_init_schema_file():
    """test to verify that method can read schema from file"""
    ZenodoMetadata(metadata=metadata, schema=schema_file)


def test_init_schema_not_present():
    """test to verify that method raise an error if schema file not present"""
    with pytest.raises(ZenodoMetadataException):
        ZenodoMetadata(metadata=metadata, schema='not_present')


def test_init_schema_not_correct_type():
    """test to verify that method raise an error if schema file not present"""
    with pytest.raises(ZenodoMetadataException):
        ZenodoMetadata(metadata=metadata, schema=1)


def test_init_schema_is_none():
    """test to verify that method raise an error if schema file not present"""
    with pytest.raises(ZenodoMetadataException):
        ZenodoMetadata(metadata=metadata, schema=None)


def test_set_schema_wrong_schema(zeno_meta):
    with pytest.raises(ZenodoMetadataException):
        zeno_meta.set_schema(schema=None)


def test_set_schema_modifying_schema_from_file(zeno_meta):
    zeno_meta.set_schema(schema=schema_file)


def test_set_schema_modifying_schema_from_dictionary(zeno_meta):
    zeno_meta.set_schema(schema=yaml_schema)


def test_set_schema_modifying_schema_failed(zeno_meta):
    with pytest.raises(ZenodoMetadataException):
        zeno_meta.set_schema(schema=1)


def test_set_metadata_modifying_metadata_none(zeno_meta):
    zeno_meta.set_metadata(metadata=metadata)


def test_set_metadata_modifying_from_dictionary(zeno_meta):
    zeno_meta.set_metadata({})


def test_set_metadata_modifying_from_file(zeno_meta):
    zeno_meta.set_metadata(test_metadata / metadata_file)


def test_set_metadata_is_none(zeno_meta):
    with pytest.raises(ZenodoMetadataException):
        zeno_meta.set_metadata(None)


def test__read_metadata_from_file(zeno_meta):
    assert metadata == zeno_meta._read_metadata(test_metadata / metadata_file)


def test__read_metadata_from_bad_file(zeno_meta):
    with pytest.raises(ZenodoMetadataException):
        zeno_meta._read_metadata('no file')


def test__check_minimal_ok(zeno_meta):
    assert zeno_meta._check_minimal()


def test__check_minimal_missing_title(zeno_meta):
    tmp = metadata.copy()
    del tmp['title']
    zeno_meta._metadata = tmp
    with pytest.raises(ZenodoMetadataException):
        zeno_meta._check_minimal()


def test__remove_extra_properties(zeno_meta):
    tmp = metadata.copy()
    tmp['addkey'] = '122'
    zeno_meta._metadata = tmp
    zeno_meta._remove_extra_properties()
    assert 'addkey' not in zeno_meta._metadata


def test_verify_metadata_ok(zeno_meta):
    zeno_meta.validate()


@pytest.fixture(params=['open', 'embargoed'])
def zeno_access(request):
    _metadata = metadata.copy()
    _metadata.update({'access_right': request.param})
    zeno_access = ZenodoMetadata(metadata=_metadata, schema=schema_file)
    return zeno_access


def test__check_license_availability_ccby4(zeno_access):
    zeno_access.set_metadata({'license': 'cc-by-4.0'})
    assert zeno_access._check_license_availability()


def test__check_license_availability_failed(zeno_access):
    zeno_access.set_metadata({'license': 'not a valid license'})
    with pytest.raises(ZenodoMetadataException):
        zeno_access._check_license_availability()


def test__check_license_availability_no_access_right():
    tmp = metadata.copy()
    tmp.update({'license': 'cc-by-4.0'})
    zeno = ZenodoMetadata(metadata=tmp, schema=schema_file)
    assert zeno._check_license_availability()


def test__check_license_availability_default(zeno_access):
    zeno_access._check_minimal()
    assert zeno_access._check_license_availability()


def test__check_license_availability_access_right_not_in_open_embargoed():
    _metadata = metadata.copy()
    _metadata.update({'access_right': 'closed'})
    zeno = ZenodoMetadata(metadata=_metadata, schema=schema_file)
    assert zeno._check_license_availability()


def test__check_license_availability_licenses_files_provided(zeno_access):
    zeno_access.set_metadata({'license': 'cc-by-4.0'})
    assert zeno_access._check_license_availability(flicenses=os.path.join(
        test_metadata, 'opendefinition-licenses.json'))


# use it with internet connection or find a way to mimic it...
def test__check_license_availability_from_opendefinition(zeno_access):
    zeno_access.set_metadata({'license': 'cc-by-4.0'})
    assert zeno_access._check_license_availability(opendefinition=True)
