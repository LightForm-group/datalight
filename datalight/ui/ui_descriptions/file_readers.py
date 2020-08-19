"""Functions to get YAML data files and read them."""

import pathlib

import yaml


def read_ui(ui_path: str, repository_name: str = "zenodo") -> dict:
    """Read the UI specification from a YAML file."""
    ui_path = pathlib.Path(ui_path)
    ui_file = pathlib.Path(f"{repository_name}.yaml")
    metadata_file = pathlib.Path("metdata.yaml")

    with open(ui_path / ui_file, encoding='utf8') as input_file:
        ui_specification = yaml.load(input_file, Loader=yaml.FullLoader)
    with open(ui_path / metadata_file, encoding='utf8') as input_file:
        metadata_spec = yaml.load(input_file, Loader=yaml.FullLoader)

    return {**ui_specification, **metadata_spec}


def read_author_list(ui_path: str) -> dict:
    """Read Author names, affiliations and ORCIDs from a yaml file."""
    ui_path = pathlib.Path(ui_path)
    author_file = pathlib.Path("author_details.yaml")
    author_path = ui_path / author_file

    with open(author_path, 'r') as input_file:
        authors = yaml.load(input_file, Loader=yaml.FullLoader)
    return authors
