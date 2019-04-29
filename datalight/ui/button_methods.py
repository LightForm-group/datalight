"""
This script contains functions which are linked to buttons in the UI.
In order to be linked to a button, a function must have the same name as the button as specified
in the UI YAML specification.
"""
from PyQt5 import QtWidgets


def clear_button(datalight_ui):
    print("clear button")


def select_file(datalight_ui):
    print("file select button")


def select_folder(datalight_ui):
    print("folder select button")


def ok_button(datalight_ui):
    """
    The on click method for the OK button. Take all data from the form and package
    it up into a dictionary.
    """
    output = {}
    widgets = datalight_ui.central_widget.findChildren(QtWidgets.QWidget)
    for widget in widgets:
        name = widget.objectName()
        if isinstance(widget, QtWidgets.QComboBox):
            output[name] = widget.currentText()
        elif isinstance(widget, QtWidgets.QPlainTextEdit):
            output[name] = widget.toPlainText()
        elif isinstance(widget, QtWidgets.QDateEdit):
            output[name] = widget.date()
        else:
            pass
    print(output)
