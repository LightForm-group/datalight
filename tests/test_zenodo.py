import os
import pytest
import configparser

from .conftest import Zenodo, ZenodoException

# Path where the tests are
_dir = os.path.dirname(os.path.realpath(__file__))

# Path where the data files are located
_dir_data = os.path.join(_dir, 'data')
_dir_metadata = os.path.join(_dir, 'metadata')


# Tokenfile use to connect to zenodo, it is located in the main directory
# of the project.
tokenfile = os.path.join(_dir, '..', '.zenodo')

# Using a ini file
zenoconfig = configparser.ConfigParser()
zenoconfig.read(tokenfile)

metadata_file = 'minimum_valid.yml'
metadata = os.path.join(_dir_metadata, metadata_file)

SANDBOX = True
if SANDBOX:
    token = zenoconfig['sandbox.zenodo.org']['lightForm']
else:
    token = zenoconfig['zenodo.org']['lightForm']


@pytest.fixture(params=[token, None])
def zeno(request):
    zeno = Zenodo(token=request.param, metadata=metadata,
                  sandbox=SANDBOX)

    # zeno.metadata = {'metadata': {
    #     'title': 'My first upload',
    #     'upload_type': 'dataset',
    #     'description': 'This is my first upload',
    #     'creators': [{'name': 'Doe, John',
    #                   'affiliation': 'Zenodo'}]
    # }}

    # metadata_file = 'minimum_valid.yml'
    # with open(os.path.join(_dir_metadata, metadata_file),
    #           encoding="utf-8") as f:
    #     try:
    #         from ruamel.yaml import YAML
    #         zeno.metadata = {'metadata': YAML(typ="safe", pure=True).load(f)}
    #     except ImportError:
    #         import yaml
    #         zeno.metadata = {'metadata': yaml.load(f)}

    def fin():
        print('teardown zeno')
        zeno.token = None
    request.addfinalizer(fin)

    return zeno


class TestZenodo(object):

    def test_status_code_500(self, zeno):
        with pytest.raises(ZenodoException):
            zeno._check_status_code(500)

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

    def test_get_deposition_id_and_delete(self):
        zeno = Zenodo(token=token, metadata=metadata,
                      sandbox=SANDBOX)
        if zeno.token is not None:
            zeno.get_deposition_id()
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

    def test_upload_files_id_int(self, zeno):
        filenames = 'test.csv'
        if zeno.token is not None:
            zeno.get_deposition_id()
            zeno.upload_files(filenames, path=_dir_data, _id=zeno.deposition_id)
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

    def test_upload_metadata_one_file(self, zeno):
        filenames = 'test.csv'
        if zeno.token is not None:
            zeno.get_deposition_id()
            zeno.upload_files(filenames, path=_dir_data)
            zeno.upload_metadata()

            if zeno.status_code >= 500:
                print('Test was not able to work because of '
                      'error {} on the server'.format(zeno.status_code))
            else:
                assert type(zeno.status_code) is int
            zeno.delete()
        else:
            with pytest.raises(ZenodoException):
                zeno.upload_files(filenames)

    def test_upload_metadata_id_int(self, zeno):
        filenames = 'test.csv'
        if zeno.token is not None:
            zeno.get_deposition_id()
            zeno.upload_files(filenames, path=_dir_data)
            zeno.upload_metadata(_id=zeno.deposition_id)

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

            zeno.upload_metadata()

            if zeno.status_code >= 500:
                print('Test was not able to work because of '
                      'error {} on the server'.format(zeno.status_code))
            else:
                assert type(zeno.status_code) is int
            zeno.delete()
        else:
            with pytest.raises(ZenodoException):
                zeno.upload_files(filenames)

    def test_download_file(self, zeno):

        with pytest.raises(ZenodoException):
            zeno.download_files()
         # raise "Not implemented"

    def test_set_metadata(self, zeno):
        assert 'metadata' in zeno.set_metadata()

    ## Commented to not publish too many files on the sandbox
    ## if needed to be tested again remove comments

    # def test_publish(self, zeno):
    #     filenames = 'test.csv'
    #     if zeno.token is not None:
    #         zeno.get_deposition_id()
    #         zeno.upload_files(filenames, path=_dir_data)
    #         zeno.upload_metadata(metadata=zeno.metadata)
    #         zeno.publish()
    #         if zeno.status_code >= 500:
    #             print('Test was not able to work because of '
    #                   'error {} on the server'.format(zeno.status_code))
    #
    #         else:
    #             assert type(zeno.status_code) is int
    #
    #     else:
    #         with pytest.raises(ZenodoException):
    #             zeno.publish()



def test_Zenodo_zenodo_api():
    zeno = Zenodo(token=token, sandbox=False)
    assert zeno.api_baseurl == 'https://zenodo.org/api/'
