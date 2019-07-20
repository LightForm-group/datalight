"""Functions to get YAML data files and read them."""

import pathlib

import requests
import yaml


def read_basic_ui(ui_path):
    """Read the UI specification from a YAML file."""
    ui_path = pathlib.Path(ui_path)
    ui_file = pathlib.Path("minimum_ui.yaml")

    with open(ui_path / ui_file, encoding='utf8') as input_file:
        ui_specification = yaml.load(input_file, Loader=yaml.FullLoader)
    return ui_specification


def get_experimental_metadata(url: str) -> dict:
    """Get the experimental metadata file from a URL."""
    response = requests.get(url)
    if not response.ok:
        response.raise_for_status()
    response.encoding = 'utf-8'

    experiment_metadata = yaml.load(response.text, Loader=yaml.FullLoader)
    return experiment_metadata


def read_author_list(ui_path: str) -> dict:
    """Read Author names, affiliations and ORCIDs from a yaml file."""
    ui_path = pathlib.Path(ui_path)
    author_file = pathlib.Path("author_details.yaml")
    author_path = ui_path / author_file

    with open(author_path, 'r') as input_file:
        authors = yaml.load(input_file, Loader=yaml.FullLoader)
    return authors
