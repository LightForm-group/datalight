import os
import pytest
import configparser

from .conftest import Zenodo, ZenodoException

# Path where the tests are
_dir = os.path.dirname(os.path.realpath(__file__))

# Path where the data files are located
_dir_data = os.path.join(_dir, 'data')

# Tokenfile use to connect to zenodo, it is located in the main directory
# of the project.
tokenfile = os.path.join(_dir, '..', '.zenodo')

# Using a ini file
zenoconfig = configparser.ConfigParser()
zenoconfig.read(tokenfile)

SANDBOX = False
if SANDBOX:
    token = zenoconfig['sandbox.zenodo.org']['lightForm']
else:
    token = zenoconfig['zenodo.org']['lightForm']


@pytest.fixture(params=[token, None])
def zeno(request):
    zeno = Zenodo(token=request.param, sandbox=SANDBOX)

    # zeno.metadata = {'metadata': {
    #     'title': 'My first upload',
    #     'upload_type': 'dataset',
    #     'description': 'This is my first upload',
    #     'creators': [{'name': 'Doe, John',
    #                   'affiliation': 'Zenodo'}]
    # }}

    with open(_dir_data + '/lightform.yml', encoding="utf-8") as f:
        try:
            from ruamel.yaml import YAML
            zeno.metadata = {'metadata': YAML(typ="safe", pure=True).load(f)}
        except ImportError:
            import yaml
            zeno.metadata = {'metadata': yaml.load(f)}

    def fin():
        print('teardown zeno')
        zeno.token = None
    request.addfinalizer(fin)

    return zeno


class TestZenodo(object):

    def test_status_code_500(self, zeno):
        assert zeno._check_status_code(500) == 500

    def test_status_code_400(self, zeno):
        with pytest.raises(ZenodoException):
            zeno._check_status_code(400)

    def test_status_code_200(self, zeno):
        assert zeno._check_status_code(200) == 200

    def test_connection_token(self, zeno):
        if zeno.token is not None:
            zeno.connection()
            assert zeno.status_code == 200
        else:
            with pytest.raises(ZenodoException):
                zeno.connection()

    def test_connection_wrong_url(self, zeno):
        zeno.token = 1234
        with pytest.raises(ZenodoException):
            zeno.connection()

    def test_delete_bad_token(self, zeno):
        with pytest.raises(ZenodoException):
            zeno.delete(1234)

    def test_delete_wrong_url_or_bad_token(self, zeno):
        zeno.depositions_url = 'https://zenodo.org/'
        with pytest.raises(ZenodoException):
            zeno.delete(1234)

    def test_get_deposition_error_400(self, zeno):
        zeno.depositions_url = 'https://zenodo.org/'
        with pytest.raises(ZenodoException):
            zeno.get_deposition_id()

    def test_get_deposition_id_and_delete(self, zeno):
        if zeno.token is not None:
            z = zeno.get_deposition_id()
            assert type(zeno.deposition_id) is int

            # Remove the record create for the test
            zeno.delete()
        else:
            with pytest.raises(ZenodoException):
                zeno.get_deposition_id()

    def test_upload_no_deposition_id(self, zeno):
        filename = 'test.csv'
        if zeno.token is not None:
            if zeno.deposition_id is None:
                zeno.get_deposition_id()

            zeno.upload_files(filename, path=_dir_data)
            if zeno.status_code >= 500:
                print('Test was not able to work because of '
                      'error {} on the server'.format(zeno.status_code))
            else:
                assert type(zeno.status_code) is int

            # Remove the record create for the test
            zeno.delete()
        else:
            with pytest.raises(ZenodoException):
                zeno.upload_files(filename)

    def test_upload_files_one_file(self, zeno):
        filenames = 'test.csv'
        if zeno.token is not None:
            zeno.get_deposition_id()
            zeno.upload_files(filenames, path=_dir_data)
            if zeno.status_code >= 500:
                print('Test was not able to work because of '
                      'error {} on the server'.format(zeno.status_code))
            else:
                assert type(zeno.status_code) is int

            # Remove the record create for the test
            zeno.delete()
        else:
            with pytest.raises(ZenodoException):
                zeno.upload_files(filenames, path=_dir_data)

    def test_upload_files_multiple_files(self, zeno):
        filenames = ['test.csv', 'test2.csv']
        if zeno.token is not None:
            zeno.get_deposition_id()
            zeno.upload_files(filenames, path=_dir_data)
            if zeno.status_code >= 500:
                print('Test was not able to work because of '
                      'error {} on the server'.format(zeno.status_code))
            else:
                assert type(zeno.status_code) is int

            # Remove the record create for the test
            zeno.delete()
        else:
            with pytest.raises(ZenodoException):
                zeno.upload_files(filenames)

    def test_upload_metadata_one_file(self, zeno):
        filenames = 'test.csv'
        if zeno.token is not None:
            zeno.get_deposition_id()
            zeno.upload_files(filenames, path=_dir_data)

            zeno.upload_metadata(metadata=zeno.metadata)

            if zeno.status_code >= 500:
                print('Test was not able to work because of '
                      'error {} on the server'.format(zeno.status_code))
            else:
                assert type(zeno.status_code) is int
            zeno.delete()
        else:
            with pytest.raises(ZenodoException):
                zeno.upload_files(filenames)

    def test_upload_metadata_multiple_file(self, zeno):
        filenames = ['test.csv', 'test2.csv']

        if zeno.token is not None:
            zeno.get_deposition_id()
            zeno.upload_files(filenames, path=_dir_data)

            zeno.upload_metadata(metadata=zeno.metadata)

            if zeno.status_code >= 500:
                print('Test was not able to work because of '
                      'error {} on the server'.format(zeno.status_code))
            else:
                assert type(zeno.status_code) is int
            zeno.delete()
        else:
            with pytest.raises(ZenodoException):
                zeno.upload_files(filenames)

    def test_upload_metadata_nodict(self, zeno):
        filenames = 'test.csv'
        if zeno.token is not None:
            zeno.get_deposition_id()
            zeno.upload_files(filenames, path=_dir_data)

            with pytest.raises(ZenodoException):
                zeno.upload_metadata(metadata=[])

            if zeno.status_code >= 500:
                print('Test was not able to work because of '
                      'error {} on the server'.format(zeno.status_code))
            else:
                assert type(zeno.status_code) is int
            zeno.delete()
        else:
            with pytest.raises(ZenodoException):
                zeno.upload_files(filenames)

    # def test_publish(self):
    #     # Need to understand how to do a mock to be able to test it.
    #     raise "Not implemented"

    # def test_download_file():
    #     raise "Not implemented"
