import os
import pytest

from datalight.common import get_authentication_token
from datalight.zenodo import Zenodo, ZenodoException

# Path where the tests are
_dir = os.path.dirname(os.path.realpath(__file__))

# Path where the data files are located
_dir_data = os.path.join(_dir, 'data')
_dir_metadata = os.path.join(_dir, 'metadata')

# Path to metadata example
metadata_file = 'minimum_valid.yml'
metadata = os.path.join(_dir_metadata, metadata_file)


@pytest.fixture()
def zeno():
    # Read Zenodo API token from file
    token = get_authentication_token(sandbox=True)
    if token is None:
        pytest.skip("Unable to read API token from file. Skipping API tests.")

    return Zenodo(token=token, metadata_path=metadata, sandbox=True)


class TestZenodo(object):
    @staticmethod
    def test_status_code_500(zeno):
        with pytest.raises(ZenodoException):
            zeno._check_status_code(500)

    @staticmethod
    def test_status_code_400(zeno):
        with pytest.raises(ZenodoException):
            zeno._check_status_code(400)

    @staticmethod
    def test_status_code_200(zeno):
        assert zeno._check_status_code(200) == 200

    @staticmethod
    def test_connection_token(zeno):
        zeno._try_connection()
        assert zeno.status_code == 200

    @staticmethod
    def test_connection_wrong_url(zeno):
        zeno.token = 1234
        with pytest.raises(ZenodoException):
            zeno._try_connection()

    @staticmethod
    def test_delete_bad_token(zeno):
        with pytest.raises(ZenodoException):
            zeno.delete(1234)

    @staticmethod
    def test_delete_wrong_url_or_bad_token(zeno):
        zeno.depositions_url = 'https://zenodo.org/'
        with pytest.raises(ZenodoException):
            zeno.delete(1234)

    @staticmethod
    def test_get_deposition_error_400(zeno):
        zeno.depositions_url = 'https://zenodo.org/'
        with pytest.raises(ZenodoException):
            zeno._get_deposition_id()

    @staticmethod
    def test_get_deposition_id_and_delete(zeno):
        zeno._get_deposition_id()
        assert type(zeno.deposition_id) is int

        # Remove the record created for the test
        zeno.delete()

    def test_upload_no_deposition_id(self, zeno):
        filename = 'test.csv'

        if zeno.deposition_id is None:
            zeno._get_deposition_id()

        zeno._upload_files(filename, path=_dir_data)
        if zeno.status_code >= 500:
            self.print_server_error(zeno)
        else:
            assert type(zeno.status_code) is int

        # Remove the record created for the test
        zeno.delete()

    def test_upload_files_one_file(self, zeno):
        filenames = 'test.csv'
        zeno._get_deposition_id()
        zeno._upload_files(filenames, path=_dir_data)
        if zeno.status_code >= 500:
            self.print_server_error(zeno)
        else:
            assert type(zeno.status_code) is int

        # Remove the record created for the test
        zeno.delete()

    def test_upload_files_multiple_files(self, zeno):
        filenames = ['test.csv', 'test2.csv']

        zeno._get_deposition_id()
        zeno._upload_files(filenames, path=_dir_data)
        if zeno.status_code >= 500:
            self.print_server_error(zeno)
        else:
            assert type(zeno.status_code) is int

        # Remove the record created for the test
        zeno.delete()

    def test_upload_files_id_int(self, zeno):
        filenames = 'test.csv'

        zeno._get_deposition_id()
        zeno._upload_files(filenames, path=_dir_data)
        if zeno.status_code >= 500:
            self.print_server_error(zeno)
        else:
            assert type(zeno.status_code) is int

        # Remove the record created for the test
        zeno.delete()

    def test_upload_metadata_one_file(self, zeno):
        filenames = 'test.csv'

        zeno._get_deposition_id()
        zeno._upload_files(filenames, path=_dir_data)
        zeno.set_metadata()
        zeno.upload_metadata()

        if zeno.status_code >= 500:
            self.print_server_error(zeno)
        else:
            assert type(zeno.status_code) is int
        zeno.delete()

    def test_upload_metadata_multiple_file(self, zeno):
        filenames = ['test.csv', 'test2.csv']

        zeno._get_deposition_id()
        zeno._upload_files(filenames, path=_dir_data)
        zeno.set_metadata()
        zeno.upload_metadata()

        if zeno.status_code >= 500:
            self.print_server_error(zeno)
        else:
            assert type(zeno.status_code) is int
        zeno.delete()

    @staticmethod
    def print_server_error(zeno):
        print('Test failed due to server error {}.'.format(zeno.status_code))

    @staticmethod
    def test_set_metadata(zeno):
        zeno.set_metadata()
        assert 'metadata' in zeno.checked_metadata


def test_zenodo_api():
    """All of the above tests access the Zenodo sandbox while this test accesses the real Zenodo API."""
    token = get_authentication_token(sandbox=False)
    if token is None:
        pytest.skip("Unable to read API token from file. Skipping API tests.")
    zeno = Zenodo(token=token, metadata_path=metadata, sandbox=False)
    assert zeno.api_base_url == 'https://zenodo.org/api/'
