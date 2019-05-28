"""Tests for the functions in common.py"""
import os
import pathlib
import pytest

from datalight.common import get_files_from_directory, zip_data

# Path where the tests are
test_directory = pathlib.Path(__file__).parent

common_dir = test_directory / pathlib.Path('common')
test_file_1 = pathlib.Path('test_1.dat')
test_file_2 = pathlib.Path('test_2.dat')
test_file_3 = pathlib.Path('subdirectory/test_3.dat')
file_path_1 = (common_dir / test_file_1).resolve()
file_path_2 = (common_dir / test_file_2).resolve()
file_path_3 = (common_dir / test_file_3).resolve()
zip_name = pathlib.Path("data.zip")


def test_get_files_path_file():
    """Get the path of a single file."""
    assert [file_path_1] == get_files_from_directory(file_path_1)


def test_get_files_path_directory():
    """ Get the paths of all files in a directory"""
    assert sorted([file_path_1, file_path_2, file_path_3]) == get_files_from_directory(common_dir)


def test_get_files_path_exception():
    """Getting a non-existant file should raise an exception."""
    with pytest.raises(FileNotFoundError):
        get_files_from_directory('doesnotexist')


def test_zip_data_nofile_or_file_does_not_exist():
    """Zipping a non existent file should raies an exception."""
    with pytest.raises(FileNotFoundError):
        zip_data([''], zip_name)


def test_zip_data_with_existing_file():
    """Zipping a valid file"""
    zip_data([file_path_1], zip_name)
    assert zip_name.is_file()
    os.remove(zip_name)


def test_zip_data_wrong_input():
    """Zip should take a list of strings as input."""
    with pytest.raises(TypeError):
        zip_data(1233, zip_name)


def test_zip_data_directory_as_input():
    """Zip can also accept a directory name."""
    zip_data([common_dir], zip_name)
    assert zip_name.is_file()
    os.remove(zip_name)


def test_zip_data_save_zip_another_name():
    """We can change the name of the zip file which is output."""
    zip_name = pathlib.Path('toto.zip')
    zip_data([common_dir], test_directory / zip_name)
    assert (test_directory / zip_name).is_file()
    os.remove(test_directory / zip_name)
