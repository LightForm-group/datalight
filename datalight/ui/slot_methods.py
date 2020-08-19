"""
This script contains functions which are linked to buttons in the UI.
In order to be linked to a button, a function must have the same name as the button as specified
in the UI YAML specification.
"""
import re
from typing import TYPE_CHECKING

from PyQt5 import QtWidgets, QtCore

from datalight.common import logger
from datalight.ui import custom_widgets
from datalight.ui.custom_widgets import GroupBox, get_new_widget
import datalight.ui.validation
from datalight.zenodo import upload_record

if TYPE_CHECKING:
    from datalight.ui.main_form import DatalightUIWindow


def remove_item_button(datalight_ui):
    """Remove the selected item(s) from the file/folder upload list."""
    list_widget = datalight_ui.get_widget_by_name("file_list")
    files = list_widget.selectedItems()
    for item in files:
        row_index = list_widget.row(item)
        list_widget.takeItem(row_index)


def select_file_button(datalight_ui):
    """Prepare to open a dialog box to select a file to upload."""
    file_dialogue = QtWidgets.QFileDialog()
    file_dialogue.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
    open_file_window(datalight_ui, file_dialogue)


def select_folder_button(datalight_ui):
    """Prepare to open a dialog box to select a folder` to upload."""
    file_dialogue = QtWidgets.QFileDialog()
    file_dialogue.setFileMode(QtWidgets.QFileDialog.Directory)
    open_file_window(datalight_ui, file_dialogue)


def open_file_window(datalight_ui, file_dialogue):
    """Open a dialogue box to select a file or folder."""
    list_widget = datalight_ui.get_widget_by_name("file_list")
    if file_dialogue.exec():
        for path in file_dialogue.selectedFiles():
            if not list_widget.findItems(path, QtCore.Qt.MatchExactly):
                list_widget.addItem(path)
            else:
                file_name = re.split(r"[\\/]", path)[-1]
                QtWidgets.QMessageBox.warning(datalight_ui.central_widget, "Warning",
                                              f"File {file_name}, already selected.")


def ok_button(datalight_ui: "DatalightUIWindow"):
    """
    The on click method for the OK button. Take all data from the form and package
    it up into a dictionary.
    """
    repository_widget = datalight_ui.get_widget_by_name("zenodo_core_metadata")
    incomplete_widgets, short_widgets = validate_widgets(repository_widget)

    if incomplete_widgets:
        datalight.ui.validation.process_incomplete_widgets(incomplete_widgets)
    elif short_widgets:
        datalight.ui.validation.process_short_widgets(short_widgets)
    else:
        repository_metadata = datalight.ui.validation.get_widget_values(repository_widget)
        experiment_widget = datalight_ui.get_widget_by_name("experimental_metadata")
        experiment_metadata = datalight.ui.validation.get_widget_values(experiment_widget)

        upload_record(repository_metadata.pop("file_list"), repository_metadata,
                      publish=repository_metadata.pop("publish"),
                      sandbox=repository_metadata.pop("sandbox"))
        logger.info("Datalight upload successful.")
        custom_widgets.message_box("Datalight upload successful.",
                                   QtWidgets.QMessageBox.Information)


def validate_widgets(widget: QtWidgets.QWidget):
    child_widgets = widget.findChildren(QtWidgets.QWidget)

    valid_length = datalight.ui.validation.validate_output_length(child_widgets)
    valid_output = datalight.ui.validation.validate_widget_contents(child_widgets)

    # Validation of widget contents
    incomplete_widgets = [key for key, value in list(valid_output.items()) if not value]
    short_widgets = [key for key, value in list(valid_length.items()) if not value]

    return incomplete_widgets, short_widgets


def update_author_details(name: str, affiliation: QtWidgets.QComboBox, orcid: QtWidgets.QComboBox,
                          author_list: dict):
    """A function attached to the currentIndexChanged method of author_list_box.
    Checks if the passed name is in the stored author list and if so, sets the relevant
    affiliation and ORCID."""
    if name in author_list:
        affiliation.setText(author_list[name]["affiliation"])
        orcid.setText(str(author_list[name]["orcid"]))


def update_experimental_metadata(experimental_group_box: GroupBox, new_value: str,
                                 ui_descriptions: dict):
    """Clear the experimental group box and refill it with new widgets."""

    # Get all children remove them from the layout and close them
    children = experimental_group_box.children()
    for child in reversed(children):
        if not isinstance(child, QtWidgets.QLayout):
            experimental_group_box.remove_widget_from_layout(child)
            child.close()

    if new_value != "none":
        new_widget = get_new_widget(experimental_group_box, ui_descriptions[new_value])
        experimental_group_box.add_widget(*new_widget)
