import os
import pytest

from conftest import DatalightException, get_files_path, zip_data

# Path where the tests are
test_directory = os.path.dirname(os.path.realpath(__file__))

common_dir = os.path.join(test_directory, 'common')
test_file_1 = 'test_1.dat'
test_file_2 = 'test_2.dat'
test_file_3 = 'subdirectory/test_3.dat'
file_path_1 = os.path.abspath(os.path.join(common_dir, test_file_1))
file_path_2 = os.path.abspath(os.path.join(common_dir, test_file_2))
file_path_3 = os.path.abspath(os.path.join(common_dir, test_file_3))


def test_get_files_path_file():
    # Test getting the path of a single file.
    assert [file_path_1] == get_files_path(file_path_1)


def test_get_files_path_directory():
    # Test getting the paths of all files in a directory
    assert sorted([file_path_1, file_path_2, file_path_3]) == get_files_path(common_dir)


def test_get_files_path_exception():
    with pytest.raises(DatalightException):
        get_files_path('doesnotexist')


def test_zipdata_nofile_or_file_does_not_exist():
    with pytest.raises(DatalightException):
        zip_data('')


def test_zipdata_with_existing_file():
    zip_data(file_path_1)
    assert os.path.isfile('data.zip')
    os.remove('data.zip')


def test_zipdata_wrong_input():
    with pytest.raises(DatalightException):
        zip_data(1233)


def test_zipdata_directory_as_input():
    zip_data(common_dir)
    assert os.path.isfile('data.zip')
    os.remove('data.zip')


def test_zipdata_save_zip_another_name():
    zip_data(common_dir, os.path.join(test_directory, 'toto.zip'))
    assert os.path.isfile(os.path.join(test_directory, 'toto.zip'))
    os.remove(os.path.join(test_directory, 'toto.zip'))
