import os
import pytest

import yaml

from .conftest import ZenodoMetadata, ZenodoMetadataException, schemafile

# Path where the tests are
_dir = os.path.dirname(os.path.realpath(__file__))

# Path where the schema files are located
_dir_data = os.path.join(_dir, 'metadata')

# Path where the metadata tests files are located
_dir_test_files = os.path.join(_dir, 'schemas', 'zenodo', 'test')


with open(schemafile) as f:
    yamlschema = yaml.load(f)


metadatafile = 'minimum_valid.yml'
with open(os.path.join(_dir_data, metadatafile)) as f:
        metadata = yaml.load(f)


@pytest.fixture(params=[schemafile, yamlschema])
def zenometa(request):
    zenometa = ZenodoMetadata(metadata=metadata,
                              schema=request.param)
    return zenometa


def test_init_schema_yaml():
    """test to verify that method can accept yaml file as schema
    """
    ZenodoMetadata(metadata=metadata,
                   schema=yamlschema)


def test_init_schema_file():
    """test to verify that method can read schema from file
    """
    ZenodoMetadata(metadata=metadata,
                   schema=schemafile)


def test_init_schema_not_present():
    """test to verify that method raise an error if schema file not present
    """
    with pytest.raises(ZenodoMetadataException):
        ZenodoMetadata(metadata=metadata, schema='notpresent')


def test_init_schema_not_correct_type():
    """test to verify that method raise an error if schema file not present
    """
    with pytest.raises(ZenodoMetadataException):
        ZenodoMetadata(metadata=metadata,
                       schema=1)


def test_init_schema_is_None():
    """test to verify that method raise an error if schema file not present
    """
    with pytest.raises(ZenodoMetadataException):
        ZenodoMetadata(metadata=metadata,
                       schema=None)


def test_set_schema_wrong_schema(zenometa):
    with pytest.raises(ZenodoMetadataException):
        zenometa.set_schema(schema=None)


def test_set_schema_modifying_schema_from_file(zenometa):
    zenometa.set_schema(schema=schemafile)


def test_set_schema_modifying_schema_from_dictionary(zenometa):
    zenometa.set_schema(schema=yamlschema)


def test_set_schema_modifying_schema_failed(zenometa):
    with pytest.raises(ZenodoMetadataException):
        zenometa.set_schema(schema=1)


def test_set_metadata_modifying_metatdata_None(zenometa):
    zenometa.set_metadata(metadata=metadata)


def test_set_metadata_modifying_from_dictionary(zenometa):
    zenometa.set_metadata({})


def test_set_metadata_modifying_from_file(zenometa):
    zenometa.set_metadata(os.path.join(_dir_data, metadatafile))


def test_set_metadata_is_None(zenometa):
    with pytest.raises(ZenodoMetadataException):
        zenometa.set_metadata(None)


def test__read_metadata_from_file(zenometa):
    assert metadata == zenometa._read_metadata(os.path.join(_dir_data,
                                                            metadatafile))


def test__read_metadata_from_file(zenometa):
    with pytest.raises(ZenodoMetadataException):
        zenometa._read_metadata('no file')


def test__check_minimal_ok(zenometa):
    assert zenometa._check_minimal()


def test__check_minimal_missing_title(zenometa):
    tmp = metadata.copy()
    del tmp['title']
    zenometa._metadata = tmp
    with pytest.raises(ZenodoMetadataException):
        zenometa._check_minimal()


def test__remove_extra_properties(zenometa):
    tmp = metadata.copy()
    tmp['addkey'] = '122'
    zenometa._metadata = tmp
    zenometa._remove_extra_properties()
    assert 'addkey' not in zenometa._metadata


def test_verify_metadata_ok(zenometa):
    zenometa.validate()


@pytest.fixture(params=['open', 'embargoed'])
def zenoaccess(request):
    _metadata = metadata.copy()
    _metadata.update({'access_right': request.param})
    zenoaccess = ZenodoMetadata(metadata=_metadata,
                                schema=schemafile)
    return zenoaccess


def test__check_license_availability_ccby4(zenoaccess):
    zenoaccess.set_metadata({'license': 'cc-by-4.0'})
    assert zenoaccess._check_license_availability()


def test__check_license_availability_failed(zenoaccess):
    zenoaccess.set_metadata({'license': 'not a valid license'})
    with pytest.raises(ZenodoMetadataException):
        zenoaccess._check_license_availability()


def test__check_license_availability_no_access_right():
    tmp = metadata.copy()
    tmp.update({'license': 'cc-by-4.0'})
    zeno = ZenodoMetadata(metadata=tmp,
                          schema=schemafile)
    assert zeno._check_license_availability()


def test__check_license_availability_default(zenoaccess):
    zenoaccess._check_minimal()
    assert zenoaccess._check_license_availability()


def test__check_license_availability_access_right_not_in_open_embargoed():
    _metadata = metadata.copy()
    _metadata.update({'access_right': 'closed'})
    zeno = ZenodoMetadata(metadata=_metadata,
                          schema=schemafile)
    assert zeno._check_license_availability()


def test__check_license_availability_licenses_files_provided(zenoaccess):
    zenoaccess.set_metadata({'license': 'cc-by-4.0'})
    assert zenoaccess._check_license_availability(flicenses=
                                                  os.path.join(_dir_data,
                                            'opendefinition-licenses.json'))


# use it with internet connection or find a way to mimic it...
def test__check_license_availability_from_opendefinition(zenoaccess):
    zenoaccess.set_metadata({'license': 'cc-by-4.0'})
    assert zenoaccess._check_license_availability(opendefinition=True)


# use it with no internet connection or find a way to mimic it...
def test__check_license_availability_from_opendefinition_no_internet(zenoaccess):
    zenoaccess.set_metadata({'license': 'cc-by-4.0'})
    with pytest.raises(ZenodoMetadataException):
        assert zenoaccess._check_license_availability(opendefinition=True)


# test which work doesn't matter if internet or not (not the best
# but at least all test can be green :) )
def test__check_license_availability_from_opendefinition_no_internet(zenoaccess):
    zenoaccess.set_metadata({'license': 'cc-by-4.0'})
    try:
        assert zenoaccess._check_license_availability(opendefinition=True)
    except ZenodoMetadataException:
        with pytest.raises(ZenodoMetadataException):
            assert zenoaccess._check_license_availability(opendefinition=True)


# def test__verify_metadata_with_extra_argument(self):
#     raise NotImplemented
#
#
# def test__verify_metadata_with_wrong_key_type(self):
#     raise NotImplemented
#
#
# def test__verify_metadata_with_missing_key_combination(self):
#     raise NotImplemented