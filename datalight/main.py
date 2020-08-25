"""Main module for datalight."""

import sys

from PyQt5 import QtWidgets

from datalight.ui.main_form import DatalightUIWindow, connect_button_methods


def main(credentials_path: str, ui_path: str):
    """The main function.
    :param credentials_path: The path to the config file with API tokens
    :param ui_path: The full path to the datalight/ui folder that contains minimum_ui.yaml.
    metadata descriptions.
    """
    app = QtWidgets.QApplication(sys.argv)
    datalight_ui = DatalightUIWindow(ui_path, credentials_path)
    datalight_ui.ui_setup()
    datalight_ui.main_window.show()
    datalight_ui.set_window_position()
    connect_button_methods(datalight_ui)
    sys.exit(app.exec_())


if __name__ == "__main__":
    CRED_PATH = sys.argv[1]
    UI_PATH = sys.argv[2]
    main(CRED_PATH, UI_PATH)
