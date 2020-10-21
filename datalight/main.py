"""Main module for datalight."""
import pathlib
import sys
from typing import List, Union

from PyQt5 import QtWidgets

from datalight.ui.main_form import DatalightUIWindow, connect_button_methods
from datalight import zenodo


def upload_record(file_paths: List[str], repository_metadata: Union[dict, str],
                  config_path: Union[pathlib.Path, str],
                  experimental_metadata: Union[dict, None] = None, publish: bool = False,
                  sandbox: bool = True, repository: str = "Zenodo"):

    if repository == "Zenodo":
        zenodo.upload_record(file_paths, repository_metadata, config_path, experimental_metadata,
                             publish, sandbox)
    else:
        raise TypeError(f"Unknown repository type: '{repository}'.")


def open_gui(root_path: str):
    """The main function. This opens the DataLight GUI.
    :param root_path: The path to the root of the RoboTA project
    metadata descriptions.
    """
    app = QtWidgets.QApplication(sys.argv)
    datalight_ui = DatalightUIWindow(root_path)
    datalight_ui.ui_setup()
    datalight_ui.main_window.show()
    datalight_ui.set_window_position()
    connect_button_methods(datalight_ui)
    sys.exit(app.exec_())


if __name__ == "__main__":
    ROOT_PATH = sys.argv[1]
    open_gui(ROOT_PATH)
