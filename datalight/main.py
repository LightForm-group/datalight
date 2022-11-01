"""Main module for datalight."""
import pathlib
import sys
from typing import List, Union

from PyQt5 import QtWidgets

from datalight.ui.main_form import DatalightUIWindow, connect_button_methods
from datalight import zenodo, common


def upload_record(file_paths: List[str], repository_metadata: Union[dict, str],
                  config_path: Union[pathlib.Path, str],
                  experimental_metadata: Union[dict, None] = None, publish: bool = False,
                  sandbox: bool = True, repository: str = "Zenodo", 
                  deposition_ID: int = None):
    """Upload a new record to a data repository."""
    if repository == "Zenodo":
        zenodo.upload_record(file_paths, repository_metadata, config_path, experimental_metadata,
                             publish, sandbox, deposition_ID)
    else:
        raise TypeError(f"Unknown repository type: '{repository}'.")


def get_status(config_path: Union[pathlib.Path, str],
               repository: str = "Zenodo", **kwargs) -> bool:
    r"""Check whether the selected data repository is set up correctly to do an upload.
    Return True if it is and False if not.
    :param config_path: The path to the Datalight config file containing API keys.
    :param repository: The data repository that will be used.
    :param kwargs:
        See below

    :Keyword Arguments:
        * *sandbox* (``bool``) --
          If Zenodo is selected as the repository. Whether to use the Zenodo sandbox or live
          Zenodo.
    """
    if repository == "Zenodo":
        if "sandbox" in kwargs:
            sandbox = kwargs["sandbox"]
        else:
            sandbox = True
        credentials_location = pathlib.Path(config_path).resolve()
        token = common.get_authentication_token(credentials_location, sandbox)
        deposition_url = zenodo.get_deposition_url(sandbox)
        status = zenodo.try_connection(deposition_url, token)
        if status.code in zenodo.STATUS_SUCCESS:
            return True
        else:
            return False
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
