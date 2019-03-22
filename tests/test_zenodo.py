"""Test for functions in Zenodo.py."""

import os
import pytest

from datalight.common import get_authentication_token
from datalight.zenodo import Zenodo, ZenodoException

# Path where the tests are
test_directory = os.path.dirname(os.path.realpath(__file__))

# Path where the data files are located
data_directory = os.path.join(test_directory, 'data')
metadata_directory = os.path.join(test_directory, 'metadata')

# Path to metadata example
metadata_file = 'minimum_valid.yml'
metadata = os.path.join(metadata_directory, metadata_file)


@pytest.fixture()
def zeno():
    """Set up for the API related tests by trying to read an API token and
    instantiating a Zenodo object.
    """

    token = get_authentication_token(sandbox=True)
    if token is None:
        pytest.skip("Unable to read API token from file. Skipping API tests.")

    return Zenodo(token=token, metadata_path=metadata, sandbox=True)


class TestZenodo:
    """Tests for methods of the Zenodo object."""
    @staticmethod
    def test_status_code_500(zeno):
        """Status 500 represents a server error."""
        with pytest.raises(ZenodoException):
            zeno._check_status_code(500)

    @staticmethod
    def test_status_code_400(zeno):
        """400 errors are the response to malformed requests."""
        with pytest.raises(ZenodoException):
            zeno._check_status_code(400)

    @staticmethod
    def test_status_code_200(zeno):
        """200 errors represent success."""
        assert zeno._check_status_code(200) == 200

    @staticmethod
    def test_connection_token(zeno):
        """Try and connect to the API"""
        zeno._try_connection()
        assert zeno.status_code == 200

    @staticmethod
    def test_connection_wrong_url(zeno):
        """Trying to connect to anything bu the API should raise an exception."""
        zeno.token = 1234
        with pytest.raises(ZenodoException):
            zeno._try_connection()

    @staticmethod
    def test_delete_bad_id(zeno):
        """"Deleting a record that doesnt exist should raise an exception."""
        with pytest.raises(ZenodoException):
            zeno.delete(1234)

    @staticmethod
    def test_delete_wrong_url_or_bad_token(zeno):
        """Deleting a record with an incorrect address should raise an exception."""
        zeno.depositions_url = 'https://zenodo.org/'
        with pytest.raises(ZenodoException):
            zeno.delete(1234)

    @staticmethod
    def test_get_deposition_error_400(zeno):
        """Depositing a record with an incorrect address should raise an exception."""
        zeno.depositions_url = 'https://zenodo.org/'
        with pytest.raises(ZenodoException):
            zeno._get_deposition_id()

    @staticmethod
    def test_get_deposition_id_and_delete(zeno):
        """Get a valid deposition id."""
        zeno._get_deposition_id()
        assert isinstance(zeno.deposition_id, int)

        # Remove the record created for the test
        zeno.delete()

    def test_upload_files_one_file(self, zeno):
        """Try and upload a single valid file."""
        filenames = 'test.csv'
        zeno._get_deposition_id()
        zeno._upload_files(filenames, path=data_directory)
        if zeno.status_code >= 500:
            self.print_server_error(zeno)
        else:
            assert isinstance(zeno.status_code, int)

        # Remove the record created for the test
        zeno.delete()

    def test_upload_files_multiple_files(self, zeno):
        """Try and upload multiple valid files."""
        filenames = ['test.csv', 'test2.csv']

        zeno._get_deposition_id()
        zeno._upload_files(filenames, path=data_directory)
        if zeno.status_code >= 500:
            self.print_server_error(zeno)
        else:
            assert isinstance(zeno.status_code, int)

        # Remove the record created for the test
        zeno.delete()

    def test_upload_metadata_one_file(self, zeno):
        """Upload a file and its metadata."""
        filenames = 'test.csv'

        zeno._get_deposition_id()
        zeno._upload_files(filenames, path=data_directory)
        zeno.set_metadata()
        zeno.upload_metadata()

        if zeno.status_code >= 500:
            self.print_server_error(zeno)
        else:
            assert isinstance(zeno.status_code, int)
        zeno.delete()

    def test_upload_metadata_multiple_file(self, zeno):
        """Upload multiple files and their metadata."""
        filenames = ['test.csv', 'test2.csv']

        zeno._get_deposition_id()
        zeno._upload_files(filenames, path=data_directory)
        zeno.set_metadata()
        zeno.upload_metadata()

        if zeno.status_code >= 500:
            self.print_server_error(zeno)
        else:
            assert isinstance(zeno.status_code, int)
        zeno.delete()

    @staticmethod
    def print_server_error(zeno):
        """An error for when requests return a 500 status code."""
        print('Test failed due to server error {}.'.format(zeno.status_code))

    @staticmethod
    def test_set_metadata(zeno):
        """Test setting metadata for a record."""
        zeno.set_metadata()
        assert 'metadata' in zeno.checked_metadata


def test_zenodo_api():
    """All of the above tests access the Zenodo
    sandbox while this test tests a connection to the real Zenodo API.
    """
    token = get_authentication_token(sandbox=False)
    if token is None:
        pytest.skip("Unable to read API token from file. Skipping API tests.")
    zeno = Zenodo(token=token, metadata_path=metadata, sandbox=False)
    assert zeno.api_base_url == 'https://zenodo.org/api/'
