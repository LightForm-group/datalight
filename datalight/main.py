"""Main module for datalight."""

import sys

from PyQt5 import QtWidgets

from datalight.ui.main_form import DatalightUIWindow, connect_button_methods


def main(ui_path):
    """The main function.
    :param ui_path: The full path to the datalight/ui folder that contains minimum_ui.yaml.
    metadata descriptions.
    """
    app = QtWidgets.QApplication(sys.argv)
    datalight_ui = DatalightUIWindow(ui_path)
    datalight_ui.ui_setup()
    datalight_ui.main_window.show()
    datalight_ui.set_window_position()
    connect_button_methods(datalight_ui)
    sys.exit(app.exec_())


if __name__ == "__main__":
    UI_PATH = sys.argv[1]
    main(UI_PATH)
