"""
This script contains functions which are linked to buttons in the UI.
In order to be linked to a button, a function must have the same name as the button as specified
in the UI YAML specification.
"""
import pathlib
import re

import yaml
from PyQt5 import QtWidgets, QtCore

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
                                                  re.split("[\\\/]", path)[-1]))


def ok_button(datalight_ui):
    """
    The on click method for the OK button. Take all data from the form and package
    it up into a dictionary.
    """
    metadata_output = {}
    valid_output = {}
    widgets = datalight_ui.central_widget.findChildren(QtWidgets.QWidget)
    for widget in widgets:
        widget_name = widget.objectName()
        try:
            metadata_output[widget_name] = widget.get_value()
            valid_output[widget_name] = widget.is_valid()
        except AttributeError:
            pass

    print(valid_output)

    if False in list(valid_output.values()):
        warning_text = "Some mandatory fields have not been completed: \n"
        for item in valid_output:
            if valid_output[item] is False:
                warning_text += "• {}\n".format(item)
        warning_box = QtWidgets.QMessageBox()
        warning_box.setIcon(QtWidgets.QMessageBox.Warning)
        warning_box.setText(warning_text)
        warning_box.setWindowTitle("Datalight warning")
        warning_box.exec()
    else:
        print(metadata_output)
        upload_record(metadata_output["file_list"][0], metadata_output)


def update_author_details(name, affiliation, orcid, author_path):
    with open(author_path, 'r') as input_file:
        author_list = yaml.load(input_file, Loader=yaml.FullLoader)
    if name in author_list:
        affiliation.setText(author_list[name]["affiliation"])
        orcid.setText(author_list[name]["orcid"])


def update_experimental_metadata(experimental_group_box: GroupBox, new_value, ui_folder):
    # Get all children remove them from the layout and close them
    children = experimental_group_box.children()
    for child in reversed(children):
        if not isinstance(child, QtWidgets.QLayout):
            experimental_group_box._layout.removeWidget(child)
            child.close()

    new_widgets = read_ui_file(ui_folder, new_value)
    for widget in new_widgets:
        # Create a new widget and add it
        new_widget = get_new_widget(experimental_group_box, new_widgets[widget])
        experimental_group_box.add_widget(*new_widget)


def read_ui_file(ui_path, ui_name):
        """Read the UI specification from a YAML file."""
        ui_path = pathlib.Path(ui_path)
        ui_file = pathlib.Path("{}.yaml".format(ui_name))
        if not (ui_path / ui_file).exists():
            raise FileNotFoundError("Cannot find experimental metadata file: {}".format(
                ui_path / ui_file))

        with open(ui_path / ui_file, encoding='utf8') as input_file:
            return yaml.load(input_file, Loader=yaml.FullLoader)
