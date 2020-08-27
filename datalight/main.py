"""Main module for datalight."""

import sys

from PyQt5 import QtWidgets

from datalight.ui.main_form import DatalightUIWindow, connect_button_methods


def main(root_path: str):
    """The main function.
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
    main(ROOT_PATH)
