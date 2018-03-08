import os
import sys
import pytest

from .conftest import Zenodo, ZenodoException

# Read the token file (if present)
if os.path.isfile('../.zenodo'):
    tokenfile = '../.zenodo'
elif os.path.isfile('.zenodo'):
    tokenfile = '.zenodo'

with open(tokenfile) as f:
    token = f.readline().strip()


@pytest.fixture(params=[token, None])
def zeno(request):

    zeno = Zenodo(token=request.param, sandbox=True)

    def fin():
        print('teardown zeno')
        zeno._token = None
    request.addfinalizer(fin)

    return zeno


class TestZenodo(object):

    def test_connection_token(self, zeno):
        if zeno._token is not None:
            zeno.connection()
            assert zeno.status_code == 200
        else:
            with pytest.raises(ZenodoException):
                zeno.connection()

    def test_get_deposition_id_and_delete(self, zeno):

        if zeno._token is not None:
            z = zeno.get_deposition_id()
            assert type(zeno.deposition_id) is int

            # Remove the record create for the test
            zeno.delete()
        else:
            with pytest.raises(ZenodoException):
                zeno.get_deposition_id()

    def test_upload_file(self, zeno):

        if zeno._token is not None:
            zeno.get_deposition_id()
            zeno.upload_file('test.csv')
            if zeno.status_code >= 500:
                print('Test was not able to work because of '
                      'error {} on the server'.format(zeno.status_code))
            else:
                assert type(zeno.status_code) is int

            # Remove the record create for the test
            zeno.delete()
        else:
            with pytest.raises(ZenodoException):
                zeno.upload_file('test.csv')


    # def test_publish(self):
    #     # Need to understand how to do a mock to be able to test it.
    #     raise "Not implemented"

    # def test_download_file():
    #     raise "Not implemented"
    #
    #
    # def test_metadata_verify():
    #     raise "Not implemented"

