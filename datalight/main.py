"""Main module for datalight."""

import sys

from PyQt5 import QtWidgets

from datalight.ui.form_generator import DatalightUIWindow, connect_button_methods


def main(ui_path):
    """The main function."""
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

