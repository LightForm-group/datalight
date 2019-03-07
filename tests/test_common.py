import os
import pytest
import pathlib

from datalight.common import get_files_path, zip_data

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
    # Test getting the path of a single file.
    assert [file_path_1] == get_files_path(file_path_1)


def test_get_files_path_directory():
    # Test getting the paths of all files in a directory
    assert sorted([file_path_1, file_path_2, file_path_3]) == get_files_path(common_dir)


def test_get_files_path_exception():
    with pytest.raises(FileNotFoundError):
        get_files_path('doesnotexist')


def test_zip_data_nofile_or_file_does_not_exist():
    with pytest.raises(FileNotFoundError):
        zip_data([''], zip_name)


def test_zip_data_with_existing_file():
    zip_data([file_path_1], zip_name)
    assert zip_name.is_file()
    os.remove(zip_name)


def test_zip_data_wrong_input():
    with pytest.raises(TypeError):
        zip_data(1233, zip_name)


def test_zip_data_directory_as_input():
    zip_data([common_dir], zip_name)
    assert zip_name.is_file()
    os.remove(zip_name)


def test_zip_data_save_zip_another_name():
    zip_name = pathlib.Path('toto.zip')
    zip_data([common_dir], test_directory / zip_name)
    assert (test_directory / zip_name).is_file()
    os.remove(test_directory / zip_name)
