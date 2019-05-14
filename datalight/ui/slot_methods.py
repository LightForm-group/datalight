"""
This script contains functions which are linked to buttons in the UI.
In order to be linked to a button, a function must have the same name as the button as specified
in the UI YAML specification.
"""
import re

import yaml
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot


def remove_item_button(datalight_ui):
    """Remove the selected item(s) from the file/folder upload list."""
    list_widget = datalight_ui.get_widget_by_name("file_list")
    files = list_widget.selectedItems()
    for item in files:
        row_index = list_widget.row(item)
        list_widget.takeItem(row_index)


def select_file_button(datalight_ui):
    """Open a dialog box to select a file to upload."""
    file_dialogue = QtWidgets.QFileDialog()
    file_dialogue.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
    open_file_window(datalight_ui, file_dialogue)


def select_folder_button(datalight_ui):
    """Open a dialog box to select a folder` to upload."""
    file_dialogue = QtWidgets.QFileDialog()
    file_dialogue.setFileMode(QtWidgets.QFileDialog.Directory)
    open_file_window(datalight_ui, file_dialogue)


def open_file_window(datalight_ui, file_dialogue):
    list_widget = datalight_ui.get_widget_by_name("file_list")
    if file_dialogue.exec():
        for path in file_dialogue.selectedFiles():
            if not list_widget.findItems(path, QtCore.Qt.MatchExactly):
                list_widget.addItem(path)
            else:
                QtWidgets.QMessageBox.warning(datalight_ui.central_widget, "Warning",
                                              "File {}, already selected.".format(
                                                  re.split("[\\\/]", path)[-1]))


def ok_button(datalight_ui):
    """
    The on click method for the OK button. Take all data from the form and package
    it up into a dictionary.
    """
    output = {}
    widgets = datalight_ui.central_widget.findChildren(QtWidgets.QWidget)
    for widget in widgets:
        name = widget.objectName()
        try:
            output[name] = widget.get_value()
        except AttributeError:
            pass
    print(output)


def update_author_details(name, affiliation, orcid):
    with open("author_details.yaml", 'r') as input_file:
        author_list = yaml.load(input_file, Loader=yaml.FullLoader)
    if name in author_list:
        affiliation.setText(author_list[name]["affiliation"])
        orcid.setText(author_list[name]["orcid"])
