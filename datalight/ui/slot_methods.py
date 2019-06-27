"""
This script contains functions which are linked to buttons in the UI.
In order to be linked to a button, a function must have the same name as the button as specified
in the UI YAML specification.
"""
import pathlib
import re

import yaml
from PyQt5 import QtWidgets, QtCore

from datalight.common import logger
from datalight.ui import custom_widgets
from datalight.ui.custom_widgets import GroupBox, get_new_widget
from datalight.zenodo import upload_record


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
                                                  re.split(r"[\\/]", path)[-1]))


def ok_button(datalight_ui):
    """
    The on click method for the OK button. Take all data from the form and package
    it up into a dictionary.
    """
    metadata_output = {}
    valid_output = {}
    valid_length = {}
    widgets = datalight_ui.central_widget.findChildren(QtWidgets.QWidget)
    for widget in widgets:
        widget_name = widget.objectName()
        try:
            metadata_output[widget_name] = widget.get_value()
            valid_output[widget_name] = widget.check_optional()
        except AttributeError:
            # If the widget does not have a get_value method then ignore the widget.
            # If the widget does not have a check_optional method then do not add it to the valid
            # output list.
            pass
        try:
            valid_length[widget_name] = widget.check_length()
        except AttributeError:
            # If the widget does not have a check_length method
            pass

    incomplete_widgets = [key for key, value in list(valid_output.items()) if not value]
    short_widgets = [key for key, value in list(valid_length.items()) if not value]

    logger.warning("Has invalid output: {}".format(incomplete_widgets))
    logger.warning("Has invalid length: {}".format(short_widgets))

    if False in list(valid_output.values()):
        warning_text = "Some mandatory fields have not been completed: \n"
        for item in incomplete_widgets:
            warning_text += "• {}\n".format(item)
        custom_widgets.message_box(warning_text, QtWidgets.QMessageBox.Warning)
    elif False in list(valid_length.values()):
        warning_text = "Some fields have a minimum length that has not been met: \n"
        for item in short_widgets:
            warning_text += "• {}\n".format(item)
        custom_widgets.message_box(warning_text, QtWidgets.QMessageBox.Warning)
    else:
        print(metadata_output)
        upload_record(metadata_output["file_list"], metadata_output)
        logger.info("Datalight upload successful.")
        custom_widgets.message_box("Datalight upload successful.",
                                   QtWidgets.QMessageBox.Information)


def update_author_details(name, affiliation, orcid, author_path):
    with open(author_path, 'r') as input_file:
        author_list = yaml.load(input_file, Loader=yaml.FullLoader)
    if name in author_list:
        affiliation.setText(author_list[name]["affiliation"])
        orcid.setText(str(author_list[name]["orcid"]))


def update_experimental_metadata(experimental_group_box: GroupBox, new_value, ui_descriptions):
    # Get all children remove them from the layout and close them
    children = experimental_group_box.children()
    for child in reversed(children):
        if not isinstance(child, QtWidgets.QLayout):
            experimental_group_box.remove_widget_from_layout(child)
            child.close()

    if new_value != "none":
        new_widget = get_new_widget(experimental_group_box, ui_descriptions[new_value])
        experimental_group_box.add_widget(*new_widget)
